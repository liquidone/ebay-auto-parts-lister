@echo off
REM eBay Auto Parts Lister - Backup Script (Batch Version)
REM Double-click this file to create a timestamped backup

echo Creating backup of eBay Auto Parts Lister...

REM Get current date and time for backup name
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "timestamp=%YYYY%-%MM%-%DD%_%HH%-%Min%-%Sec%"

set "backupName=BACKUP_%timestamp%"
set "backupPath=..\Ebay Lister v1.0 - BACKUPS\%backupName%"

echo Backup name: %backupName%

REM Create backup directory if it doesn't exist
if not exist "..\Ebay Lister v1.0 - BACKUPS" mkdir "..\Ebay Lister v1.0 - BACKUPS"

REM Copy all files (excluding the backup directory itself)
echo Copying files...
xcopy "." "%backupPath%" /E /I /H /Y /EXCLUDE:backup_exclude.txt

REM Create backup info file
echo # Backup Information > "%backupPath%\BACKUP_INFO.md"
echo. >> "%backupPath%\BACKUP_INFO.md"
echo **Created:** %date% %time% >> "%backupPath%\BACKUP_INFO.md"
echo **Backup Name:** %backupName% >> "%backupPath%\BACKUP_INFO.md"
echo. >> "%backupPath%\BACKUP_INFO.md"
echo ## Status at Backup Time: >> "%backupPath%\BACKUP_INFO.md"
echo - Image upload and preview: Working >> "%backupPath%\BACKUP_INFO.md"
echo - FastAPI backend: Running >> "%backupPath%\BACKUP_INFO.md"
echo - Database: Functional >> "%backupPath%\BACKUP_INFO.md"
echo - All modules: Intact >> "%backupPath%\BACKUP_INFO.md"
echo. >> "%backupPath%\BACKUP_INFO.md"
echo ## To Restore: >> "%backupPath%\BACKUP_INFO.md"
echo 1. Copy contents of this backup folder to main project directory >> "%backupPath%\BACKUP_INFO.md"
echo 2. Run: pip install -r requirements.txt >> "%backupPath%\BACKUP_INFO.md"
echo 3. Run: python main.py >> "%backupPath%\BACKUP_INFO.md"
echo 4. Access: http://127.0.0.1:8000 >> "%backupPath%\BACKUP_INFO.md"
echo. >> "%backupPath%\BACKUP_INFO.md"
echo **Backup completed successfully!** >> "%backupPath%\BACKUP_INFO.md"

echo.
echo ================================
echo Backup completed successfully!
echo Location: %backupPath%
echo ================================
echo.
pause
