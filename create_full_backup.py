#!/usr/bin/env python3
"""
Create a complete backup of the eBay Auto Parts Lister project
Before surgical cleanup operation
"""

import os
import zipfile
from datetime import datetime
import shutil

def create_backup():
    # Get current directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Backup filename
    backup_name = f"FULL_BACKUP_BEFORE_CLEANUP_{timestamp}.zip"
    backup_path = os.path.join(project_dir, backup_name)
    
    print(f"Creating backup: {backup_name}")
    print("=" * 60)
    
    # Files/folders to exclude from backup
    exclude_patterns = [
        '.git',
        '__pycache__',
        '*.pyc',
        '.env',
        'FULL_BACKUP_BEFORE_CLEANUP_*.zip'
    ]
    
    file_count = 0
    
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_dir):
            # Remove excluded directories from the walk
            dirs[:] = [d for d in dirs if d not in exclude_patterns]
            
            for file in files:
                # Skip excluded patterns
                if any(pattern in file for pattern in exclude_patterns):
                    continue
                    
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, project_dir)
                
                # Skip the backup file itself
                if backup_name in file:
                    continue
                
                print(f"  Adding: {arcname}")
                zipf.write(file_path, arcname)
                file_count += 1
    
    # Get backup size
    size_mb = os.path.getsize(backup_path) / (1024 * 1024)
    
    print("=" * 60)
    print(f"✓ Backup created successfully!")
    print(f"  Files backed up: {file_count}")
    print(f"  Backup size: {size_mb:.2f} MB")
    print(f"  Location: {backup_path}")
    
    return backup_path

if __name__ == "__main__":
    backup_file = create_backup()
    print("\n✓ Backup complete! Safe to proceed with cleanup.")
    print(f"\nBackup saved as: {os.path.basename(backup_file)}")
