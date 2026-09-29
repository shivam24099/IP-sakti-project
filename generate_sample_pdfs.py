"""
generate_sample_pdfs.py
-----------------------
Generates 5 realistic, domain-specific sample PDF documents for the
IP-SAKTI Sahayak prototype using ReportLab.

These PDFs serve as the official knowledge base across 5 key domains:
1. Patent / IP (patent_guidelines.pdf)
2. Ayurveda / Traditional Knowledge (ayurveda_tk_compendium.pdf)
3. AYUSH Regulatory (ayush_manufacturing_rules.pdf)
4. FSSAI Regulations (fssai_nutraceutical_regulations.pdf)
5. Biodiversity / ABS (nba_biodiversity_abs_guidelines.pdf)
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

PDF_DIR = os.path.join(os.path.dirname(__file__), "data", "pdfs")
os.makedirs(PDF_DIR, exist_ok=True)


def build_pdf(filename, pages_content):
    filepath = os.path.join(PDF_DIR, filename)
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54,
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1b4332"),
        spaceAfter=12,
    )
    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#2d6a4f"),
        spaceBefore=10,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#212529"),
        spaceAfter=8,
    )

    story = []
    for i, page_data in enumerate(pages_content):
        if i > 0:
            story.append(PageBreak())

        story.append(Paragraph(page_data["title"], title_style))
        story.append(Spacer(1, 10))

        for section in page_data["sections"]:
            story.append(Paragraph(section["heading"], heading_style))
            story.append(Paragraph(section["body"], body_style))
            story.append(Spacer(1, 8))

    doc.build(story)
    print(f"Created: {filepath} ({len(pages_content)} pages)")


def generate_all_sample_pdfs():
    print("Generating sample PDFs for IP-SAKTI Sahayak...\n")

    # 1. Patent Guidelines PDF (2 Pages)
    patent_pages = [
        {
            "title": "Indian Patent Office: Guidelines for Patentability (Page 1)",
            "sections": [
                {
                    "heading": "1. Statutory Patentability Criteria (Section 2(1)(j))",
                    "body": "Under the Indian Patents Act 1970, an invention is patentable only if it satisfies three statutory criteria: Novelty (new compared to existing prior art worldwide), Inventive Step (a feature of an invention that involves technical advance as compared to existing knowledge and makes it non-obvious to a person skilled in the art), and Industrial Applicability (the invention is capable of being made or used in an industry).",
                },
                {
                    "heading": "2. Filing Procedure and Specifications",
                    "body": "An applicant may initially file a Provisional Specification to secure a priority date. Within 12 months from the date of filing the provisional application, a Complete Specification detailing full description, best method of performing the invention, and precise patent claims must be submitted to the Patent Office.",
                },
            ],
        },
        {
            "title": "Indian Patent Office: Non-Patentable Inventions & TK (Page 2)",
            "sections": [
                {
                    "heading": "3. Section 3(p) Traditional Knowledge Exclusion",
                    "body": "Section 3(p) of the Patents Act explicitly states that an invention which in effect is traditional knowledge or an aggregation or duplication of known properties of traditionally known components is not an invention. Therefore, traditional Ayurvedic remedies, known uses of herbs like Neem or Turmeric, or classical decoctions cannot be patented as standalone compositions.",
                },
                {
                    "heading": "4. Section 3(e) Mere Admixture vs. Synergistic Formulations",
                    "body": "Under Section 3(e), a substance obtained by a mere admixture resulting only in aggregation of properties is not patentable. To overcome Section 3(e) and Section 3(p), the applicant must prove technical synergy—experimental evidence demonstrating unexpected biological efficacy beyond the additive effects of the individual herbal ingredients.",
                },
            ],
        },
    ]
    build_pdf("patent_guidelines.pdf", patent_pages)

    # 2. Ayurveda & Traditional Knowledge Compendium (2 Pages)
    ayurveda_pages = [
        {
            "title": "Ayurveda & Traditional Knowledge Compendium (Page 1)",
            "sections": [
                {
                    "heading": "1. Classical Formulations and Polyherbal Science",
                    "body": "Classical Ayurvedic pharmacology (Dravyaguna and Bhasajya Kalpana) emphasizes polyherbal formulations categorized as Churna (powders), Asava/Arishta (fermented decoctions), Kwatha (extracts), and Ghrita (medicated ghee). Key herbs such as Neem (Azadirachta indica), Ashwagandha (Withania somnifera), Turmeric (Curcuma longa), and Tulsi (Ocimum sanctum) have defined therapeutic profiles in ancient Ayurvedic treatises.",
                },
                {
                    "heading": "2. Classical Text References & Documentation",
                    "body": "The authoritative Ayurvedic texts referenced under the First Schedule of the Drugs and Cosmetics Act include Charaka Samhita, Sushruta Samhita, Astanga Hridaya, and Sharangadhara Samhita. Any formulation prepared strictly following the recipes, methods, and indications described in these authoritative texts is classified as a Classical Ayurvedic Medicine.",
                },
            ],
        },
        {
            "title": "Ayurveda & Traditional Knowledge Compendium (Page 2)",
            "sections": [
                {
                    "heading": "3. Traditional Knowledge Digital Library (TKDL)",
                    "body": "The Traditional Knowledge Digital Library (TKDL) is a pioneering Indian database that translates and organizes traditional knowledge from classical Sanskrit, Urdu, Arabic, and Tamil texts into five international languages (English, French, German, Japanese, Spanish). TKDL provides International Patent Offices with documented prior art to prevent misappropriation and bio-piracy of Indian traditional knowledge.",
                },
                {
                    "heading": "4. Patent Examination and TKDL Prior Art Citations",
                    "body": "When an Ayurvedic researcher files a patent, patent examiners search TKDL. If the claimed formulation, herb extract, or therapeutic use is documented in TKDL, the claim is rejected for lack of novelty under Section 3(p). Applicants must clearly disclose novel extraction methodologies, novel delivery systems (e.g. nano-carriers), or non-obvious synergistic combinations not found in classical literature.",
                },
            ],
        },
    ]
    build_pdf("ayurveda_tk_compendium.pdf", ayurveda_pages)

    # 3. AYUSH Regulatory & Manufacturing Guidelines (2 Pages)
    ayush_pages = [
        {
            "title": "Ministry of AYUSH: Drug Manufacturing & Licensing (Page 1)",
            "sections": [
                {
                    "heading": "1. Regulatory Framework for ASU Drugs",
                    "body": "Manufacture and sale of Ayurveda, Siddha, and Unani (ASU) medicines in India are governed by Chapter IV-A of the Drugs and Cosmetics Act 1940 and the Drugs and Cosmetics Rules 1945. Commercial manufacturing of any Ayurvedic medicine requires a valid manufacturing license issued by the State Licensing Authority (SLA) under the AYUSH department.",
                },
                {
                    "heading": "2. Classical vs. Proprietary Ayurvedic Medicines",
                    "body": "Ayurvedic products are divided into two legal categories: (1) Classical Ayurvedic Medicines, manufactured strictly according to formulas in recognized books of First Schedule, requiring proof of textual reference; and (2) Ayurvedic Proprietary Medicines, which contain ingredients mentioned in classical texts but formulated in a non-classical combination, dosage form, or extract. Proprietary medicines require pilot clinical trials and safety documentation before licensing.",
                },
            ],
        },
        {
            "title": "Ministry of AYUSH: Quality Compliance & GMP (Page 2)",
            "sections": [
                {
                    "heading": "3. Schedule T Good Manufacturing Practices (GMP)",
                    "body": "All Ayurvedic manufacturing premises must strictly comply with Schedule T of the Drugs and Cosmetics Rules. Schedule T mandates hygienic factory premises, air handling units, cross-contamination prevention, water purification, qualified Ayurvedic pharmacists, and fully equipped in-house quality control testing laboratories.",
                },
                {
                    "heading": "4. Quality Control & Safety Testing Parameters",
                    "body": "Before commercial release, every batch of Ayurvedic formulation must be tested for Pharmacopoeial standards: limits on heavy metals (Lead, Cadmium, Mercury, Arsenic), pesticide residues, microbial contamination (E. coli, Salmonella), and aflatoxins as specified in the Ayurvedic Pharmacopoeia of India (API).",
                },
            ],
        },
    ]
    build_pdf("ayush_manufacturing_rules.pdf", ayush_pages)

    # 4. FSSAI Nutraceuticals & Ayur-Aahar Regulations (2 Pages)
    fssai_pages = [
        {
            "title": "FSSAI Regulations: Nutraceuticals & Ayur-Aahar (Page 1)",
            "sections": [
                {
                    "heading": "1. Scope of FSSAI Food and Supplement Regulations",
                    "body": "The Food Safety and Standards Authority of India (FSSAI) governs Health Supplements, Nutraceuticals, Food for Special Dietary Use (FSDU), and Ayur-Aahar products under the FSS (Health Supplements, Nutraceuticals, Food for Special Dietary Use, Food for Special Medical Purpose, and Prebiotic and Probiotic Food) Regulations.",
                },
                {
                    "heading": "2. Ayur-Aahar Category Rules",
                    "body": "FSSAI introduced special regulations for 'Ayur-Aahar' (food products prepared in accordance with the recipes or principles of Ayurveda). Ayur-Aahar products are meant to promote wellness, sustain physiological functions, and support digestion. However, Ayur-Aahar products must NOT be presented as medicines or remedies for diagnosing, treating, or preventing specific human diseases.",
                },
            ],
        },
        {
            "title": "FSSAI Regulations: Permissible Ingredients & Labeling (Page 2)",
            "sections": [
                {
                    "heading": "3. Permitted Botanicals and Ingredients",
                    "body": "Food supplements and Ayur-Aahar may only contain botanical ingredients explicitly listed in Schedule IV or approved by FSSAI. Ingredients listed under Schedule E of the Drugs and Cosmetics Act (poisonous substances/Schedule E1 herbs) are strictly prohibited from use in food, herbal teas, or nutritional supplements.",
                },
                {
                    "heading": "4. Mandatory Labeling and Disclaimer Requirements",
                    "body": "All Ayurvedic food and supplement packaging must carry the official Ayur-Aahar logo, list nutritional values per 100g/serving, and display the mandatory statutory disclaimer: 'NOT FOR MEDICINAL USE'. False or misleading therapeutic claims can lead to immediate cancellation of the FSSAI license and penal action under Section 53 of the FSS Act.",
                },
            ],
        },
    ]
    build_pdf("fssai_nutraceutical_regulations.pdf", fssai_pages)

    # 5. National Biodiversity Authority & ABS Guidelines (2 Pages)
    nba_pages = [
        {
            "title": "National Biodiversity Authority: ABS Regulations (Page 1)",
            "sections": [
                {
                    "heading": "1. The Biological Diversity Act 2002 Overview",
                    "body": "The Biological Diversity Act 2002 was enacted to conserve biological diversity, promote sustainable use of its components, and ensure fair and equitable sharing of benefits arising out of the utilization of Indian biological resources and associated traditional knowledge. It is administered by the National Biodiversity Authority (NBA) at national level and State Biodiversity Boards (SBB) at state level.",
                },
                {
                    "heading": "2. Access and Benefit Sharing (ABS) Mechanism",
                    "body": "Commercial utilization of biological resources (herbs, roots, microbial strains, seeds collected from India) requires prior intimation to the concerned SBB for Indian entities, or prior approval of NBA for foreign entities/NRIs. The entity must enter into an Access and Benefit Sharing (ABS) agreement, depositing a percentage of annual sales (typically 0.1% to 0.5%) into the National Biodiversity Fund for community conservation.",
                },
            ],
        },
        {
            "title": "NBA Approval for Patent Applications (Page 2)",
            "sections": [
                {
                    "heading": "3. Section 6 Mandate: Prior NBA Approval for Patents",
                    "body": "Section 6(1) of the Biological Diversity Act mandates that no person shall apply for any intellectual property right, by whatever name called, in or outside India for any invention based on any research or information on a biological resource obtained from India, without obtaining the prior approval of the National Biodiversity Authority (NBA).",
                },
                {
                    "heading": "4. Form III Application Procedure",
                    "body": "Applicants must submit Form III to the NBA along with the patent application details. In the patent specification filed before the Indian Patent Office, the applicant must formally disclose the geographic source and origin of the biological resource used in the invention. Failure to obtain NBA clearance can lead to refusal of patent grant and criminal prosecution under Section 55 of the Act.",
                },
            ],
        },
    ]
    build_pdf("nba_biodiversity_abs_guidelines.pdf", nba_pages)

    print("\nAll 5 domain sample PDFs successfully generated in data/pdfs/!")


if __name__ == "__main__":
    generate_all_sample_pdfs()
