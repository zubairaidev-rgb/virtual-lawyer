"""
Create CrPC and Constitution JSON files for multi-source RAG
These complement the PPC and SHC case data
"""
import json
from pathlib import Path

def create_crpc_sections() -> list:
    """Create CrPC sections JSON"""
    print("📚 Creating CrPC sections...")
    
    crpc_sections = [
        {
            "section_number": "154",
            "title": "CrPC Section 154 - First Information Report (FIR)",
            "text": "Section 154 CrPC - First Information Report (FIR). Every information relating to the commission of a cognizable offence, if given orally to an officer in charge of a police station, shall be reduced to writing by him or under his direction, and be read over to the informant. Every such information, whether given in writing or reduced to writing, shall be signed by the person giving it. The FIR must be registered immediately. Delay in FIR can be fatal to prosecution case unless properly explained. The FIR sets the criminal law in motion and is crucial evidence.",
            "source": "crpc_section_154",
            "type": "crpc_section",
            "metadata": {"section": "154", "topic": "FIR"}
        },
        {
            "section_number": "155",
            "title": "CrPC Section 155 - Non-Cognizable Cases",
            "text": "Section 155 CrPC - Information as to non-cognizable cases. When information is given to an officer in charge of a police station of the commission within the limits of such station of a non-cognizable offence, he shall enter or cause to be entered the substance of the information in a book to be kept by such officer. The police cannot investigate non-cognizable offences without the order of a Magistrate. Non-cognizable offences require Magistrate's permission for investigation.",
            "source": "crpc_section_155",
            "type": "crpc_section",
            "metadata": {"section": "155", "topic": "Non-Cognizable"}
        },
        {
            "section_number": "164",
            "title": "CrPC Section 164 - Recording of Confessions",
            "text": "Section 164 CrPC - Recording of confessions and statements. Any Metropolitan Magistrate or Judicial Magistrate may record any confession or statement made to him in the course of an investigation. The confession must be voluntary and made in the presence of the Magistrate. The Magistrate must explain that the person is not bound to make the confession. Confessions to police are not admissible. Only confessions recorded under Section 164 CrPC are admissible in evidence. The Magistrate must ensure voluntariness.",
            "source": "crpc_section_164",
            "type": "crpc_section",
            "metadata": {"section": "164", "topic": "Confessions"}
        },
        {
            "section_number": "167",
            "title": "CrPC Section 167 - Remand and Detention",
            "text": "Section 167 CrPC - Procedure when investigation cannot be completed in twenty-four hours. The officer in charge shall forward the accused to the nearest Judicial Magistrate. The Magistrate may authorize detention for a term not exceeding fifteen days in total. In case of offences punishable with death, imprisonment for life, or imprisonment for not less than ten years, the detention may extend to ninety days. After expiry of remand period, the accused must be produced before court. This prevents indefinite detention.",
            "source": "crpc_section_167",
            "type": "crpc_section",
            "metadata": {"section": "167", "topic": "Remand"}
        },
        {
            "section_number": "173",
            "title": "CrPC Section 173 - Police Report (Challan)",
            "text": "Section 173 CrPC - Report of police officer on completion of investigation. As soon as investigation is completed, the officer in charge shall forward to a Magistrate a report in the prescribed form. This report is called the challan or charge sheet. The report must contain all material facts and evidence collected during investigation. The Magistrate takes cognizance based on this report. The challan is crucial for prosecution case.",
            "source": "crpc_section_173",
            "type": "crpc_section",
            "metadata": {"section": "173", "topic": "Challan"}
        },
        {
            "section_number": "497",
            "title": "CrPC Section 497 - Bail in Non-Bailable Offences",
            "text": "Section 497 CrPC - When bail may be taken in case of non-bailable offence. When any person accused of a non-bailable offence is arrested, he may be released on bail. However, such person shall not be so released if there appear reasonable grounds for believing that he has been guilty of an offence punishable with death or imprisonment for life. The court considers factors like nature of offence, evidence, likelihood of absconding, and tampering with evidence. Bail is discretionary in non-bailable offences.",
            "source": "crpc_section_497",
            "type": "crpc_section",
            "metadata": {"section": "497", "topic": "Bail"}
        },
        {
            "section_number": "498",
            "title": "CrPC Section 498 - High Court Power to Grant Bail",
            "text": "Section 498 CrPC - Power to direct admission to bail or reduction of bail. The High Court or Court of Session may direct that any person accused of an offence and in custody be released on bail. The High Court has wide powers to grant bail even in cases where bail is not normally granted. This is an extraordinary power to ensure justice. The High Court can grant bail in exceptional circumstances.",
            "source": "crpc_section_498",
            "type": "crpc_section",
            "metadata": {"section": "498", "topic": "Bail"}
        },
        {
            "section_number": "382-B",
            "title": "CrPC Section 382-B - Set-off of Detention Period",
            "text": "Section 382-B CrPC - Benefit of set-off. The period of detention undergone by the accused during investigation, inquiry, or trial, before the sentence of imprisonment is awarded, shall be set off against the term of imprisonment imposed on him. This means if an accused is in jail for 6 months before conviction and sentenced to 2 years, he only needs to serve 18 more months. This prevents double punishment and ensures fair treatment.",
            "source": "crpc_section_382b",
            "type": "crpc_section",
            "metadata": {"section": "382-B", "topic": "Set-off"}
        },
        {
            "section_number": "540",
            "title": "CrPC Section 540 - Power to Summon Witnesses",
            "text": "Section 540 CrPC - Power to summon material witness, or examine person present. Any court may, at any stage of any inquiry, trial, or other proceeding, summon any person as a witness, or examine any person in attendance, though not summoned as a witness, or recall and re-examine any person already examined. This section gives the court wide powers to ensure all relevant evidence is brought before it. The court can summon witnesses suo moto.",
            "source": "crpc_section_540",
            "type": "crpc_section",
            "metadata": {"section": "540", "topic": "Witnesses"}
        },
        {
            "section_number": "561-A",
            "title": "CrPC Section 561-A - Inherent Powers of High Court",
            "text": "Section 561-A CrPC - Saving of inherent power of High Court. Nothing in this Code shall be deemed to limit or affect the inherent power of the High Court to make such orders as may be necessary to give effect to any order under this Code, or to prevent abuse of the process of any court, or otherwise to secure the ends of justice. This section gives the High Court wide powers to prevent abuse of process and ensure justice. The High Court can quash proceedings if there is abuse of process.",
            "source": "crpc_section_561a",
            "type": "crpc_section",
            "metadata": {"section": "561-A", "topic": "Inherent Powers"}
        },
    ]
    
    return crpc_sections

def create_constitution_articles() -> list:
    """Create Constitution articles JSON"""
    print("📚 Creating Constitution articles...")
    
    constitution_articles = [
        {
            "article_number": "4",
            "title": "Constitution Article 4 - Right to be Dealt with According to Law",
            "text": "Article 4 of the Constitution of Pakistan - Right of individuals to be dealt with in accordance with law. To enjoy the protection of law and to be treated in accordance with law is the inalienable right of every citizen, wherever he may be, and of every other person for the time being within Pakistan. In particular, no action detrimental to the life, liberty, body, reputation, or property of any person shall be taken except in accordance with law. This article guarantees fundamental rights and due process. It ensures that all actions must be lawful.",
            "source": "constitution_article_4",
            "type": "constitution_article",
            "metadata": {"article": "4", "topic": "Right to Law"}
        },
        {
            "article_number": "9",
            "title": "Constitution Article 9 - Security of Person",
            "text": "Article 9 of the Constitution of Pakistan - Security of person. No person shall be deprived of life or liberty save in accordance with law. This article guarantees the fundamental right to life and liberty. Any deprivation of life or liberty must be in accordance with law, meaning through proper legal procedures. This is a fundamental right that cannot be suspended except during emergency. It protects against arbitrary detention and extrajudicial killings.",
            "source": "constitution_article_9",
            "type": "constitution_article",
            "metadata": {"article": "9", "topic": "Life and Liberty"}
        },
        {
            "article_number": "10",
            "title": "Constitution Article 10 - Safeguards for Arrest and Detention",
            "text": "Article 10 of the Constitution of Pakistan - Safeguards as to arrest and detention. No person who is arrested shall be detained in custody without being informed, as soon as may be, of the grounds for such arrest, nor shall he be denied the right to consult and be defended by a legal practitioner of his choice. Every person who is arrested and detained in custody shall be produced before a Magistrate within a period of twenty-four hours of such arrest. No such person shall be detained in custody beyond the said period without the authority of a Magistrate. This article protects against arbitrary arrest and ensures due process.",
            "source": "constitution_article_10",
            "type": "constitution_article",
            "metadata": {"article": "10", "topic": "Arrest Rights"}
        },
        {
            "article_number": "10-A",
            "title": "Constitution Article 10-A - Right to Fair Trial",
            "text": "Article 10-A of the Constitution of Pakistan - Right to fair trial. For the determination of his civil rights and obligations or in a criminal charge, a person shall be entitled to a fair trial and due process. This article guarantees the right to a fair trial, which includes the right to be heard, right to legal representation, right to present evidence, and right to be tried by an impartial tribunal. Fair trial is a fundamental right essential for justice.",
            "source": "constitution_article_10a",
            "type": "constitution_article",
            "metadata": {"article": "10-A", "topic": "Fair Trial"}
        },
        {
            "article_number": "13",
            "title": "Constitution Article 13 - Protection Against Double Jeopardy",
            "text": "Article 13 of the Constitution of Pakistan - Protection against double punishment and self-incrimination. No person shall be prosecuted or punished for the same offence more than once. No person shall, when accused of an offence, be compelled to be a witness against himself. This article protects against double jeopardy and self-incrimination. It ensures that a person cannot be tried twice for the same offence and cannot be forced to testify against themselves.",
            "source": "constitution_article_13",
            "type": "constitution_article",
            "metadata": {"article": "13", "topic": "Double Jeopardy"}
        },
        {
            "article_number": "14",
            "title": "Constitution Article 14 - Dignity and Privacy",
            "text": "Article 14 of the Constitution of Pakistan - Inviolability of dignity of man. The dignity of man and, subject to law, the privacy of home, shall be inviolable. This article protects human dignity and privacy. It ensures that individuals are treated with respect and that their privacy is protected, subject to lawful restrictions. Dignity and privacy are fundamental rights that must be respected.",
            "source": "constitution_article_14",
            "type": "constitution_article",
            "metadata": {"article": "14", "topic": "Dignity"}
        },
    ]
    
    return constitution_articles

def main():
    """Main function"""
    print("=" * 60)
    print("CREATING CrPC AND CONSTITUTION JSON FILES")
    print("=" * 60)
    print()
    
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create CrPC sections
    crpc_sections = create_crpc_sections()
    crpc_path = output_dir / "crpc_sections.json"
    with open(crpc_path, 'w', encoding='utf-8') as f:
        json.dump(crpc_sections, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved {len(crpc_sections)} CrPC sections to {crpc_path}")
    
    # Create Constitution articles
    constitution_articles = create_constitution_articles()
    const_path = output_dir / "constitution_articles.json"
    with open(const_path, 'w', encoding='utf-8') as f:
        json.dump(constitution_articles, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved {len(constitution_articles)} Constitution articles to {const_path}")
    
    print("\n" + "=" * 60)
    print("✅ COMPLETE")
    print("=" * 60)
    print("\n📝 Next steps:")
    print("   1. Process PPC PDF: python process_ppc_pdf_to_json.py")
    print("   2. Process SHC cases: python process_shc_cases_to_rag.py")
    print("   3. Test pipeline: python test_multi_layer_pipeline.py")

if __name__ == "__main__":
    main()























