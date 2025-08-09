@echo off
echo Cleaning up local duplicate files to match production server...

REM Delete duplicate part_identifier files
if exist part_identifier.py del part_identifier.py
if exist part_identifier_old.py del part_identifier_old.py
if exist part_identifier_improved.py del part_identifier_improved.py
if exist part_identifier_backup.py del part_identifier_backup.py
if exist modules\part_identifier_old.py del modules\part_identifier_old.py
if exist modules\part_identifier_improved.py del modules\part_identifier_improved.py
if exist modules\part_identifier_backup.py del modules\part_identifier_backup.py
if exist modules\enhanced_part_identifier.py del modules\enhanced_part_identifier.py

REM Delete old main files
if exist main_full.py del main_full.py
if exist main_old.py del main_old.py
if exist main_backup.py del main_backup.py
if exist main_minimal_backup.py del main_minimal_backup.py

REM Delete redundant test files
if exist test_duplicate_calls.py del test_duplicate_calls.py
if exist test_single_call.py del test_single_call.py
if exist test_debug_output.py del test_debug_output.py
if exist test_vision_direct.py del test_vision_direct.py
if exist test_vision_ocr.py del test_vision_ocr.py
if exist test_duplicate_response.json del test_duplicate_response.json
if exist test_response.json del test_response.json

REM Delete old backup files
if exist deleted_files_backup_20250806_191035.zip del deleted_files_backup_20250806_191035.zip

REM Delete unused scripts
if exist create_backup.bat del create_backup.bat
if exist create_backup.ps1 del create_backup.ps1
if exist setup_command.txt del setup_command.txt
if exist get_test_images.py del get_test_images.py
if exist create_test_images.py del create_test_images.py

REM Delete browser fallback files
if exist modules\gemini_browser_fallback.py del modules\gemini_browser_fallback.py
if exist modules\browser_fallback.py del modules\browser_fallback.py

REM Remove temp_restore directory
if exist temp_restore rmdir /s /q temp_restore

REM Remove old backup directory
if exist "Ebay Lister v1.0 - BACKUPS" rmdir /s /q "Ebay Lister v1.0 - BACKUPS"

echo.
echo Cleanup complete! Local files now match production server.
echo.
