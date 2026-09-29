<<<<<<< HEAD
# IP sakti project
This is the IP sakti project repo made for creating a demo of my smart india hackathon problem statement as it is a demo there's going to be tons of changes and upgrades in the files
=======
# IP-SAKTI Sahayak (Smart India Hackathon Prototype)

> **AI Assistant for Ayurveda Intellectual Property, AYUSH & Food Regulatory Guidance**  
> *Demonstrating Pre-Retrieval Multi-Dimensional Knowledge Domain Routing*

---

## 1. Project Overview & Concept

In a generic RAG chatbot, a user query is sent against a single, unorganized vector database containing all documents. This frequently causes:
1. **Irrelevant retrieval** (e.g., retrieving trademark or food guidelines when asking a patent novelty question).
2. **Context dilution** (top-$k$ chunks wasted on irrelevant regulatory domains).
3. **Hallucinated or non-verifiable citations**.

**IP-SAKTI Sahayak** introduces **Pre-Retrieval Knowledge Routing**:
```
User Query
    ↓
1. Intent & Context Extraction (Product, Biological Resource, Objective)
    ↓
2. Knowledge-Domain Routing (Evaluates relevance across Patent, Ayurveda/TK, AYUSH, FSSAI, ABS)
    ↓
3. Domain-Filtered Retrieval (LangChain + Chroma filters chunks matching ONLY routed domains)
    ↓
4. Grounded Answer Generation (Local Ollama LLM cites evidence inline [1], [2])
    ↓
5. Verified Source Citations (Extracted directly from PDF metadata: Document, Page, Domain)
```

---

## 2. Project File Structure

```
ip-sakti-demo/
│
├── app.py                      # Streamlit UI showing 4-step visible routing pipeline
├── router.py                   # Rule-based intent analysis & multi-dimensional domain router
├── rag.py                      # LangChain Chroma retriever + grounded generation + citations
├── ingest.py                   # Simple PDF ingestion function (PyPDFLoader + RecursiveSplitter)
├── generate_sample_pdfs.py     # Generates 5 realistic 2-page domain PDFs using ReportLab
├── requirements.txt            # Minimal required dependencies
├── README.md                   # Complete documentation & SIH presentation guide
│
├── data/
│   └── pdfs/                   # Knowledge Base PDFs
│       ├── patent_guidelines.pdf                 (Domain: patent)
│       ├── ayurveda_tk_compendium.pdf            (Domain: ayurveda_tk)
│       ├── ayush_manufacturing_rules.pdf         (Domain: ayush)
│       ├── fssai_nutraceutical_regulations.pdf   (Domain: fssai)
│       └── nba_biodiversity_abs_guidelines.pdf   (Domain: biodiversity_abs)
│
└── chroma_db/                  # Single persistent ChromaDB vector store
```

---

## 3. Quickstart & Installation

### Step 1: Install Dependencies
Open your terminal inside the project directory and run:
```bash
pip install -r requirements.txt
```

### Step 2: (Optional) Start Ollama LLM
If you have [Ollama](https://ollama.ai) installed, pull and serve a local model:
```bash
ollama pull llama3.2
ollama serve
```
> **Note on Zero-Crash Fallback:** If Ollama is not installed or not running, the application **does not crash**. It automatically activates **Extractive Synthesis Mode**, presenting the exact retrieved regulatory excerpts with numbered citations.

### Step 3: Ingest the Knowledge Base PDFs
Run the ingestion script once:
```bash
python ingest.py
```
*(If the sample PDFs are missing, `ingest.py` will automatically generate them using `generate_sample_pdfs.py` before indexing!)*

### Step 4: Launch the Streamlit Demo
```bash
streamlit run app.py
```
The interface will open in your browser at `http://localhost:8501`.

---

## 4. How the Prototype Works (For SIH Judges & Presentation)

### A. The Routing Logic (`router.py`)
Instead of hiding routing inside an opaque black-box agent, `router.py` uses transparent, rule-based multi-dimensional logic:
1. **Keyword Analysis**: Checks for domain terms (e.g., `patent`, `novelty`, `ayush`, `license`, `fssai`, `nutraceutical`, `nba`, `abs`).
2. **Context & Herb Identification**: Extracts biological resources (e.g., *Neem*, *Turmeric*, *Ashwagandha*).
3. **Cross-Domain Rules (The Core SIH Innovation)**:
   - **Ayurvedic Herb + Patent Goal**: Under Section 3(p) of the Indian Patents Act, traditional knowledge cannot be patented as-is. The router routes to **Patent** + **Ayurveda / TK**.
   - **Indian Biological Resource + Patenting**: Under Section 6(1) of the Biological Diversity Act 2002, using Indian biological resources requires prior approval from the National Biodiversity Authority (NBA). The router activates **Biodiversity / ABS**.
   - **Ayurvedic Formulation + Food / Tea**: Requires compliance with FSSAI (Ayur-Aahar) as well as verifying boundaries with AYUSH medicine licensing. The router activates **FSSAI** + **Ayurveda / TK** + **AYUSH**.

### B. PDF Ingestion Function (`ingest.py`)
Adding new PDFs is straightforward. You only pass a list of tuples to `ingest_pdfs`:
```python
ingest_pdfs([
    ("data/pdfs/patent_guidelines.pdf", "patent"),
    ("data/pdfs/ayurveda_tk_compendium.pdf", "ayurveda_tk"),
    ("data/pdfs/fssai_nutraceutical_regulations.pdf", "fssai"),
    # Add any new PDF here:
    # ("data/pdfs/my_new_guideline.pdf", "ayush"),
])
```
- **`PyPDFLoader`** loads each page as a LangChain `Document`.
- Metadata is attached to each page: `doc.metadata["document_name"] = filename`, `doc.metadata["domain"] = domain`, `doc.metadata["page"] = page_number`.
- **`RecursiveCharacterTextSplitter`** chunks pages while preserving all metadata on every chunk.
- **`Chroma.from_documents`** embeds chunks using `all-MiniLM-L6-v2` and persists them into a single collection (`ip_sakti_store`).

### C. Chroma + LangChain Retrieval (`rag.py`)
To isolate retrieval strictly to the routed domains, LangChain's Chroma retriever uses a metadata filter:
```python
# If 1 domain is routed:
domain_filter = {"domain": "patent"}

# If multiple domains are routed:
domain_filter = {"domain": {"$in": ["patent", "ayurveda_tk", "biodiversity_abs"]}}

retriever = vectorstore.as_retriever(
    search_kwargs={"k": 4, "filter": domain_filter}
)
retrieved_docs = retriever.invoke(query)
```
Documents belonging to unselected domains (e.g. FSSAI or Copyright) are excluded from the vector search.

### D. Source Citations (Zero Hallucination)
The model is prompted to answer using only the numbered evidence (`[1]`, `[2]`).
The source citations shown in the UI are **not generated by the LLM**; they are mapped directly from `doc.metadata`:
- **Document Name**: `meta["document_name"]`
- **Page Number**: `meta["page"]`
- **Knowledge Domain**: `meta["domain"]`

---

## 5. Demonstration Queries for Presentation

| # | Query | Routed Domains | What It Demonstrates to Judges |
|---|---|---|---|
| **1** | *"Can I patent an Ayurvedic formulation made of neem and turmeric in India?"* | ✅ **Patent**<br>✅ **Ayurveda / TK**<br>✅ **Biodiversity / ABS** | **Multi-Domain Cross-Routing**: Automatically identifies Section 3(p) TK exclusion and Section 6 NBA approval requirement for biological resources. |
| **2** | *"What are the food safety and labeling requirements for an Ayurvedic herbal tea?"* | ✅ **FSSAI**<br>✅ **Ayurveda / TK**<br>✅ **AYUSH** | **Regulatory Boundary Routing**: Routes to FSSAI (Ayur-Aahar standards) and AYUSH to distinguish food supplements from licensed medicines. |
| **3** | *"How do I obtain an AYUSH manufacturing license and ensure Schedule T GMP compliance?"* | ✅ **AYUSH** | **Single Domain Routing**: Isolates retrieval to AYUSH drug licensing and Schedule T GMP rules; skips Patent and FSSAI. |
| **4** | *"What are the statutory patentability criteria for novelty and inventive step in India?"* | ✅ **Patent** | **Single Domain IP Routing**: Focuses strictly on Section 2(1)(j) patent criteria. |
| **5** | *"Do I need prior approval from the National Biodiversity Authority (NBA) before filing a patent?"* | ✅ **Patent**<br>✅ **Biodiversity / ABS** | **Dual Domain Statutory Routing**: Explains NBA Form III requirement for patent applicants. |

---

## 6. What is Real vs. Future Scope (Honest Scope Boundary)

| Feature | In Current Prototype (What to Claim) | In Proposed Future Architecture (Roadmap) |
|---|---|---|
| **Knowledge Domains** | 5 core domains implemented with verified PDFs (Patent, Ayurveda/TK, AYUSH, FSSAI, ABS). | 15 comprehensive domains including GI, Trademarks, Plant Varieties, etc. |
| **Routing Mechanism** | Deterministic, transparent Python rule-based router with context/entity extraction. | LLM + SQL/Vector semantic intent router with multi-agent orchestration. |
| **Database** | Single persistent ChromaDB collection with metadata filtering (`$in`). | Distributed multidimensional vector indices with hybrid BM25 + dense search. |
| **Pipeline Framework** | Standard LangChain (`PyPDFLoader`, `RecursiveSplitter`, `Chroma`, `Retriever`). | Stateful LangGraph workflow with corrective RAG (CRAG) & self-reflection. |
| **Language Support** | English queries and documents. | Multilingual support across 22 scheduled Indian languages via Bhashini. |

---

## 7. SIH Presentation Pitch Script (30 Seconds)

> *"Respected judges, current IP and regulatory workflows in Ayurveda are fragmented across multiple governing bodies: the Patent Office, the Ministry of AYUSH, FSSAI, and the National Biodiversity Authority. A generic RAG chatbot fails because it searches everything at once and hallucinates citations.*
>
> *Our system, **IP-SAKTI Sahayak**, introduces **Pre-Retrieval Multi-Dimensional Knowledge Routing**. Before touching the vector database, our router extracts biological entities and intent to identify the exact regulatory domains involved.*
>
> *For example, when an innovator asks to patent a neem formulation, our system automatically routes to Patent Law (Section 3p), Ayurveda TKDL, and the Biological Diversity Act (NBA Form III). Retrieval is strictly filtered to those domains, and every answer is backed by verifiable, page-level citations."*
>>>>>>> e1db202 (Initial commit)
