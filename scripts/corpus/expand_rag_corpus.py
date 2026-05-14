"""
Expand RAG Corpus - Add More PPC, CrPC Sections and Legal Knowledge
This script adds many more sections to create a comprehensive corpus
"""
import json
from pathlib import Path
from typing import List, Dict

def add_more_ppc_sections() -> List[Dict]:
    """Add many more PPC sections"""
    print("📚 Adding more PPC sections...")
    
    additional_ppc = [
        {
            "text": "Section 304 PPC - Punishment for qatl-i-khata (culpable homicide). Whoever commits qatl-i-khata shall be punished with imprisonment of either description for a term which may extend to ten years, and shall also be liable to fine. Qatl-i-khata is causing death by doing an act with the knowledge that it is likely to cause death but without intention. This is a non-bailable and cognizable offence. The key difference from murder is the absence of intention to cause death.",
            "title": "PPC Section 304 - Culpable Homicide (Qatl-i-khata)",
            "source": "ppc_section_304"
        },
        {
            "text": "Section 307 PPC - Attempt to commit qatl-i-khata. Whoever attempts to commit qatl-i-khata shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine. This is a non-bailable and cognizable offence. An attempt requires some act towards commission of the offence.",
            "title": "PPC Section 307 - Attempt to Commit Culpable Homicide",
            "source": "ppc_section_307"
        },
        {
            "text": "Section 338 PPC - Causing hurt by means of poison. Whoever causes hurt to any person by means of any poison or any stupefying, intoxicating, or unwholesome drug, or by means of any other thing with intent to commit or facilitate the commission of an offence, shall be punished with imprisonment of either description for a term which may extend to ten years, and shall also be liable to fine. This is a non-bailable and cognizable offence.",
            "title": "PPC Section 338 - Causing Hurt by Poison",
            "source": "ppc_section_338"
        },
        {
            "text": "Section 339 PPC - Wrongful restraint. Whoever voluntarily obstructs any person so as to prevent that person from proceeding in any direction in which that person has a right to proceed, is said wrongfully to restrain that person. The punishment is imprisonment up to one month or fine up to five hundred rupees. This is a bailable and cognizable offence.",
            "title": "PPC Section 339 - Wrongful Restraint",
            "source": "ppc_section_339"
        },
        {
            "text": "Section 340 PPC - Wrongful confinement. Whoever wrongfully restrains any person in such a manner as to prevent that person from proceeding beyond certain circumscribing limits, is said wrongfully to confine that person. The punishment is imprisonment up to one year or fine up to one thousand rupees. This is a bailable and cognizable offence.",
            "title": "PPC Section 340 - Wrongful Confinement",
            "source": "ppc_section_340"
        },
        {
            "text": "Section 352 PPC - Assault. Whoever makes any gesture, or any preparation, intending or knowing it to be likely that such gesture or preparation will cause any person present to apprehend that he who makes that gesture or preparation is about to use criminal force to that person, is said to commit an assault. The punishment is imprisonment up to three months or fine up to five hundred rupees. This is a bailable and cognizable offence.",
            "title": "PPC Section 352 - Assault",
            "source": "ppc_section_352"
        },
        {
            "text": "Section 354 PPC - Assault or criminal force to woman with intent to outrage her modesty. Whoever assaults or uses criminal force to any woman, intending to outrage or knowing it to be likely that he will thereby outrage her modesty, shall be punished with imprisonment of either description for a term which may extend to two years, or with fine, or with both. This is a non-bailable and cognizable offence.",
            "title": "PPC Section 354 - Assault to Outrage Modesty",
            "source": "ppc_section_354"
        },
        {
            "text": "Section 363 PPC - Kidnapping. Whoever kidnaps any person from Pakistan or from lawful guardianship, shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine. Kidnapping means taking away a person by force or fraud. This is a non-bailable and cognizable offence.",
            "title": "PPC Section 363 - Kidnapping",
            "source": "ppc_section_363"
        },
        {
            "text": "Section 364 PPC - Kidnapping or abducting in order to murder. Whoever kidnaps or abducts any person in order that such person may be murdered or may be so disposed of as to be put in danger of being murdered, shall be punished with imprisonment for life, or with rigorous imprisonment for a term which may extend to ten years, and shall also be liable to fine. This is a non-bailable and cognizable offence.",
            "title": "PPC Section 364 - Kidnapping to Murder",
            "source": "ppc_section_364"
        },
        {
            "text": "Section 365 PPC - Kidnapping or abducting with intent secretly and wrongfully to confine person. Whoever kidnaps or abducts any person with intent to cause that person to be secretly and wrongfully confined, shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine. This is a non-bailable and cognizable offence.",
            "title": "PPC Section 365 - Kidnapping to Confine",
            "source": "ppc_section_365"
        },
        {
            "text": "Section 366 PPC - Kidnapping, abducting or inducing woman to compel her marriage. Whoever kidnaps or abducts any woman with intent that she may be compelled, or knowing it to be likely that she will be compelled, to marry any person against her will, or in order that she may be forced or seduced to illicit intercourse, shall be punished with imprisonment of either description for a term which may extend to ten years, and shall also be liable to fine. This is a non-bailable and cognizable offence.",
            "title": "PPC Section 366 - Kidnapping Woman to Compel Marriage",
            "source": "ppc_section_366"
        },
        {
            "text": "Section 377 PPC - Unnatural offences. Whoever voluntarily has carnal intercourse against the order of nature with any man, woman, or animal, shall be punished with imprisonment for life, or with imprisonment of either description for a term which may extend to ten years, and shall also be liable to fine. This is a non-bailable and cognizable offence.",
            "title": "PPC Section 377 - Unnatural Offences",
            "source": "ppc_section_377"
        },
        {
            "text": "Section 380 PPC - Theft in dwelling house. Whoever commits theft in any building, tent, or vessel, which building, tent, or vessel is used as a human dwelling, or used for the custody of property, shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine. This is a non-bailable and cognizable offence.",
            "title": "PPC Section 380 - Theft in Dwelling House",
            "source": "ppc_section_380"
        },
        {
            "text": "Section 384 PPC - Extortion. Whoever intentionally puts any person in fear of any injury to that person, or to any other, and thereby dishonestly induces the person so put in fear to deliver to any person any property or valuable security, or anything signed or sealed which may be converted into a valuable security, commits extortion. The punishment is imprisonment up to three years or fine or both. This is a non-bailable and cognizable offence.",
            "title": "PPC Section 384 - Extortion",
            "source": "ppc_section_384"
        },
        {
            "text": "Section 394 PPC - Voluntarily causing hurt in committing robbery. If any person, in committing or in attempting to commit robbery, voluntarily causes hurt, such person, and any other person jointly concerned in committing or attempting to commit such robbery, shall be punished with imprisonment for life, or with rigorous imprisonment for a term which may extend to ten years, and shall also be liable to fine. This is a non-bailable and cognizable offence.",
            "title": "PPC Section 394 - Hurt in Robbery",
            "source": "ppc_section_394"
        },
        {
            "text": "Section 396 PPC - Dacoity with murder. If any one of five or more persons, who are conjointly committing dacoity, commits murder in so committing dacoity, every one of those persons shall be punished with death, or imprisonment for life, or with rigorous imprisonment for a term which may extend to ten years, and shall also be liable to fine. This is a non-bailable and cognizable offence.",
            "title": "PPC Section 396 - Dacoity with Murder",
            "source": "ppc_section_396"
        },
        {
            "text": "Section 397 PPC - Robbery or dacoity with attempt to cause death or grievous hurt. If, at the time of committing robbery or dacoity, the offender uses any deadly weapon, or causes grievous hurt to any person, or attempts to cause death or grievous hurt to any person, the imprisonment with which such offender shall be punished shall not be less than seven years. This is a non-bailable and cognizable offence.",
            "title": "PPC Section 397 - Robbery/Dacoity with Deadly Weapon",
            "source": "ppc_section_397"
        },
        {
            "text": "Section 403 PPC - Dishonest misappropriation of property. Whoever dishonestly misappropriates or converts to his own use any moveable property, shall be punished with imprisonment of either description for a term which may extend to two years, or with fine, or with both. This is a bailable and cognizable offence.",
            "title": "PPC Section 403 - Dishonest Misappropriation",
            "source": "ppc_section_403"
        },
        {
            "text": "Section 405 PPC - Criminal breach of trust. Whoever, being in any manner entrusted with property, or with any dominion over property, dishonestly misappropriates or converts to his own use that property, or dishonestly uses or disposes of that property in violation of any direction of law, or of any legal contract, commits criminal breach of trust. The punishment varies based on value of property. This is a non-bailable and cognizable offence.",
            "title": "PPC Section 405 - Criminal Breach of Trust",
            "source": "ppc_section_405"
        },
        {
            "text": "Section 406 PPC - Punishment for criminal breach of trust. Whoever commits criminal breach of trust shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both. If the value exceeds certain threshold, the punishment is more severe. This is a non-bailable and cognizable offence.",
            "title": "PPC Section 406 - Punishment for Breach of Trust",
            "source": "ppc_section_406"
        },
        {
            "text": "Section 415 PPC - Cheating. Whoever, by deceiving any person, fraudulently or dishonestly induces the person so deceived to deliver any property to any person, or to consent that any person shall retain any property, or intentionally induces the person so deceived to do or omit to do anything which he would not do or omit if he were not so deceived, and which act or omission causes or is likely to cause damage or harm to that person in body, mind, reputation, or property, is said to cheat.",
            "title": "PPC Section 415 - Definition of Cheating",
            "source": "ppc_section_415"
        },
        {
            "text": "Section 417 PPC - Punishment for cheating. Whoever cheats shall be punished with imprisonment of either description for a term which may extend to one year, or with fine, or with both. This is a bailable and cognizable offence. The punishment is enhanced under Section 420 if property is delivered.",
            "title": "PPC Section 417 - Punishment for Cheating",
            "source": "ppc_section_417"
        },
        {
            "text": "Section 441 PPC - Criminal trespass. Whoever enters into or upon property in the possession of another with intent to commit an offence or to intimidate, insult, or annoy any person in possession of such property, or having lawfully entered into or upon such property, unlawfully remains there with intent to intimidate, insult, or annoy any such person, or with intent to commit an offence, is said to commit criminal trespass.",
            "title": "PPC Section 441 - Criminal Trespass",
            "source": "ppc_section_441"
        },
        {
            "text": "Section 447 PPC - Punishment for criminal trespass. Whoever commits criminal trespass shall be punished with imprisonment of either description for a term which may extend to three months, or with fine which may extend to one thousand five hundred rupees, or with both. This is a bailable and cognizable offence.",
            "title": "PPC Section 447 - Punishment for Criminal Trespass",
            "source": "ppc_section_447"
        },
        {
            "text": "Section 448 PPC - House-trespass. Whoever commits criminal trespass by entering into or remaining in any building, tent, or vessel used as a human dwelling, or any building used as a place for worship, or as a place for the custody of property, is said to commit house-trespass. The punishment is imprisonment up to one year or fine up to one thousand rupees. This is a bailable and cognizable offence.",
            "title": "PPC Section 448 - House-Trespass",
            "source": "ppc_section_448"
        },
        {
            "text": "Section 449 PPC - House-trespass in order to commit offence. Whoever commits house-trespass in order to the committing of any offence punishable with death, shall be punished with imprisonment for life, or with rigorous imprisonment for a term which may extend to ten years, and shall also be liable to fine. This is a non-bailable and cognizable offence.",
            "title": "PPC Section 449 - House-Trespass to Commit Offence",
            "source": "ppc_section_449"
        },
        {
            "text": "Section 452 PPC - House-trespass after preparation for hurt, assault, or wrongful restraint. Whoever commits house-trespass, having made preparation for causing hurt to any person, or for assaulting any person, or for wrongfully restraining any person, or for putting any person in fear of hurt, or of assault, or of wrongful restraint, shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine. This is a non-bailable and cognizable offence.",
            "title": "PPC Section 452 - House-Trespass with Preparation",
            "source": "ppc_section_452"
        },
        {
            "text": "Section 457 PPC - Lurking house-trespass or house-breaking by night. Whoever commits lurking house-trespass, or house-breaking, by night, shall be punished with imprisonment of either description for a term which may extend to fourteen years, and shall also be liable to fine. This is a non-bailable and cognizable offence. Night means the period between sunset and sunrise.",
            "title": "PPC Section 457 - House-Breaking by Night",
            "source": "ppc_section_457"
        },
        {
            "text": "Section 489 PPC - Counterfeiting currency notes or bank notes. Whoever counterfeits, or knowingly performs any part of the process of counterfeiting, any currency note or bank note, shall be punished with imprisonment for life, or with imprisonment of either description for a term which may extend to ten years, and shall also be liable to fine. This is a non-bailable and cognizable offence.",
            "title": "PPC Section 489 - Counterfeiting Currency",
            "source": "ppc_section_489"
        },
        {
            "text": "Section 493 PPC - Cohabitation caused by a man deceitfully inducing a belief of lawful marriage. Every man who by deceit causes any woman who is not lawfully married to him to believe that she is lawfully married to him and to cohabit with him in that belief, shall be punished with imprisonment of either description for a term which may extend to ten years, and shall also be liable to fine. This is a non-bailable and cognizable offence.",
            "title": "PPC Section 493 - Deceitful Cohabitation",
            "source": "ppc_section_493"
        },
        {
            "text": "Section 496 PPC - Marriage ceremony fraudulently gone through without lawful marriage. Whoever, dishonestly or with a fraudulent intention, goes through the ceremony of being married, knowing that he is not thereby lawfully married, shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine. This is a non-bailable and cognizable offence.",
            "title": "PPC Section 496 - Fraudulent Marriage",
            "source": "ppc_section_496"
        },
        {
            "text": "Section 498 PPC - Enticing or taking away or detaining with criminal intent a married woman. Whoever takes or entices away any woman who is and whom he knows or has reason to believe to be the wife of any other man, from that man, or from any person having the care of her on behalf of that man, with intent that she may have illicit intercourse with any person, or conceals or detains with that intent any such woman, shall be punished with imprisonment of either description for a term which may extend to two years, or with fine, or with both. This is a bailable and cognizable offence.",
            "title": "PPC Section 498 - Enticing Married Woman",
            "source": "ppc_section_498"
        },
        {
            "text": "Section 500 PPC - Defamation. Whoever defames another shall be punished with simple imprisonment for a term which may extend to two years, or with fine, or with both. Defamation means making or publishing any imputation concerning any person, intending to harm, or knowing or having reason to believe that such imputation will harm, the reputation of such person. This is a bailable and non-cognizable offence.",
            "title": "PPC Section 500 - Defamation",
            "source": "ppc_section_500"
        },
        {
            "text": "Section 503 PPC - Criminal intimidation. Whoever threatens another with any injury to his person, reputation, or property, or to the person or reputation of any one in whom that person is interested, with intent to cause alarm to that person, or to cause that person to do any act which he is not legally bound to do, or to omit to do any act which that person is legally entitled to do, as the means of avoiding the execution of such threat, commits criminal intimidation.",
            "title": "PPC Section 503 - Definition of Criminal Intimidation",
            "source": "ppc_section_503"
        },
        {
            "text": "Section 509 PPC - Word, gesture, or act intended to insult the modesty of a woman. Whoever, intending to insult the modesty of any woman, utters any word, makes any sound or gesture, or exhibits any object, intending that such word or sound shall be heard, or that such gesture or object shall be seen, by such woman, or intrudes upon the privacy of such woman, shall be punished with simple imprisonment for a term which may extend to three years, or with fine, or with both. This is a bailable and cognizable offence.",
            "title": "PPC Section 509 - Insulting Modesty of Woman",
            "source": "ppc_section_509"
        },
        {
            "text": "Section 34 PPC - Acts done by several persons in furtherance of common intention. When a criminal act is done by several persons in furtherance of the common intention of all, each of such persons is liable for that act in the same manner as if it were done by him alone. Common intention requires prior meeting of minds and pre-arranged plan. Mere presence at the scene is not enough. This section creates joint liability.",
            "title": "PPC Section 34 - Common Intention",
            "source": "ppc_section_34"
        },
        {
            "text": "Section 109 PPC - Punishment of abetment if the act abetted is committed in consequence and where no express provision is made for its punishment. Whoever abets any offence shall, if the act abetted is committed in consequence of the abetment, and no express provision is made by this Code for the punishment of such abetment, be punished with the punishment provided for the offence. Abetment means instigating, engaging in conspiracy, or intentionally aiding the commission of an offence.",
            "title": "PPC Section 109 - Abetment",
            "source": "ppc_section_109"
        },
    ]
    
    print(f"   ✅ Added {len(additional_ppc)} more PPC sections")
    return additional_ppc

def add_more_crpc_sections() -> List[Dict]:
    """Add more CrPC sections"""
    print("📚 Adding more CrPC sections...")
    
    additional_crpc = [
        {
            "text": "Section 156 CrPC - Police officer's power to investigate cognizable case. Any officer in charge of a police station may, without the order of a Magistrate, investigate any cognizable case which a court having jurisdiction over the local area within the limits of such station would have power to inquire into or try under the provisions of Chapter XV. The police can start investigation immediately upon receiving information about a cognizable offence.",
            "title": "CrPC Section 156 - Power to Investigate",
            "source": "crpc_section_156"
        },
        {
            "text": "Section 157 CrPC - Procedure for investigation. If, from information received or otherwise, an officer in charge of a police station has reason to suspect the commission of an offence which he is empowered to investigate, he shall forthwith send a report of the same to a Magistrate and proceed in person to the spot to investigate the facts and circumstances of the case. The police must investigate promptly and thoroughly.",
            "title": "CrPC Section 157 - Procedure for Investigation",
            "source": "crpc_section_157"
        },
        {
            "text": "Section 161 CrPC - Examination of witnesses by police. Any police officer making an investigation may examine orally any person supposed to be acquainted with the facts and circumstances of the case. Such person is bound to answer truly all questions relating to such case, but may refuse to answer questions which would have a tendency to expose him to a criminal charge. Statements to police are not signed and are not substantive evidence.",
            "title": "CrPC Section 161 - Examination of Witnesses",
            "source": "crpc_section_161"
        },
        {
            "text": "Section 162 CrPC - Statements to police not to be signed. No statement made by any person to a police officer in the course of an investigation shall, if reduced to writing, be signed by the person making it. Such statements can only be used to contradict the witness during trial. They cannot be used as substantive evidence. This prevents coercion and ensures voluntary statements.",
            "title": "CrPC Section 162 - Statements Not to be Signed",
            "source": "crpc_section_162"
        },
        {
            "text": "Section 190 CrPC - Cognizance of offences by Magistrates. Subject to the provisions of this Chapter, any Magistrate of the first class may take cognizance of any offence: (a) upon receiving a complaint of facts which constitute such offence; (b) upon a police report of such facts; (c) upon information received from any person other than a police officer, or upon his own knowledge, that such offence has been committed. The Magistrate takes cognizance based on complaint, police report, or information.",
            "title": "CrPC Section 190 - Cognizance of Offences",
            "source": "crpc_section_190"
        },
        {
            "text": "Section 200 CrPC - Examination of complainant. A Magistrate taking cognizance of an offence on complaint shall examine upon oath the complainant and the witnesses present, if any, and the substance of such examination shall be reduced to writing and shall be signed by the complainant and the witnesses, and also by the Magistrate. This ensures that the complaint is genuine and not frivolous.",
            "title": "CrPC Section 200 - Examination of Complainant",
            "source": "crpc_section_200"
        },
        {
            "text": "Section 204 CrPC - Issue of process. If in the opinion of a Magistrate taking cognizance of an offence there is sufficient ground for proceeding, and the case appears to be one in which, according to the fourth column of the Second Schedule, a summons should be issued, he shall issue his summons for the attendance of the accused. If the case appears to be one in which a warrant should be issued, he may issue a warrant. The Magistrate issues process if there is sufficient ground.",
            "title": "CrPC Section 204 - Issue of Process",
            "source": "crpc_section_204"
        },
        {
            "text": "Section 241 CrPC - Evidence for prosecution. If the accused pleads not guilty, the Magistrate shall proceed to hear the prosecution and take all such evidence as may be produced in support of the prosecution. The prosecution must prove its case beyond reasonable doubt. The accused has the right to cross-examine prosecution witnesses.",
            "title": "CrPC Section 241 - Evidence for Prosecution",
            "source": "crpc_section_241"
        },
        {
            "text": "Section 242 CrPC - Evidence for defence. The accused shall then be called upon to enter upon his defence and produce his evidence. If the accused applies to the Magistrate to issue any process for compelling the attendance of any witness, the Magistrate shall issue such process unless he considers that such application should be refused. The accused has the right to present defence evidence.",
            "title": "CrPC Section 242 - Evidence for Defence",
            "source": "crpc_section_242"
        },
        {
            "text": "Section 245 CrPC - Acquittal or conviction. If the Magistrate, upon taking the evidence, finds the accused not guilty, he shall record an order of acquittal. If the Magistrate finds the accused guilty, he shall pass sentence upon him according to law. The Magistrate must give reasons for acquittal or conviction. The accused can appeal against conviction.",
            "title": "CrPC Section 245 - Acquittal or Conviction",
            "source": "crpc_section_245"
        },
        {
            "text": "Section 426 CrPC - Suspension of sentence pending appeal. When an appeal has been filed, the Appellate Court may, for reasons to be recorded by it in writing, order that the execution of the sentence or order appealed against be suspended and, if the accused is in confinement, that he be released on bail or on his own bond. The Appellate Court can suspend sentence during appeal.",
            "title": "CrPC Section 426 - Suspension of Sentence",
            "source": "crpc_section_426"
        },
    ]
    
    print(f"   ✅ Added {len(additional_crpc)} more CrPC sections")
    return additional_crpc

def expand_corpus():
    """Expand existing corpus with more sections"""
    print("=" * 60)
    print("EXPANDING RAG CORPUS WITH MORE SECTIONS")
    print("=" * 60)
    print()
    
    # Load existing corpus if exists
    existing_path = Path("data/processed/full_rag_corpus.json")
    existing_corpus = []
    
    if existing_path.exists():
        print("📚 Loading existing corpus...")
        with open(existing_path, 'r', encoding='utf-8') as f:
            existing_corpus = json.load(f)
        print(f"   ✅ Loaded {len(existing_corpus)} existing documents")
    else:
        print("   ⚠️  No existing corpus found, creating new one...")
    
    # Add more sections
    print("\n🔄 Adding more sections...\n")
    all_docs = existing_corpus.copy()
    all_docs.extend(add_more_ppc_sections())
    all_docs.extend(add_more_crpc_sections())
    
    # Remove duplicates
    print("\n🧹 Removing duplicates...")
    seen = set()
    unique_docs = []
    for doc in all_docs:
        text_hash = hash(doc['text'][:500])
        if text_hash not in seen:
            seen.add(text_hash)
            unique_docs.append(doc)
    
    print(f"   ✅ Removed {len(all_docs) - len(unique_docs)} duplicates")
    print(f"   Final corpus: {len(unique_docs)} documents")
    
    # Save expanded corpus
    print(f"\n💾 Saving expanded corpus...")
    with open(existing_path, 'w', encoding='utf-8') as f:
        json.dump(unique_docs, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Expanded corpus saved!")
    print(f"   Location: {existing_path}")
    print(f"   Total documents: {len(unique_docs)}")
    
    # Statistics
    print("\n📊 Corpus Statistics:")
    ppc_count = sum(1 for doc in unique_docs if 'ppc' in doc.get('source', '').lower())
    crpc_count = sum(1 for doc in unique_docs if 'crpc' in doc.get('source', '').lower())
    constitution_count = sum(1 for doc in unique_docs if 'constitution' in doc.get('source', '').lower())
    definition_count = sum(1 for doc in unique_docs if 'definition' in doc.get('source', '').lower())
    article_count = sum(1 for doc in unique_docs if 'article' in doc.get('source', '').lower())
    
    print(f"   PPC sections: {ppc_count}")
    print(f"   CrPC sections: {crpc_count}")
    print(f"   Constitution articles: {constitution_count}")
    print(f"   Legal definitions: {definition_count}")
    print(f"   Legal articles: {article_count}")
    print(f"   Total: {len(unique_docs)} documents")
    
    print("\n" + "=" * 60)
    print("✅ CORPUS EXPANDED!")
    print("=" * 60)
    print("\n📝 Next steps:")
    print("   1. Run: python clean_rag_corpus.py")
    print("   2. Run: python scrape_online_legal_data.py (for even more data)")
    print("   3. Test: python test_chatbot_v5.py")

if __name__ == "__main__":
    expand_corpus()























