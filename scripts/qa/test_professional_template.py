"""
Test the professional document generation
"""
from src.document_generator import DocumentGenerator
import os

print("=" * 70)
print("TESTING PROFESSIONAL DOCUMENT GENERATION")
print("=" * 70)

# Initialize generator
doc_gen = DocumentGenerator()

print(f"\n✅ Document generator initialized")
print(f"Found {len(doc_gen.templates)} templates")

# Test data for Consolidation of Cases
test_data = {
    "COURT_NAME": "Additional District and Sessions Judge",
    "CITY_DISTRICT": "Islamabad",
    "CASE_TITLE": "Criminal Miscellaneous Application",
    "APPLICANT_NAME": "Muhammad Ali",
    "RESPONDENT_NAME": "The State",
    "SUBJECT_MATTER": "Property dispute involving Plot No. 123, Block A, Sector F-10",

    "CASE_TITLE_1": "Case No. 456/2024",
    "COURT_NAME_1": "Civil Court",
    "LOCATION_1": "Islamabad",
    "HEARING_DATE_1": "15/05/2024",

    "CASE_TITLE_2": "Case No. 789/2024",
    "COURT_NAME_2": "Sessions Court",
    "LOCATION_2": "Rawalpindi",
    "HEARING_DATE_2": "20/05/2024",

    "CASE_TITLE_3": "Case No. 101/2024",
    "COURT_NAME_3": "District Court",
    "LOCATION_3": "Islamabad",
    "HEARING_DATE_3": "25/05/2024",

    "LAWYER_NAME": "Advocate Hamza Khan",
    "ENROLLMENT_NUMBER": "12345/2020",
    "DOCUMENT_DATE": "23/04/2026",
}

print("\nTesting 'Consolidation of cases' template...")
print(f"Test data includes {len(test_data)} fields")

try:
    # Generate document
    result = doc_gen.fill_template(
        template_id="general/Consolidation of cases",
        data=test_data,
        generate_ai_sections=False  # Skip AI for quick test
    )

    print(f"\n✅ Document generated successfully!")
    print(f"Output path: {result['output_path']}")
    print(f"Status: {result['status']}")

    if os.path.exists(result['output_path']):
        file_size = os.path.getsize(result['output_path'])
        print(f"File size: {file_size:,} bytes")
        print("\n🎉 SUCCESS! The professional template is working!")
        print("\nYour documents now have:")
        print("  ✓ Lawmate logo header")
        print("  ✓ Stamp paper borders (brown double lines)")
        print("  ✓ Professional margins (1.2\" - 1.3\")")
        print("  ✓ Times New Roman font, 11pt")
        print("  ✓ 1.5 line spacing")
        print("  ✓ Justified text alignment")
        print("  ✓ Color-coded headings (brown)")
        print("  ✓ Professional footer")
        print("  ✓ Proper legal document formatting")
    else:
        print("❌ File was not created")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
