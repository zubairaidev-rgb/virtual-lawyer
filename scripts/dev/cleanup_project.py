#!/usr/bin/env python3
"""
Project Cleanup Script
Safely deletes unnecessary files from the project while keeping essential functionality.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

_scripts_dir = Path(__file__).resolve().parents[1]
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))
from _repo import repo_root as _repo_root  # noqa: E402

# Files to delete - categorized
FILES_TO_DELETE = {
    # Documentation files (MD)
    "docs": [
        "ALL_BACKEND_FEATURES_SUMMARY.md",
        "API_DOCUMENTATION.md",
        "BACKEND_ANSWER_GENERATION.md",
        "BACKEND_FEATURES_COMPLETE_LIST.md",
        "CHATBOT_INTEGRATION_FIX.md",
        "COMPLETE_BACKEND_FEATURES.md",
        "CORRECT_TESTING_WORKFLOW.md",
        "DOCUMENT_FEATURES_GUIDE.md",
        "EMBEDDING_CACHE_FIX.md",
        "FINAL_INTEGRATION_COMPLETE.md",
        "FIX_FREEZING_ISSUE.md",
        "HOW_TO_TEST_DOCUMENT_FEATURES.md",
        "INSTALL_AND_RUN.md",
        "INSTALL_DOCUMENT_FEATURES.md",
        "INTEGRATION_COMPLETE.md",
        "MODEL_IMPROVEMENT_PLAN.md",
        "QUICK_REFERENCE.md",
        "QUICK_START_DOCUMENT_FEATURES.md",
        "QUICK_START.md",
        "QUICK_TEST_DOCUMENTS.md",
        "RAG_SYSTEM_IMPROVEMENTS.md",
        "README_COMPLETE.md",
        "SETUP_COMPLETE.md",
        "SOLUTION_FREEZING_ISSUE.md",
        "START_API.md",
        "START_HERE.md",
        "SYSTEM_FLOW.md",
        "TEST_DOCUMENTS_SUMMARY.md",
        "TROUBLESHOOTING_FREEZING_ISSUE.md",
        "VERIFICATION_REPORT.md",
    ],
    
    
    # Test files
    "tests": [
        "test_all_features.py",
        "test_api.py",
        "test_chatbot_v5.py",
        "test_dashboard_api.py",
        "test_groq_api.py",
        "test_multi_layer_pipeline.py",
        "test_rag_retrieval.py",
        "test_two_stage_pipeline.py",
        "test_results.json",
    ],
    
    # Other files
    "other": [
        "bash.exe.stackdump",
        "frontend.html"
    ]
}

# Essential files that should NEVER be deleted
ESSENTIAL_FILES = [
    "api_complete.py",
    "config.py",
    "requirements.txt",
    "requirements_api.txt",
    ".gitignore",
]

# Essential directories
ESSENTIAL_DIRS = [
    "src",
    "scripts",
    "Lawmate",
    "venv",
]


def get_project_root():
    """Get the project root directory"""
    return _repo_root()


def check_essential_files():
    """Check if essential files exist"""
    root = get_project_root()
    missing = []
    
    for file in ESSENTIAL_FILES:
        if not (root / file).exists():
            missing.append(file)
    
    for dir_name in ESSENTIAL_DIRS:
        if not (root / dir_name).exists():
            missing.append(f"{dir_name}/")
    
    return missing


def collect_files_to_delete():
    """Collect all files that should be deleted"""
    root = get_project_root()
    files_to_delete = []
    
    for category, file_list in FILES_TO_DELETE.items():
        for filename in file_list:
            file_path = root / filename
            if file_path.exists():
                files_to_delete.append((file_path, category))
    
    return files_to_delete


def delete_files(files, dry_run=False):
    """Delete files (or simulate if dry_run=True)"""
    root = get_project_root()
    deleted = []
    errors = []
    
    for file_path, category in files:
        try:
            if dry_run:
                print(f"  [DRY RUN] Would delete: {file_path.name} ({category})")
                deleted.append((file_path, category))
            else:
                if file_path.is_file():
                    file_path.unlink()
                    print(f"  [OK] Deleted: {file_path.name} ({category})")
                    deleted.append((file_path, category))
                elif file_path.is_dir():
                    import shutil
                    shutil.rmtree(file_path)
                    print(f"  [OK] Deleted directory: {file_path.name} ({category})")
                    deleted.append((file_path, category))
        except Exception as e:
            error_msg = f"  [X] Error deleting {file_path.name}: {str(e)}"
            print(error_msg)
            errors.append((file_path, str(e)))
    
    return deleted, errors


def create_deletion_log(deleted_files):
    """Create a log file of deleted files"""
    root = get_project_root()
    log_file = root / f"deletion_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(log_file, 'w') as f:
        f.write(f"Project Cleanup Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Total files deleted: {len(deleted_files)}\n\n")
        
        # Group by category
        by_category = {}
        for file_path, category in deleted_files:
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(file_path.name)
        
        for category, files in by_category.items():
            f.write(f"\n{category.upper()} ({len(files)} files):\n")
            for filename in sorted(files):
                f.write(f"  - {filename}\n")
    
    return log_file


def main():
    """Main cleanup function"""
    print("=" * 60)
    print("PROJECT CLEANUP SCRIPT")
    print("=" * 60)
    print()
    
    # Check essential files
    print("[*] Checking essential files...")
    missing = check_essential_files()
    if missing:
        print("  [!] WARNING: Some essential files/directories are missing:")
        for item in missing:
            print(f"     - {item}")
        response = input("\n  Continue anyway? (yes/no): ").lower()
        if response != 'yes':
            print("  [X] Aborted. Please ensure essential files exist.")
            return
    else:
        print("  [OK] All essential files found")
    
    print()
    
    # Collect files to delete
    print("[*] Scanning for files to delete...")
    files_to_delete = collect_files_to_delete()
    
    if not files_to_delete:
        print("  [OK] No files found to delete. Project is already clean!")
        return
    
    # Group by category
    by_category = {}
    for file_path, category in files_to_delete:
        if category not in by_category:
            by_category[category] = []
        by_category[category].append((file_path, category))
    
    # Show summary
    print(f"\n[*] Found {len(files_to_delete)} files to delete:\n")
    for category, files in by_category.items():
        print(f"  {category.upper()}: {len(files)} files")
    
    print()
    
    # Dry run
    print("[DRY RUN] Files that will be deleted:\n")
    deleted_dry, _ = delete_files(files_to_delete, dry_run=True)
    print()
    
    # Confirmation
    print("=" * 60)
    response = input(f"[!] Delete {len(files_to_delete)} files? (yes/no): ").lower()
    
    if response != 'yes':
        print("  [X] Cleanup cancelled.")
        return
    
    print()
    print("[*] Deleting files...\n")
    
    # Actually delete
    deleted, errors = delete_files(files_to_delete, dry_run=False)
    
    print()
    print("=" * 60)
    print("CLEANUP SUMMARY")
    print("=" * 60)
    print(f"  [OK] Successfully deleted: {len(deleted)} files")
    if errors:
        print(f"  [X] Errors: {len(errors)} files")
    
    # Create log
    if deleted:
        log_file = create_deletion_log(deleted)
        print(f"\n  [*] Deletion log saved to: {log_file.name}")
    
    print()
    print("[OK] Cleanup complete!")
    print()
    print("Next steps:")
    print("  1. Test your API: python api_complete.py")
    print("  2. Verify frontend still works")
    print("  3. Review deletion log if needed")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[X] Cleanup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[X] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

