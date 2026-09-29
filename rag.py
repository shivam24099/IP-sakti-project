"""
rag.py
------
Standard LangChain RAG pipeline with knowledge-domain filtering and grounded generation.

Components used:
- HuggingFaceEmbeddings (all-MiniLM-L6-v2)
- Chroma (Vector Store with metadata filtering)
- LangChain Retriever (as_retriever with search_kwargs)
- Local Ollama LLM (with graceful extractive fallback if Ollama is not active)
"""

import json
import os
import urllib.request
from typing import Dict, List, Tuple

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# Base directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")
COLLECTION_NAME = "ip_sakti_store"

# Ollama LLM Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"  # or mistral, llama3, qwen2.5

# Singleton vectorstore cache to avoid reloading embeddings model on every query
_CACHED_VECTORSTORE = None


# ==============================================================================
# 1. VECTORSTORE INITIALIZATION
# ==============================================================================
def get_collection_count(persist_directory: str = CHROMA_DIR) -> int:
    """
    Fast chunk count check without loading heavy embedding models into memory.
    """
    try:
        import chromadb
        client = chromadb.PersistentClient(path=persist_directory)
        coll = client.get_collection(COLLECTION_NAME)
        return coll.count()
    except Exception:
        return 0


def get_vectorstore(persist_directory: str = CHROMA_DIR) -> Chroma:
    """
    Initializes or returns the cached LangChain Chroma vectorstore.
    """
    global _CACHED_VECTORSTORE
    if _CACHED_VECTORSTORE is not None:
        return _CACHED_VECTORSTORE

    if not os.path.exists(persist_directory):
        return None

    # Load local sentence-transformer embeddings
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    _CACHED_VECTORSTORE = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME,
    )
    return _CACHED_VECTORSTORE


# ==============================================================================
# 2. DOMAIN-ROUTED RETRIEVAL (The Core Innovation)
# ==============================================================================
def retrieve_from_domains(
    query: str,
    selected_domains: List[str],
    k: int = 4,
    persist_directory: str = CHROMA_DIR,
) -> List[Document]:
    """
    Retrieves documents from ChromaDB strictly filtered to the routed domains.

    How this works in LangChain:
    - If 1 domain is selected: filter={'domain': 'patent'}
    - If multiple domains selected: filter={'domain': {'$in': ['patent', 'ayurveda_tk']}}
    - Documents outside the routed domains are NEVER searched or returned.
    """
    vectorstore = get_vectorstore(persist_directory)
    if vectorstore is None:
        return []

    if not selected_domains:
        return []

    # Build the Chroma metadata filter
    if len(selected_domains) == 1:
        domain_filter = {"domain": selected_domains[0]}
    else:
        domain_filter = {"domain": {"$in": selected_domains}}

    # Adjust retrieval depth based on number of routed domains
    retrieval_k = max(k, len(selected_domains) * 2)

    # Standard LangChain Retriever
    retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": retrieval_k,
            "filter": domain_filter,
        }
    )

    retrieved_docs = retriever.invoke(query)
    return retrieved_docs


# ==============================================================================
# 3. CONTEXT & SOURCE CITATION BUILDER
# ==============================================================================
def build_context_and_citations(docs: List[Document]) -> Tuple[str, List[Dict]]:
    """
    Transforms retrieved LangChain documents into:
    1. A numbered context block for the LLM prompt.
    2. A structured citation list extracted directly from document metadata.
    """
    context_lines = []
    citations = []

    for i, doc in enumerate(docs, start=1):
        meta = doc.metadata
        doc_name = meta.get("document_name", "Document")
        page_num = meta.get("page", 1)
        domain = meta.get("domain", "General")
        text = doc.page_content.strip()

        context_lines.append(f"[{i}] (Source: {doc_name}, Page: {page_num}, Domain: {domain})\n{text}")

        citations.append({
            "citation_id": i,
            "document_name": doc_name,
            "page": page_num,
            "domain": domain,
            "snippet": text,
        })

    return "\n\n".join(context_lines), citations


# ==============================================================================
# 4. GROUNDED PROMPT TEMPLATE
# ==============================================================================
GROUNDED_PROMPT = """You are IP-SAKTI Sahayak, an AI legal & regulatory assistant for Ayurveda Intellectual Property, AYUSH, and FSSAI compliance.

Your task is to provide clear, actionable guidance to the user's question using ONLY the numbered evidence provided below.

Strict Guidelines:
1. Base your answer strictly on the provided evidence. Do NOT invent legal statutes or guidelines.
2. Cite the evidence inline using bracketed numbers like [1], [2] whenever you state a rule or fact.
3. If the evidence does not contain sufficient details to answer, state clearly what is known and what requires further consultation.
4. Structure your response into clear bullet points or short paragraphs for readability.

Evidence:
{context}

User Question: {question}

Grounded Answer (with inline citations [1], [2]):"""


# ==============================================================================
# 5. LLM INVOCATION WITH RESILIENT FALLBACK
# ==============================================================================
def check_ollama_status() -> bool:
    """
    Fast, non-blocking check whether local Ollama server is reachable.
    """
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=1) as response:
            return response.status == 200
    except Exception:
        return False


def call_ollama(prompt: str) -> str:
    """
    Attempts to call local Ollama instance via HTTP API.
    Returns generated response string, or None if Ollama is unavailable.
    """
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.2},
    }).encode("utf-8")

    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result.get("response", "").strip()
    except Exception:
        # Graceful fallback: Ollama not running or model not pulled
        return None


def generate_extractive_answer(docs: List[Document]) -> str:
    """
    Deterministic synthesis used when Ollama is offline.
    Presents the grounded evidence directly with verified source numbers.
    This guarantees the prototype never fails during a live demonstration!
    """
    if not docs:
        return "No relevant regulatory documents found for the selected domains."

    lines = [
        "*(Note: Ollama LLM is currently offline. Displaying synthesized evidence retrieved directly from the routed knowledge domains:)*",
        "",
    ]
    for i, doc in enumerate(docs, start=1):
        meta = doc.metadata
        domain_tag = meta.get("domain", "").upper()
        doc_name = meta.get("document_name", "Document")
        page = meta.get("page", 1)
        lines.append(f"**[{i}] Regulatory Excerpt — {domain_tag} ({doc_name}, Page {page}):**")
        lines.append(f"> {doc.page_content.strip()}")
        lines.append("")

    return "\n".join(lines)


def generate_answer(query: str, docs: List[Document]) -> Tuple[str, List[Dict]]:
    """
    Full generation step:
    1. Formats context block and extracts source citations.
    2. Calls LLM if available; otherwise uses extractive synthesis.
    3. Returns (answer_text, citations_list).
    """
    if not docs:
        return (
            "No relevant documents were found in the selected knowledge domains. Please verify that your knowledge base is ingested.",
            [],
        )

    context_str, citations = build_context_and_citations(docs)
    prompt = GROUNDED_PROMPT.format(context=context_str, question=query)

    llm_response = call_ollama(prompt)
    if llm_response:
        answer = llm_response
    else:
        answer = generate_extractive_answer(docs)

    return answer, citations


# ==============================================================================
# Quick Standalone Test
# ==============================================================================
if __name__ == "__main__":
    from router import route_query

    test_q = "Can I patent an Ayurvedic formulation made with neem?"
    print(f"\nTesting Query: '{test_q}'")
    routed_domains, reasons, _ = route_query(test_q)
    print(f"Routed Domains: {routed_domains}")

    docs = retrieve_from_domains(test_q, routed_domains, k=3)
    print(f"Retrieved {len(docs)} documents:")
    for d in docs:
        print(f"  - [{d.metadata['domain']}] {d.metadata['document_name']} (Page {d.metadata['page']})")

    ans, cits = generate_answer(test_q, docs)
    print("\n--- Answer Preview ---")
    print(ans[:300] + "...")
    print(f"\nExtracted Citations Count: {len(cits)}")
