from src.document_generator import DocumentGenerator

doc_gen = DocumentGenerator()
print(f"Found {len(doc_gen.templates)} templates:\n")
for template_id in sorted(doc_gen.templates.keys()):
    print(f"  - {template_id}")
