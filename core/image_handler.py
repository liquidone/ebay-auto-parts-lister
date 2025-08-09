"""
Image Handler Module
Handles image upload, validation, and storage
"""

import os
import shutil
from pathlib import Path
from fastapi import UploadFile, HTTPException
import config
from utils.validators import validate_image_file

class ImageHandler:
    """Handles all image-related operations"""
    
    def __init__(self):
        self.upload_dir = config.UPLOAD_DIR
        self.processed_dir = config.PROCESSED_DIR
    
    async def save_upload(self, file: UploadFile) -> Path:
        """
        Save an uploaded file to the upload directory
        
        Args:
            file: The uploaded file from FastAPI
            
        Returns:
            Path to the saved file
        """
        # Validate the file
        if not validate_image_file(file):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {config.ALLOWED_EXTENSIONS}"
            )
        
        # Generate unique filename
        file_path = self.upload_dir / file.filename
        
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return file_path
    
    def cleanup_uploads(self):
        """Clean up uploaded files after processing"""
        for file in self.upload_dir.glob("*"):
            if file.is_file():
                file.unlink()
    
    def move_to_processed(self, file_path: Path) -> Path:
        """
        Move a file to the processed directory
        
        Args:
            file_path: Path to the file to move
            
        Returns:
            New path in processed directory
        """
        new_path = self.processed_dir / file_path.name
        shutil.move(str(file_path), str(new_path))
        return new_path
