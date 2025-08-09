"""
File I/O Utilities
Handles file reading and writing operations
"""

from pathlib import Path
import config

def read_prompt(filename: str) -> str:
    """
    Read a prompt file from the prompts directory
    
    Args:
        filename: Name of the prompt file
        
    Returns:
        Contents of the prompt file
    """
    prompt_path = config.PROMPTS_DIR / filename
    
    if not prompt_path.exists():
        # Return a default prompt if file doesn't exist
        return """You are an expert at identifying auto parts from images. 
        Analyze the image and provide detailed information about the part."""
    
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()

def save_json(data: dict, filename: str) -> Path:
    """
    Save data as JSON file
    
    Args:
        data: Dictionary to save
        filename: Output filename
        
    Returns:
        Path to saved file
    """
    import json
    output_path = config.BASE_DIR / filename
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    return output_path

def ensure_directories():
    """Ensure all required directories exist"""
    directories = [
        config.UPLOAD_DIR,
        config.PROCESSED_DIR,
        config.STATIC_DIR,
        config.TEMPLATES_DIR,
        config.PROMPTS_DIR,
        config.STATIC_DIR / "css",
        config.STATIC_DIR / "js"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
