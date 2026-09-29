"""
app.py
------
Streamlit UI for IP-SAKTI Sahayak (Smart India Hackathon Prototype).

Demonstrates the core concept:
    User Query -> Intent/Context -> Knowledge-Domain Routing -> Domain-Filtered Retrieval -> Grounded LLM -> Source Citations

Run with:
    streamlit run app.py
"""

import os
import streamlit as st

from router import route_query, DOMAINS, UNIMPLEMENTED_DOMAINS
from rag import (
    retrieve_from_domains,
    generate_answer,
    get_vectorstore,
    get_collection_count,
    check_ollama_status,
    OLLAMA_MODEL,
    CHROMA_DIR,
)

# Page configuration
st.set_page_config(
    page_title="IP-SAKTI Sahayak | Ayurveda IP & Regulatory AI",
    page_icon="🌿",
    layout="wide",
)

# Custom CSS for styling cards and badges
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.3rem;
        font-weight: 700;
        color: #1b4332;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #495057;
        margin-bottom: 1.5rem;
    }
    .routed-card-selected {
        background-color: #e8f5e9;
        border-left: 5px solid #2e7d32;
        padding: 10px 14px;
        border-radius: 6px;
        margin-bottom: 8px;
    }
    .routed-card-skipped {
        background-color: #f8f9fa;
        border-left: 5px solid #ced4da;
        padding: 8px 14px;
        border-radius: 6px;
        margin-bottom: 8px;
        color: #6c757d;
    }
    .citation-box {
        background-color: #f1f8e9;
        border: 1px solid #c8e6c9;
        padding: 12px;
        border-radius: 6px;
        margin-top: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# SIDEBAR
# ==============================================================================
with st.sidebar:
    st.image(
        "https://img.icons8.com/color/96/ayurveda.png",
        width=64,
    )
    st.markdown("### IP-SAKTI Sahayak")
    st.caption("**Smart India Hackathon (SIH 2026)** Prototype")
    st.markdown(
        """
        **Innovation Highlight:**
        Instead of searching an unorganized single corpus, this prototype demonstrates
        **Multi-Dimensional Knowledge Routing**:
        1. Query analyzed for intent & biological context
        2. Routed to specific regulatory domains
        3. Retrieval strictly isolated to relevant PDF collections
        4. Grounded answer with verified page-level citations
        """
    )
    st.markdown("---")

    st.markdown("### 🧪 Test Scenarios")
    example_options = [
        "-- Select an example query --",
        "Can I patent an Ayurvedic formulation made of neem and turmeric in India?",
        "What are the food safety and labeling requirements for an Ayurvedic herbal tea?",
        "How do I obtain an AYUSH manufacturing license and ensure Schedule T GMP compliance?",
        "What are the statutory patentability criteria for novelty and inventive step in India?",
        "Do I need prior approval from the National Biodiversity Authority (NBA) before filing a patent?",
    ]
    selected_example = st.selectbox("Quick-fill demo queries:", example_options)

    st.markdown("---")
    # Health check for Ollama
    is_ollama_online = check_ollama_status()
    if is_ollama_online:
        st.success(f"🟢 Ollama LLM Active (`{OLLAMA_MODEL}`)")
    else:
        st.info("🟡 Extractive Mode Active (Ollama offline - zero crash fallback)")

    # Vectorstore status
    if os.path.exists(CHROMA_DIR):
        doc_count = get_collection_count()
        st.caption(f"📚 Vector DB Status: **{doc_count} chunks indexed**")
    else:
        st.error("⚠️ ChromaDB not found. Please run `python ingest.py` first.")


# ==============================================================================
# MAIN PAGE
# ==============================================================================
st.markdown('<div class="main-title">🌿 IP-SAKTI Sahayak</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Intelligent Knowledge-Routed RAG for Ayurveda Intellectual Property & Regulatory Compliance</div>',
    unsafe_allow_html=True,
)

# Query Input
default_text = "" if selected_example == "-- Select an example query --" else selected_example
user_query = st.text_input(
    "Enter your Ayurvedic IP, AYUSH, or Food Regulatory query:",
    value=default_text,
    placeholder="e.g. Can I patent a new polyherbal syrup using Ashwagandha and Tulsi?",
)

col_btn, col_clear = st.columns([1, 6])
with col_btn:
    run_button = st.button("🚀 Analyze & Guide", type="primary", use_container_width=True)

if run_button and user_query.strip():
    # --------------------------------------------------------------------------
    # STEP 1: ROUTING & CONTEXT EXTRACTION
    # --------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 1. Intent Analysis & Knowledge-Domain Routing")
    st.caption("The core innovation: The system identifies relevant legal/regulatory domains BEFORE retrieval.")

    selected_domains, reasons, context = route_query(user_query)

    # Display extracted contextual slots
    col_c1, col_c2, col_c3 = st.columns(3)
    col_c1.metric("Identified Biological Resource", context.get("detected_herbs", "None"))
    col_c2.metric("Product Category", context.get("product_type", "General"))
    col_c3.metric("Primary Objective", context.get("primary_goal", "Guidance"))

    st.markdown("##### Knowledge Domains Evaluation Matrix:")
    col_d1, col_d2 = st.columns(2)

    domain_keys = list(DOMAINS.keys())
    half = (len(domain_keys) + 1) // 2

    with col_d1:
        for d in domain_keys[:half]:
            d_info = DOMAINS[d]
            if d in selected_domains:
                st.markdown(
                    f"""
                    <div class="routed-card-selected">
                        <b>✅ {d_info['label']}</b><br>
                        <small style="color: #2e7d32;"><i>Reason: {reasons[d]}</i></small>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div class="routed-card-skipped">
                        <b>❌ {d_info['label']}</b><br>
                        <small><i>Skipped: Not triggered by query context</i></small>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with col_d2:
        for d in domain_keys[half:]:
            d_info = DOMAINS[d]
            if d in selected_domains:
                st.markdown(
                    f"""
                    <div class="routed-card-selected">
                        <b>✅ {d_info['label']}</b><br>
                        <small style="color: #2e7d32;"><i>Reason: {reasons[d]}</i></small>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div class="routed-card-skipped">
                        <b>❌ {d_info['label']}</b><br>
                        <small><i>Skipped: Not triggered by query context</i></small>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # Show future/unimplemented domains
        for u_key, u_label in UNIMPLEMENTED_DOMAINS.items():
            st.markdown(
                f"""
                <div class="routed-card-skipped">
                    <b>⬜ {u_label}</b><br>
                    <small><i>Proposed future domain (Not indexed in prototype)</i></small>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # --------------------------------------------------------------------------
    # STEP 2: RETRIEVAL FROM ROUTED DOMAINS ONLY
    # --------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 2. Domain-Filtered Evidence Retrieval")
    st.markdown(
        f"Retrieving exclusively from chunks matching domains: `{'`, `'.join(selected_domains)}`"
    )

    with st.spinner("Retrieving verified document excerpts from ChromaDB..."):
        retrieved_docs = retrieve_from_domains(user_query, selected_domains, k=3)

    if not retrieved_docs:
        st.warning(
            "No documents found matching the selected domains. Please ensure you have run `python ingest.py`."
        )
    else:
        with st.expander(f"📄 View {len(retrieved_docs)} Retrieved Evidence Excerpts", expanded=False):
            for i, doc in enumerate(retrieved_docs, start=1):
                meta = doc.metadata
                d_name = meta.get("document_name", "Document")
                page = meta.get("page", 1)
                dom = meta.get("domain", "general").upper()

                st.markdown(f"**[{i}] {d_name} (Page {page}) — Domain: `{dom}`**")
                st.write(doc.page_content.strip())
                st.divider()

    # --------------------------------------------------------------------------
    # STEP 3: GROUNDED AI ANSWER GENERATION
    # --------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 3. Grounded Regulatory Guidance")

    with st.spinner("Synthesizing grounded response with source citations..."):
        answer_text, citations = generate_answer(user_query, retrieved_docs)

    st.markdown(answer_text)

    # --------------------------------------------------------------------------
    # STEP 4: VERIFIED SOURCE CITATIONS
    # --------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 4. Verified Source Citations (Zero Hallucination)")
    st.caption("Citations are mapped directly from LangChain document metadata, not invented by the LLM.")

    if citations:
        for cit in citations:
            dom_label = DOMAINS.get(cit["domain"], {}).get("label", cit["domain"])
            st.markdown(
                f"""
                <div class="citation-box">
                    <b>[{cit['citation_id']}] {cit['document_name']} — Page {cit['page']}</b><br>
                    <span style="color: #2d6a4f; font-weight: 500;">Knowledge Domain: {dom_label}</span><br>
                    <small style="color: #495057;">"{cit['snippet'][:180]}..."</small>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No source citations available for this query.")

elif run_button:
    st.warning("Please enter a query to run the assistant.")
else:
    st.info("Select a demo query from the sidebar or type a query above, then click **Analyze & Guide**.")
