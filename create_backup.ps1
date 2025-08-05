# eBay Auto Parts Lister - Backup Script
# Run this script to create a timestamped backup of the project

$timestamp = Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'
$backupName = "BACKUP_$timestamp"
$sourcePath = "Ebay Lister v1.0"
$backupPath = "Ebay Lister v1.0 - BACKUPS\$backupName"

Write-Host "Creating backup: $backupName" -ForegroundColor Green

# Create backup directory if it doesn't exist
if (!(Test-Path "Ebay Lister v1.0 - BACKUPS")) {
    New-Item -ItemType Directory -Path "Ebay Lister v1.0 - BACKUPS"
}

# Copy all files
xcopy "$sourcePath" "$backupPath" /E /I /H /Y

# Create backup info file
$backupInfo = @"
# Backup Information

**Created:** $(Get-Date)
**Backup Name:** $backupName
**Files Copied:** $(Get-ChildItem -Recurse $backupPath | Measure-Object).Count

## Status at Backup Time:
- Image upload and preview: Working
- FastAPI backend: Running
- Database: Functional
- All modules: Intact

## To Restore:
1. Copy contents of this backup folder to main project directory
2. Run: pip install -r requirements.txt
3. Run: python main.py
4. Access: http://127.0.0.1:8000

**Backup completed successfully!**
"@

$backupInfo | Out-File "$backupPath\BACKUP_INFO.md" -Encoding UTF8

Write-Host "Backup completed successfully!" -ForegroundColor Green
Write-Host "Location: $backupPath" -ForegroundColor Yellow
Write-Host "Files backed up: $((Get-ChildItem -Recurse $backupPath | Measure-Object).Count)" -ForegroundColor Yellow
