"""
Input Validation Utilities
Handles validation of user inputs and files
"""

from pathlib import Path
from fastapi import UploadFile
import config

def validate_image_file(file: UploadFile) -> bool:
    """
    Validate that an uploaded file is an allowed image type
    
    Args:
        file: The uploaded file to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not file.filename:
        return False
    
    # Get file extension
    file_ext = Path(file.filename).suffix.lower()
    
    # Check if extension is allowed
    return file_ext in config.ALLOWED_EXTENSIONS

def validate_file_size(file: UploadFile, max_size_mb: int = 10) -> bool:
    """
    Validate file size
    
    Args:
        file: The uploaded file
        max_size_mb: Maximum size in megabytes
        
    Returns:
        True if within size limit
    """
    # Read file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_size <= max_size_bytes
