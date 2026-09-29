"""
ingest.py
---------
Simple PDF ingestion pipeline using LangChain.

Loads PDFs, chunks them with RecursiveCharacterTextSplitter, attaches metadata
(source, document_name, domain, page number), and indexes them in a single ChromaDB collection.

To add new PDFs in the future, just add an entry to the PDF_LIST below!
"""

import os
import shutil
from typing import List, Tuple

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(BASE_DIR, "data", "pdfs")
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")
COLLECTION_NAME = "ip_sakti_store"


# ==============================================================================
# DEFAULT PDF REGISTRY (Add your own PDFs here!)
# Format: (relative_or_absolute_file_path, domain_tag)
# ==============================================================================
DEFAULT_PDFS: List[Tuple[str, str]] = [
    (os.path.join(PDF_DIR, "patent_guidelines.pdf"), "patent"),
    (os.path.join(PDF_DIR, "ayurveda_tk_compendium.pdf"), "ayurveda_tk"),
    (os.path.join(PDF_DIR, "ayush_manufacturing_rules.pdf"), "ayush"),
    (os.path.join(PDF_DIR, "fssai_nutraceutical_regulations.pdf"), "fssai"),
    (os.path.join(PDF_DIR, "nba_biodiversity_abs_guidelines.pdf"), "biodiversity_abs"),
]


# ==============================================================================
# MAIN INGESTION FUNCTION
# ==============================================================================
def ingest_pdfs(pdf_files: List[Tuple[str, str]], persist_directory: str = CHROMA_DIR) -> Chroma:
    """
    Ingests a list of (pdf_path, domain) into a single Chroma vector store.

    Parameters:
        pdf_files: List of tuples -> (path_to_pdf, domain_tag)
                   e.g. [("patent.pdf", "patent"), ("ayurveda.pdf", "ayurveda_tk")]
        persist_directory: Folder path where ChromaDB will persist its data.

    Returns:
        The initialized LangChain Chroma vectorstore instance.
    """
    all_chunks = []

    # 1. Standard LangChain Text Splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    print("\n" + "=" * 60)
    print("STARTING KNOWLEDGE INGESTION (LangChain + Chroma)")
    print("=" * 60)

    for pdf_path, domain in pdf_files:
        if not os.path.exists(pdf_path):
            print(f"[!] File not found: {pdf_path}. Skipping.")
            continue

        filename = os.path.basename(pdf_path)
        print(f"\n[+] Loading PDF: {filename} (Domain: '{domain}')")

        # 2. Standard LangChain PyPDFLoader
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()  # Loads each page as a LangChain Document

        # 3. Enrich page metadata before splitting
        for doc in pages:
            # PyPDFLoader provides 0-indexed 'page' in doc.metadata['page']
            raw_page = doc.metadata.get("page", 0)
            doc.metadata["page"] = int(raw_page) + 1  # Convert to 1-based page number
            doc.metadata["document_name"] = filename
            doc.metadata["domain"] = domain
            doc.metadata["source"] = filename

        # 4. Split pages into smaller, retrievable chunks
        chunks = text_splitter.split_documents(pages)
        print(f"    Loaded {len(pages)} page(s) -> created {len(chunks)} chunks.")
        all_chunks.extend(chunks)

    if not all_chunks:
        print("[!] No documents were loaded. Please check your PDF paths.")
        return None

    # 5. Initialize open-source embeddings (all-MiniLM-L6-v2)
    print(f"\n[+] Generating embeddings for {len(all_chunks)} chunks...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 6. Re-create clean persistent Chroma directory
    if os.path.exists(persist_directory):
        try:
            shutil.rmtree(persist_directory)
        except Exception:
            pass

    # 7. Store chunks into single LangChain Chroma vector store
    print(f"[+] Storing into ChromaDB collection '{COLLECTION_NAME}' at: {persist_directory}")
    vectorstore = Chroma.from_documents(
        documents=all_chunks,
        embedding=embeddings,
        persist_directory=persist_directory,
        collection_name=COLLECTION_NAME
    )

    print("\n[SUCCESS] Ingestion completed successfully!")
    print(f"Total chunks stored: {len(all_chunks)}")
    print("You can now run: streamlit run app.py\n")
    return vectorstore


if __name__ == "__main__":
    # If sample PDFs don't exist yet, generate them first
    if not os.path.exists(PDF_DIR) or not os.listdir(PDF_DIR):
        print("Sample PDFs not found. Generating them first...")
        from generate_sample_pdfs import generate_all_sample_pdfs
        generate_all_sample_pdfs()

    # Run the ingestion function
    ingest_pdfs(DEFAULT_PDFS)
