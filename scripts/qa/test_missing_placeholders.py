"""
Test document generation with missing data (some placeholders not filled)
"""
from src.document_generator import DocumentGenerator

print("=" * 70)
print("TESTING WITH MISSING PLACEHOLDERS")
print("=" * 70)

doc_gen = DocumentGenerator()

# Partial data - only some fields filled
partial_data = {
    "COURT_NAME": "Sessions Court",
    "CITY_DISTRICT": "Lahore",
    "CASE_TITLE": "Criminal Appeal",
    "APPLICANT_NAME": "Ahmed Khan",
    "RESPONDENT_NAME": "The State",
    # Missing many other fields like CASE_TITLE_2, CASE_TITLE_3, etc.
}

print(f"\nTest data has only {len(partial_data)} fields (many missing)")
print("\nGenerating document...")

try:
    result = doc_gen.fill_template(
        template_id="general/Consolidation of cases",
        data=partial_data,
        generate_ai_sections=False
    )

    print(f"\n✅ Document generated!")
    print(f"Output: {result['output_path']}")
    print("\n🎯 Unreplaced placeholders should be automatically removed!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("=" * 70)
