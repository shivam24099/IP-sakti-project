"""
router.py
---------
Lightweight, rule-based intent extraction and knowledge-domain router for IP-SAKTI Sahayak.

CORE CONCEPT DEMONSTRATED:
    User Query -> Context/Intent Extraction -> Domain Routing -> Filtered Retrieval

This replaces complex, opaque LangChain agents with a clear, deterministic Python
function that a B.Tech student can easily explain to SIH judges.
"""

from typing import Dict, List, Tuple


# ==============================================================================
# 1. KNOWLEDGE DOMAIN DEFINITIONS
# ==============================================================================
DOMAINS = {
    "patent": {
        "label": "Patent / Intellectual Property",
        "description": "Patents Act 1970, patentability, novelty, inventive step, prior art, claims, Section 3 exclusions",
    },
    "ayurveda_tk": {
        "label": "Ayurveda / Traditional Knowledge",
        "description": "Classical Ayurvedic texts, formulations, medicinal herbs, TKDL (Traditional Knowledge Digital Library)",
    },
    "ayush": {
        "label": "AYUSH Regulatory Compliance",
        "description": "Drugs & Cosmetics Act (Schedule T), AYUSH manufacturing licenses, GMP certification, ASU drug rules",
    },
    "fssai": {
        "label": "FSSAI / Food Safety Regulations",
        "description": "Food Safety & Standards Act, Ayur-Aahar, dietary supplements, nutraceuticals, food labeling",
    },
    "biodiversity_abs": {
        "label": "Biodiversity / ABS (NBA)",
        "description": "Biological Diversity Act 2002, National Biodiversity Authority (NBA), Form III patent approval, Access & Benefit Sharing",
    },
}

# Domains displayed in the UI as 'Not Implemented / Future Scope'
UNIMPLEMENTED_DOMAINS = {
    "copyright_gi": "Copyright & Geographical Indications (GI)",
    "trademark": "Trademark & Brand Protection",
}


# ==============================================================================
# 2. KEYWORD DICTIONARIES FOR INTENT EXTRACTION
# ==============================================================================
KEYWORDS = {
    "patent": [
        "patent", "patentability", "invention", "prior art", "novelty",
        "inventive step", "claims", "patent office", "ip india", "infringement",
        "provisional", "specification", "section 3", "synergy",
    ],
    "ayurveda_tk": [
        "ayurved", "ayurvedic", "traditional knowledge", "tkdl", "formulation",
        "polyherbal", "churna", "kwatha", "arishta", "classical text", "charaka",
        "sushruta", "dravyaguna", "herbal", "medicinal plant",
    ],
    "ayush": [
        "ayush", "license", "manufacturing license", "gmp", "schedule t",
        "drugs and cosmetics", "asu drug", "proprietary medicine", "classical medicine",
        "state licensing authority", "quality control", "heavy metal",
    ],
    "fssai": [
        "fssai", "food safety", "food", "nutraceutical", "dietary supplement",
        "supplement", "health food", "ayur-aahar", "ayur aahar", "tea", "beverage",
        "food license", "labeling", "not for medicinal use",
    ],
    "biodiversity_abs": [
        "biodiversity", "biological diversity", "abs", "access and benefit",
        "nba", "national biodiversity authority", "state biodiversity board", "sbb",
        "biological resource", "genetic resource", "form iii", "benefit sharing",
    ],
}

# Known Indian biological/Ayurvedic herbs triggering biological resource rules
KNOWN_HERBS = [
    "neem", "turmeric", "ashwagandha", "tulsi", "triphala", "brahmi",
    "amla", "guggulu", "shatavari", "aloe vera", "giloy", "moringa",
]


# ==============================================================================
# 3. CONTEXT EXTRACTION & ROUTING FUNCTION
# ==============================================================================
def route_query(query: str) -> Tuple[List[str], Dict[str, str], Dict[str, str]]:
    """
    Analyzes user query and routes it to one or more relevant knowledge domains.

    Returns:
        selected_domains: List of domain keys (e.g. ['patent', 'ayurveda_tk'])
        reasons: Dictionary mapping domain key to human-readable explanation
        context: Extracted structured context (product, detected herbs, objective)
    """
    q = query.lower()
    selected_domains = []
    reasons = {}

    # 1. Extract contextual clues
    detected_herbs = [herb.capitalize() for herb in KNOWN_HERBS if herb in q]
    has_formulation = any(term in q for term in ["formulation", "medicine", "product", "extract", "tea", "remedy"])
    has_patent_goal = any(term in q for term in ["patent", "patenting", "protect", "novelty", "file"])
    has_food_goal = any(term in q for term in ["food", "supplement", "nutraceutical", "ayur-aahar", "tea", "beverage"])

    context = {
        "detected_herbs": ", ".join(detected_herbs) if detected_herbs else "None specified",
        "product_type": "Ayurvedic Formulation / Extract" if (detected_herbs or has_formulation) else "General IP / Regulatory",
        "primary_goal": "Patent Protection" if has_patent_goal else ("Food Regulation" if has_food_goal else "General Guidance"),
    }

    # 2. Rule 1: Direct keyword matching for all knowledge domains
    for domain, kws in KEYWORDS.items():
        matched = [k for k in kws if k in q]
        if matched:
            selected_domains.append(domain)
            reasons[domain] = f"Matched keywords: {', '.join(matched[:3])}"

    # 3. Rule 2: Multi-Dimensional Cross-Domain Routing Rules
    # Case A: Ayurvedic formulation / herb + Patenting intent
    # Under Indian Patent Act Section 3(p), traditional knowledge is non-patentable.
    # Therefore, both Patent AND Ayurveda/TK domains must be checked.
    if has_patent_goal and (detected_herbs or "ayurved" in q or "herb" in q):
        if "patent" not in selected_domains:
            selected_domains.append("patent")
            reasons["patent"] = "Query involves patenting an invention"
        if "ayurveda_tk" not in selected_domains:
            selected_domains.append("ayurveda_tk")
            reasons["ayurveda_tk"] = "Formulation involves traditional herbs / Ayurvedic knowledge"

        # Case B: If an Indian biological resource is being patented,
        # Section 6 of the Biological Diversity Act 2002 requires National Biodiversity Authority (NBA) approval!
        if detected_herbs and "biodiversity_abs" not in selected_domains:
            selected_domains.append("biodiversity_abs")
            reasons["biodiversity_abs"] = (
                f"Uses Indian biological resource ({', '.join(detected_herbs)}) requiring NBA / ABS clearance"
            )

    # Case C: Ayurvedic herb/product + Food / Supplement / Beverage intent
    # Needs FSSAI (for Ayur-Aahar & food safety) + AYUSH (for boundary with ASU drug license)
    if has_food_goal and (detected_herbs or "ayurved" in q or "herb" in q):
        if "fssai" not in selected_domains:
            selected_domains.append("fssai")
            reasons["fssai"] = "Query relates to food safety, dietary supplement, or Ayur-Aahar rules"
        if "ayurveda_tk" not in selected_domains:
            selected_domains.append("ayurveda_tk")
            reasons["ayurveda_tk"] = "Formulation uses Ayurvedic botanicals"
        if "ayush" not in selected_domains:
            selected_domains.append("ayush")
            reasons["ayush"] = "To determine regulatory boundary between Food (FSSAI) and Drug (AYUSH)"

    # Default fallback: if no domain triggered, guide user to general Patent & Ayurveda
    if not selected_domains:
        selected_domains = ["patent", "ayurveda_tk"]
        reasons["patent"] = "Default fallback for general IP guidance"
        reasons["ayurveda_tk"] = "Default fallback for traditional knowledge consultation"

    return selected_domains, reasons, context


# ==============================================================================
# Quick Standalone Test
# ==============================================================================
if __name__ == "__main__":
    test_queries = [
        "Can I patent my new Ayurvedic formulation made of neem and turmeric?",
        "What are the food safety and labeling regulations for Ayurvedic herbal tea?",
        "How do I obtain an AYUSH manufacturing license and comply with Schedule T GMP?",
        "What are the patent novelty criteria in India?",
        "Do I need NBA approval before filing an international patent for an Indian plant extract?",
    ]

    print("=" * 80)
    print("IP-SAKTI SAHAYAK - ROUTING LOGIC DEMO")
    print("=" * 80)

    for i, q in enumerate(test_queries, 1):
        domains, explanations, ctx = route_query(q)
        print(f"\nQuery #{i}: \"{q}\"")
        print(f"Extracted Context: {ctx}")
        print("Routed Domains:")
        for d in domains:
            print(f"  [+] {DOMAINS[d]['label']}: {explanations[d]}")
