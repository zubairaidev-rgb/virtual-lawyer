"""
Create Best RAG Corpus for Pakistan Criminal Law
Builds comprehensive corpus from essential PPC, CrPC, and Constitution sections
"""
import json
from pathlib import Path
from typing import List, Dict

def create_ppc_sections() -> List[Dict]:
    """Create comprehensive PPC sections corpus - EXPANDED VERSION"""
    print("📚 Creating comprehensive PPC sections corpus...")
    
    ppc_sections = [
        {
            "text": "Section 302 PPC - Punishment for qatl-i-amd (murder). Whoever commits qatl-i-amd shall be punished with death, or imprisonment for life, and shall also be liable to fine. Qatl-i-amd means intentional killing with the intention of causing death or such bodily injury as is likely to cause death. This is a non-bailable and cognizable offence. The court may also award compensation (diyat) to the legal heirs of the deceased.",
            "title": "PPC Section 302 - Murder (Qatl-i-amd)",
            "source": "ppc_section_302"
        },
        {
            "text": "Section 300 PPC - Definition of qatl-i-amd (murder). Qatl-i-amd is committed when a person causes death of another person with the intention of causing death, or with the intention of causing such bodily injury as is likely to cause death, or with the knowledge that his act is likely to cause death. This is the most serious form of homicide under Pakistan law.",
            "title": "PPC Section 300 - Definition of Murder",
            "source": "ppc_section_300"
        },
        {
            "text": "Section 324 PPC - Attempt to commit qatl-i-amd. Whoever attempts to commit qatl-i-amd shall be punished with imprisonment for life, or with imprisonment of either description for a term which may extend to ten years, and shall also be liable to fine. This is a non-bailable and cognizable offence.",
            "title": "PPC Section 324 - Attempt to Murder",
            "source": "ppc_section_324"
        },
        {
            "text": "Section 337 PPC - Hurt. Whoever causes hurt to any person shall be punished with imprisonment of either description for a term which may extend to one year, or with fine which may extend to one thousand rupees, or with both. Hurt means causing bodily pain, disease, or infirmity to any person.",
            "title": "PPC Section 337 - Hurt",
            "source": "ppc_section_337"
        },
        {
            "text": "Section 337-A PPC - Grievous hurt. Whoever causes grievous hurt to any person shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine. Grievous hurt includes emasculation, permanent privation of sight or hearing, privation of any member or joint, destruction of powers of any member or joint, permanent disfiguration of head or face, fracture or dislocation of bone or tooth, or any hurt which endangers life or causes severe bodily pain.",
            "title": "PPC Section 337-A - Grievous Hurt",
            "source": "ppc_section_337a"
        },
        {
            "text": "Section 376 PPC - Rape. Whoever commits rape shall be punished with death or imprisonment for life, and shall also be liable to fine. Rape is committed when a man has sexual intercourse with a woman against her will, without her consent, or with her consent when consent has been obtained by putting her in fear of death or hurt, or when she is under sixteen years of age. This is a non-bailable and cognizable offence.",
            "title": "PPC Section 376 - Rape",
            "source": "ppc_section_376"
        },
        {
            "text": "Section 420 PPC - Cheating and dishonestly inducing delivery of property. Whoever cheats and thereby dishonestly induces the person deceived to deliver any property to any person, or to make, alter, or destroy the whole or any part of a valuable security, shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine. This is a non-bailable and cognizable offence.",
            "title": "PPC Section 420 - Cheating",
            "source": "ppc_section_420"
        },
        {
            "text": "Section 395 PPC - Dacoity. Whoever commits dacoity shall be punished with imprisonment for life, or with rigorous imprisonment for a term which may extend to ten years, and shall also be liable to fine. Dacoity is robbery committed by five or more persons conjointly. This is a non-bailable and cognizable offence.",
            "title": "PPC Section 395 - Dacoity",
            "source": "ppc_section_395"
        },
        {
            "text": "Section 392 PPC - Robbery. Whoever commits robbery shall be punished with rigorous imprisonment for a term which may extend to ten years, and shall also be liable to fine. Robbery is theft or extortion committed in order to commit theft, or when the offender voluntarily causes or attempts to cause to any person death, hurt, or wrongful restraint, or fear of instant death, instant hurt, or instant wrongful restraint. This is a non-bailable and cognizable offence.",
            "title": "PPC Section 392 - Robbery",
            "source": "ppc_section_392"
        },
        {
            "text": "Section 379 PPC - Theft. Whoever commits theft shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both. Theft is committed when a person moves any moveable property out of the possession of any person without that person's consent, with dishonest intention. This is a cognizable and non-bailable offence if the value of stolen property exceeds twenty-five thousand rupees, otherwise it is bailable.",
            "title": "PPC Section 379 - Theft",
            "source": "ppc_section_379"
        },
        {
            "text": "Section 382 PPC - Theft after preparation made for causing death, hurt, or restraint. Whoever commits theft, having made preparation for causing death, or hurt, or restraint, or fear of death, or of hurt, or of restraint, to any person, in order to the committing of such theft, shall be punished with rigorous imprisonment for a term which may extend to ten years, and shall also be liable to fine. This is a non-bailable and cognizable offence.",
            "title": "PPC Section 382 - Theft with Preparation",
            "source": "ppc_section_382"
        },
        {
            "text": "Section 497 PPC - Adultery. Whoever has sexual intercourse with a person who is and whom he knows or has reason to believe to be the wife of another man, without the consent or connivance of that man, such sexual intercourse not amounting to rape, is said to commit adultery. This section was declared unconstitutional by the Federal Shariat Court. The punishment was imprisonment for five years and fine.",
            "title": "PPC Section 497 - Adultery",
            "source": "ppc_section_497"
        },
        {
            "text": "Section 506 PPC - Criminal intimidation. Whoever commits criminal intimidation shall be punished with imprisonment of either description for a term which may extend to two years, or with fine, or with both. Criminal intimidation is committed when a person threatens another with any injury to his person, reputation, or property, or to the person, reputation, or property of any one in whom that person is interested, with intent to cause alarm to that person, or to cause that person to do any act which he is not legally bound to do, or to omit to do any act which that person is legally entitled to do.",
            "title": "PPC Section 506 - Criminal Intimidation",
            "source": "ppc_section_506"
        },
        {
            "text": "Section 109 PPC - Punishment of abetment. Whoever abets any offence shall, if the act abetted is committed in consequence of the abetment, and no express provision is made by this Code for the punishment of such abetment, be punished with the punishment provided for the offence. Abetment means instigating, engaging in a conspiracy, or intentionally aiding the commission of an offence.",
            "title": "PPC Section 109 - Abetment",
            "source": "ppc_section_109"
        },
        {
            "text": "Section 34 PPC - Acts done by several persons in furtherance of common intention. When a criminal act is done by several persons in furtherance of the common intention of all, each of such persons is liable for that act in the same manner as if it were done by him alone. This section creates joint liability for acts committed in furtherance of common intention.",
            "title": "PPC Section 34 - Common Intention",
            "source": "ppc_section_34"
        },
    ]
    
    print(f"   ✅ Created {len(ppc_sections)} PPC sections")
    return ppc_sections

def create_crpc_sections() -> List[Dict]:
    """Create comprehensive CrPC sections corpus"""
    print("📚 Creating CrPC sections corpus...")
    
    crpc_sections = [
        {
            "text": "Section 154 CrPC - First Information Report (FIR). Every information relating to the commission of a cognizable offence, if given orally to an officer in charge of a police station, shall be reduced to writing by him or under his direction, and be read over to the informant. Every such information, whether given in writing or reduced to writing, shall be signed by the person giving it. The FIR is the first step in criminal proceedings and must be registered immediately upon receiving information about a cognizable offence.",
            "title": "CrPC Section 154 - First Information Report (FIR)",
            "source": "crpc_section_154"
        },
        {
            "text": "Section 155 CrPC - Information as to non-cognizable cases. When information is given to an officer in charge of a police station of the commission within the limits of such station of a non-cognizable offence, he shall enter or cause to be entered the substance of the information in a book to be kept by such officer. The police cannot investigate non-cognizable offences without the order of a Magistrate.",
            "title": "CrPC Section 155 - Non-Cognizable Cases",
            "source": "crpc_section_155"
        },
        {
            "text": "Section 164 CrPC - Recording of confessions and statements. Any Metropolitan Magistrate or Judicial Magistrate may, whether or not he has jurisdiction in the case, record any confession or statement made to him in the course of an investigation under this Code or at any time afterwards before the commencement of the inquiry or trial. The confession must be voluntary and made in the presence of the Magistrate. The Magistrate must explain to the person making the confession that he is not bound to make it.",
            "title": "CrPC Section 164 - Recording of Confessions",
            "source": "crpc_section_164"
        },
        {
            "text": "Section 167 CrPC - Procedure when investigation cannot be completed in twenty-four hours. Whenever any person is arrested and detained in custody, and it appears that the investigation cannot be completed within the period of twenty-four hours, the officer in charge of the police station shall forward to the nearest Judicial Magistrate a copy of the entries in the diary and the accused person. The Magistrate may authorize detention for a term not exceeding fifteen days in total, or in case of offences punishable with death, imprisonment for life, or imprisonment for a term of not less than ten years, for a term not exceeding ninety days.",
            "title": "CrPC Section 167 - Remand and Detention",
            "source": "crpc_section_167"
        },
        {
            "text": "Section 173 CrPC - Report of police officer on completion of investigation. Every investigation under this Chapter shall be completed without unnecessary delay. As soon as it is completed, the officer in charge of the police station shall forward to a Magistrate empowered to take cognizance of the offence a report in the form prescribed by the Provincial Government. This report is called the challan or charge sheet.",
            "title": "CrPC Section 173 - Police Report (Challan)",
            "source": "crpc_section_173"
        },
        {
            "text": "Section 249-A CrPC - Acquittal of accused when complainant is absent. If the complainant is absent on the day fixed for hearing, the Magistrate may, in his discretion, acquit the accused unless for some reason he thinks it proper to adjourn the hearing of the case to some other day. This section applies to summons cases.",
            "title": "CrPC Section 249-A - Acquittal for Absence",
            "source": "crpc_section_249a"
        },
        {
            "text": "Section 265-K CrPC - Power to release on probation. When any person is convicted of an offence not punishable with death or imprisonment for life, and the court is of opinion that, having regard to the circumstances including the nature of the offence and the character of the offender, it is expedient to release him on probation of good conduct, the court may, instead of sentencing him at once to any punishment, direct that he be released on his entering into a bond, with or without sureties, to appear and receive sentence when called upon during such period as the court may direct.",
            "title": "CrPC Section 265-K - Probation",
            "source": "crpc_section_265k"
        },
        {
            "text": "Section 382-B CrPC - Benefit of set-off. The period of detention undergone by the accused during the investigation, inquiry, or trial of the case, before the sentence of imprisonment is awarded, shall be set off against the term of imprisonment imposed on him. This means if an accused is in jail for 6 months before conviction, and sentenced to 2 years, he only needs to serve 18 more months.",
            "title": "CrPC Section 382-B - Set-off of Detention Period",
            "source": "crpc_section_382b"
        },
        {
            "text": "Section 497 CrPC - When bail may be taken in case of non-bailable offence. When any person accused of, or suspected of, the commission of any non-bailable offence is arrested or detained without warrant, he may be released on bail. However, such person shall not be so released if there appear reasonable grounds for believing that he has been guilty of an offence punishable with death or imprisonment for life, or if the offence is a cognizable offence and he had been previously convicted of an offence punishable with death, imprisonment for life, or imprisonment for seven years or more.",
            "title": "CrPC Section 497 - Bail in Non-Bailable Offences",
            "source": "crpc_section_497"
        },
        {
            "text": "Section 498 CrPC - Power to direct admission to bail or reduction of bail. The High Court or Court of Session may direct that any person accused of an offence and in custody be released on bail, and if the offence is bailable, may direct that the bail required by a police officer or Magistrate be reduced. The High Court has wide powers to grant bail even in cases where bail is not normally granted.",
            "title": "CrPC Section 498 - High Court Power to Grant Bail",
            "source": "crpc_section_498"
        },
        {
            "text": "Section 540 CrPC - Power to summon material witness, or examine person present. Any court may, at any stage of any inquiry, trial, or other proceeding, summon any person as a witness, or examine any person in attendance, though not summoned as a witness, or recall and re-examine any person already examined. This section gives the court wide powers to ensure that all relevant evidence is brought before it.",
            "title": "CrPC Section 540 - Power to Summon Witnesses",
            "source": "crpc_section_540"
        },
        {
            "text": "Section 561-A CrPC - Saving of inherent power of High Court. Nothing in this Code shall be deemed to limit or affect the inherent power of the High Court to make such orders as may be necessary to give effect to any order under this Code, or to prevent abuse of the process of any court, or otherwise to secure the ends of justice. This section gives the High Court wide powers to prevent abuse of process and ensure justice.",
            "title": "CrPC Section 561-A - Inherent Powers of High Court",
            "source": "crpc_section_561a"
        },
    ]
    
    print(f"   ✅ Created {len(crpc_sections)} CrPC sections")
    return crpc_sections

def create_constitution_articles() -> List[Dict]:
    """Create Constitution articles relevant to criminal law"""
    print("📚 Creating Constitution articles corpus...")
    
    constitution_articles = [
        {
            "text": "Article 4 of the Constitution of Pakistan - Right of individuals to be dealt with in accordance with law. To enjoy the protection of law and to be treated in accordance with law is the inalienable right of every citizen, wherever he may be, and of every other person for the time being within Pakistan. In particular, no action detrimental to the life, liberty, body, reputation, or property of any person shall be taken except in accordance with law. This article guarantees fundamental rights and due process.",
            "title": "Constitution Article 4 - Right to be Dealt with According to Law",
            "source": "constitution_article_4"
        },
        {
            "text": "Article 9 of the Constitution of Pakistan - Security of person. No person shall be deprived of life or liberty save in accordance with law. This article guarantees the fundamental right to life and liberty. Any deprivation of life or liberty must be in accordance with law, meaning through proper legal procedures. This is a fundamental right that cannot be suspended except during emergency.",
            "title": "Constitution Article 9 - Security of Person",
            "source": "constitution_article_9"
        },
        {
            "text": "Article 10 of the Constitution of Pakistan - Safeguards as to arrest and detention. No person who is arrested shall be detained in custody without being informed, as soon as may be, of the grounds for such arrest, nor shall he be denied the right to consult and be defended by a legal practitioner of his choice. Every person who is arrested and detained in custody shall be produced before a Magistrate within a period of twenty-four hours of such arrest, excluding the time necessary for the journey from the place of arrest to the court of the nearest Magistrate. No such person shall be detained in custody beyond the said period without the authority of a Magistrate.",
            "title": "Constitution Article 10 - Safeguards for Arrest and Detention",
            "source": "constitution_article_10"
        },
        {
            "text": "Article 10-A of the Constitution of Pakistan - Right to fair trial. For the determination of his civil rights and obligations or in a criminal charge, a person shall be entitled to a fair trial and due process. This article guarantees the right to a fair trial, which includes the right to be heard, right to legal representation, right to present evidence, and right to be tried by an impartial tribunal.",
            "title": "Constitution Article 10-A - Right to Fair Trial",
            "source": "constitution_article_10a"
        },
        {
            "text": "Article 13 of the Constitution of Pakistan - Protection against double punishment and self-incrimination. No person shall be prosecuted or punished for the same offence more than once. No person shall, when accused of an offence, be compelled to be a witness against himself. This article protects against double jeopardy and self-incrimination.",
            "title": "Constitution Article 13 - Protection Against Double Jeopardy",
            "source": "constitution_article_13"
        },
        {
            "text": "Article 14 of the Constitution of Pakistan - Inviolability of dignity of man. The dignity of man and, subject to law, the privacy of home, shall be inviolable. This article protects human dignity and privacy. It ensures that individuals are treated with respect and that their privacy is protected, subject to lawful restrictions.",
            "title": "Constitution Article 14 - Dignity and Privacy",
            "source": "constitution_article_14"
        },
    ]
    
    print(f"   ✅ Created {len(constitution_articles)} Constitution articles")
    return constitution_articles

def create_legal_definitions() -> List[Dict]:
    """Create legal definitions and explanations"""
    print("📚 Creating legal definitions corpus...")
    
    definitions = [
        {
            "text": "Cognizable Offence - A cognizable offence is one in which a police officer may arrest without a warrant and investigate without the permission of a court. Examples include murder, rape, robbery, theft (if value exceeds threshold), and dacoity. For cognizable offences, the police can start investigation immediately upon receiving information.",
            "title": "Cognizable Offence - Definition",
            "source": "legal_definition_cognizable"
        },
        {
            "text": "Non-Cognizable Offence - A non-cognizable offence is one in which a police officer cannot arrest without a warrant and cannot investigate without the order of a Magistrate. Examples include simple hurt, defamation, and cheating (in some cases). The police must obtain permission from a Magistrate before investigating non-cognizable offences.",
            "title": "Non-Cognizable Offence - Definition",
            "source": "legal_definition_non_cognizable"
        },
        {
            "text": "Bailable Offence - A bailable offence is one in which bail is a matter of right. The accused can be released on bail by the police or court upon furnishing surety. Examples include simple hurt, defamation, and some cases of theft (if value is below threshold). The accused has a right to bail in bailable offences.",
            "title": "Bailable Offence - Definition",
            "source": "legal_definition_bailable"
        },
        {
            "text": "Non-Bailable Offence - A non-bailable offence is one in which bail is not a matter of right but a matter of discretion of the court. The court may grant or refuse bail based on the facts and circumstances of the case. Examples include murder, rape, robbery, dacoity, and theft with preparation. The court has discretion to grant bail in non-bailable offences under Section 497 CrPC.",
            "title": "Non-Bailable Offence - Definition",
            "source": "legal_definition_non_bailable"
        },
        {
            "text": "FIR (First Information Report) - The FIR is the first information given to the police about the commission of a cognizable offence. It must be registered immediately under Section 154 CrPC. The FIR sets the criminal law in motion and is crucial evidence in criminal cases. Delay in FIR registration can be fatal to the prosecution case unless properly explained.",
            "title": "FIR - First Information Report",
            "source": "legal_definition_fir"
        },
        {
            "text": "Remand - Remand is the authorization by a Magistrate to keep an accused in police custody for investigation. Under Section 167 CrPC, a Magistrate can authorize detention for up to 15 days (or 90 days for serious offences). After the remand period, the accused must be produced before the court and either released on bail or sent to judicial lockup.",
            "title": "Remand - Definition",
            "source": "legal_definition_remand"
        },
        {
            "text": "Bail - Bail is the release of an accused person from custody upon furnishing surety or personal bond, with the condition that he will appear before the court when required. In bailable offences, bail is a right. In non-bailable offences, bail is discretionary and depends on factors like nature of offence, evidence, and likelihood of absconding.",
            "title": "Bail - Definition",
            "source": "legal_definition_bail"
        },
        {
            "text": "Confession - A confession is an admission of guilt made by an accused person. Under Section 164 CrPC, confessions must be recorded by a Magistrate and must be voluntary. Confessions made to police are not admissible in evidence. Only confessions recorded by a Magistrate under Section 164 CrPC are admissible.",
            "title": "Confession - Definition",
            "source": "legal_definition_confession"
        },
        {
            "text": "Common Intention - Common intention under Section 34 PPC means a pre-arranged plan or prior meeting of minds to commit an offence. When several persons commit an offence in furtherance of common intention, each is liable as if he committed it alone. Common intention must be proved beyond reasonable doubt and cannot be inferred from mere presence.",
            "title": "Common Intention - Definition",
            "source": "legal_definition_common_intention"
        },
        {
            "text": "Qatl-i-amd (Murder) - Qatl-i-amd is intentional killing defined under Section 300 PPC. It requires intention to cause death or such bodily injury as is likely to cause death. The punishment is death or imprisonment for life under Section 302 PPC. It is the most serious form of homicide and is non-bailable and cognizable.",
            "title": "Qatl-i-amd (Murder) - Definition",
            "source": "legal_definition_qatl_amd"
        },
    ]
    
    print(f"   ✅ Created {len(definitions)} legal definitions")
    return definitions

def create_best_rag_corpus():
    """Create comprehensive RAG corpus"""
    print("=" * 60)
    print("CREATING BEST RAG CORPUS FOR PAKISTAN CRIMINAL LAW")
    print("=" * 60)
    print()
    
    output_path = Path("data/processed/full_rag_corpus.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    all_docs = []
    
    # Create all sections
    print("🔄 Building comprehensive corpus...\n")
    all_docs.extend(create_ppc_sections())
    all_docs.extend(create_crpc_sections())
    all_docs.extend(create_constitution_articles())
    all_docs.extend(create_legal_definitions())
    
    # Save corpus
    print(f"\n💾 Saving corpus to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_docs, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Corpus saved!")
    print(f"   Location: {output_path}")
    print(f"   Total documents: {len(all_docs)}")
    
    # Statistics
    print("\n📊 Corpus Statistics:")
    ppc_count = sum(1 for doc in all_docs if 'ppc' in doc.get('source', '').lower())
    crpc_count = sum(1 for doc in all_docs if 'crpc' in doc.get('source', '').lower())
    constitution_count = sum(1 for doc in all_docs if 'constitution' in doc.get('source', '').lower())
    definition_count = sum(1 for doc in all_docs if 'definition' in doc.get('source', '').lower())
    
    print(f"   PPC sections: {ppc_count}")
    print(f"   CrPC sections: {crpc_count}")
    print(f"   Constitution articles: {constitution_count}")
    print(f"   Legal definitions: {definition_count}")
    print(f"   Total: {len(all_docs)} documents")
    
    print("\n" + "=" * 60)
    print("✅ BEST RAG CORPUS CREATED!")
    print("=" * 60)
    print()
    print("📝 Next steps:")
    print("   1. Run: python clean_rag_corpus.py")
    print("   2. Test: python test_chatbot_v5.py")
    print()
    print("💡 This corpus includes:")
    print("   ✅ Essential PPC sections (murder, rape, theft, robbery, etc.)")
    print("   ✅ Important CrPC sections (FIR, bail, remand, confessions)")
    print("   ✅ Constitution articles (rights during arrest, fair trial)")
    print("   ✅ Legal definitions (cognizable, bailable, etc.)")

if __name__ == "__main__":
    create_best_rag_corpus()

