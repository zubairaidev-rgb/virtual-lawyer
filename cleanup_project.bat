@echo off
REM Project Cleanup Script for Windows
REM This script deletes unnecessary files from the project

echo ============================================================
echo PROJECT CLEANUP SCRIPT (Windows Batch)
echo ============================================================
echo.
echo This will delete 72+ unnecessary files.
echo.
pause

echo.
echo [*] Starting cleanup...
echo.

REM Delete documentation files
echo [*] Deleting documentation files...
del /Q "ALL_BACKEND_FEATURES_SUMMARY.md" 2>nul
del /Q "API_DOCUMENTATION.md" 2>nul
del /Q "BACKEND_ANSWER_GENERATION.md" 2>nul
del /Q "BACKEND_FEATURES_COMPLETE_LIST.md" 2>nul
del /Q "CHATBOT_INTEGRATION_FIX.md" 2>nul
del /Q "COMPLETE_BACKEND_FEATURES.md" 2>nul
del /Q "CORRECT_TESTING_WORKFLOW.md" 2>nul
del /Q "DOCUMENT_FEATURES_GUIDE.md" 2>nul
del /Q "EMBEDDING_CACHE_FIX.md" 2>nul
del /Q "FINAL_INTEGRATION_COMPLETE.md" 2>nul
del /Q "FIX_FREEZING_ISSUE.md" 2>nul
del /Q "HOW_TO_TEST_DOCUMENT_FEATURES.md" 2>nul
del /Q "INSTALL_AND_RUN.md" 2>nul
del /Q "INSTALL_DOCUMENT_FEATURES.md" 2>nul
del /Q "INTEGRATION_COMPLETE.md" 2>nul
del /Q "MODEL_IMPROVEMENT_PLAN.md" 2>nul
del /Q "QUICK_REFERENCE.md" 2>nul
del /Q "QUICK_START_DOCUMENT_FEATURES.md" 2>nul
del /Q "QUICK_START.md" 2>nul
del /Q "QUICK_TEST_DOCUMENTS.md" 2>nul
del /Q "RAG_SYSTEM_IMPROVEMENTS.md" 2>nul
del /Q "README_COMPLETE.md" 2>nul
del /Q "SETUP_COMPLETE.md" 2>nul
del /Q "SOLUTION_FREEZING_ISSUE.md" 2>nul
del /Q "START_API.md" 2>nul
del /Q "START_HERE.md" 2>nul
del /Q "SYSTEM_FLOW.md" 2>nul
del /Q "TEST_DOCUMENTS_SUMMARY.md" 2>nul
del /Q "TROUBLESHOOTING_FREEZING_ISSUE.md" 2>nul
del /Q "VERIFICATION_REPORT.md" 2>nul

REM Delete one-time processing scripts (under scripts\corpus, scripts\training, scripts\dev)
echo [*] Deleting one-time processing scripts...
del /Q "scripts\corpus\add_evidence_priority_to_rag.py" 2>nul
del /Q "scripts\corpus\add_evidence_to_multisource_rag.py" 2>nul
del /Q "scripts\corpus\add_witness_credibility_to_rag.py" 2>nul
del /Q "scripts\training\add_witness_credibility_to_training.py" 2>nul
del /Q "scripts\corpus\build_complete_rag_system.py" 2>nul
del /Q "scripts\corpus\clean_rag_corpus.py" 2>nul
del /Q "scripts\corpus\create_best_rag_corpus.py" 2>nul
del /Q "scripts\corpus\create_crpc_constitution_json.py" 2>nul
del /Q "scripts\training\create_golden_training_data.py" 2>nul
del /Q "scripts\qa\diagnose_document_testing.py" 2>nul
del /Q "scripts\corpus\expand_rag_corpus.py" 2>nul
del /Q "scripts\dev\fix_adapter_config_v5.py" 2>nul
del /Q "scripts\dev\install_pdf_dependencies.py" 2>nul
del /Q "scripts\corpus\merge_all_rag_corpus.py" 2>nul
del /Q "scripts\dev\PRE_DOWNLOAD_MODEL_TO_DRIVE.py" 2>nul
del /Q "scripts\corpus\process_new_pdfs_to_rag.py" 2>nul
del /Q "scripts\corpus\process_ppc_pdf_to_json.py" 2>nul
del /Q "scripts\corpus\process_shc_cases_to_rag.py" 2>nul
del /Q "scripts\corpus\process_structured_data_to_rag.py" 2>nul
del /Q "scripts\dev\PRODUCTION_PIPELINE.py" 2>nul
del /Q "scripts\corpus\rebuild_rag_corpus.py" 2>nul
del /Q "scripts\corpus\scrape_online_legal_data.py" 2>nul
del /Q "scripts\corpus\scraper.py" 2>nul
del /Q "scripts\dev\setup_venv.py" 2>nul

REM Delete test files
echo [*] Deleting test files...
del /Q "scripts\qa\test_all_features.py" 2>nul
del /Q "scripts\qa\test_api.py" 2>nul
del /Q "scripts\qa\test_chatbot_v5.py" 2>nul
del /Q "scripts\qa\test_dashboard_api.py" 2>nul
del /Q "scripts\qa\test_document_features_safe.py" 2>nul
del /Q "scripts\qa\test_document_features.py" 2>nul
del /Q "scripts\qa\test_document_imports.py" 2>nul
del /Q "scripts\qa\test_document_lightweight.py" 2>nul
del /Q "scripts\qa\test_groq_api.py" 2>nul
del /Q "scripts\qa\test_multi_layer_pipeline.py" 2>nul
del /Q "scripts\qa\test_missing_placeholders.py" 2>nul
del /Q "scripts\qa\test_professional_template.py" 2>nul
del /Q "scripts\qa\test_rag_retrieval.py" 2>nul
del /Q "scripts\qa\test_two_stage_pipeline.py" 2>nul
del /Q "test_results.json" 2>nul

REM Delete other files
echo [*] Deleting other files...
del /Q "bash.exe.stackdump" 2>nul
del /Q "frontend.html" 2>nul
del /Q "scripts\training\train_golden_data.py" 2>nul
del /Q "scripts\dev\cleanup_project.py" 2>nul

echo.
echo ============================================================
echo [OK] Cleanup complete!
echo ============================================================
echo.
echo Next steps:
echo   1. Test your API: python api_complete.py
echo   2. Verify frontend still works
echo.
pause

