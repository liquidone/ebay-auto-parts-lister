#!/usr/bin/env python3
"""
Surgical cleanup script for eBay Auto Parts Lister
Removes duplicate and unnecessary files while preserving core functionality
"""

import os
import shutil
from pathlib import Path
import sys

def confirm_backup():
    """Ensure backup was created before proceeding"""
    print("\n" + "="*60)
    print("SURGICAL CLEANUP - eBay Auto Parts Lister")
    print("="*60)
    
    response = input("\n⚠️  Have you created a backup using create_full_backup.py? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Please run 'python create_full_backup.py' first!")
        sys.exit(1)
    
    print("\n✅ Proceeding with cleanup...")
    return True

def cleanup_project():
    """Perform surgical cleanup of duplicate and unnecessary files"""
    
    # Files to delete (duplicates and unnecessary)
    files_to_delete = [
        # Duplicate part_identifier files (keeping modules/part_identifier.py)
        'part_identifier.py',  # Root duplicate
        'part_identifier_old.py',
        'part_identifier_improved.py',
        'part_identifier_backup.py',
        'modules/part_identifier_old.py',
        'modules/part_identifier_improved.py',
        'modules/part_identifier_backup.py',
        'modules/enhanced_part_identifier.py',  # Old enhanced version
        
        # Old main files
        'main_full.py',
        'main_old.py',
        'main_backup.py',
        
        # Redundant test files (keeping test_api.py, test_production_api.py, test_gemini.py)
        'test_duplicate_calls.py',
        'test_single_call.py',
        'test_debug_output.py',
        'test_vision_direct.py',
        'test_vision_ocr.py',
        'test_duplicate_response.json',
        'test_response.json',
        
        # Old backup files
        'deleted_files_backup_20250806_191035.zip',
        
        # Unused deployment scripts
        'create_backup.bat',
        'create_backup.ps1',
        'setup_command.txt',
        
        # Browser fallback files (removed from project)
        'modules/gemini_browser_fallback.py',
        'modules/browser_fallback.py',
        
        # Other unnecessary files
        'get_test_images.py',
        'create_test_images.py',
        'main_minimal_backup.py',
    ]
    
    # Directories to remove entirely
    dirs_to_remove = [
        'temp_restore',  # Contains old mixed backup files
        'Ebay Lister v1.0 - BACKUPS',  # Old backup directory
    ]
    
    deleted_files = []
    deleted_dirs = []
    not_found = []
    
    # Delete individual files
    for file_path in files_to_delete:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                deleted_files.append(file_path)
                print(f"✓ Deleted: {file_path}")
            except Exception as e:
                print(f"⚠️  Could not delete {file_path}: {e}")
        else:
            not_found.append(file_path)
    
    # Delete directories
    for dir_path in dirs_to_remove:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                deleted_dirs.append(dir_path)
                print(f"✓ Deleted directory: {dir_path}")
            except Exception as e:
                print(f"⚠️  Could not delete directory {dir_path}: {e}")
        else:
            not_found.append(dir_path)
    
    # Clean up __pycache__ directories
    pycache_count = 0
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                pycache_count += 1
            except:
                pass
    
    if pycache_count > 0:
        print(f"✓ Cleaned {pycache_count} __pycache__ directories")
    
    # Summary
    print("\n" + "="*60)
    print("CLEANUP SUMMARY")
    print("="*60)
    print(f"✅ Deleted {len(deleted_files)} files")
    print(f"✅ Deleted {len(deleted_dirs)} directories")
    print(f"ℹ️  {len(not_found)} items already missing (good!)")
    
    # List remaining key files
    print("\n" + "="*60)
    print("KEY FILES REMAINING")
    print("="*60)
    
    key_files = [
        'main.py',
        'modules/part_identifier.py',
        'modules/image_processor.py',
        'modules/image_processor_simple.py',
        'modules/database.py',
        'modules/ebay_api.py',
        'modules/pricing.py',
        'modules/compliance.py',
        'modules/feature_flags.py',
        'test_api.py',
        'test_production_api.py',
        'test_gemini.py',
        'requirements.txt',
        '.env',
        'auto-deploy.sh',
        'webhook-server.py',
    ]
    
    for file_path in key_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"⚠️  Missing: {file_path}")
    
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("1. Test the application: python test_api.py")
    print("2. Start the server: python main.py")
    print("3. Access at: http://143.198.55.193")
    print("4. Commit changes: git add -A && git commit -m 'Surgical cleanup complete'")
    print("\n✅ Cleanup complete! Your project is now clean and organized.")

if __name__ == "__main__":
    if confirm_backup():
        cleanup_project()
