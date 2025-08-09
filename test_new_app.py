"""
Test script to verify the new modular application structure
Run this to ensure all imports work correctly
"""

import sys
import os

def test_imports():
    """Test that all modules can be imported"""
    print("Testing module imports...")
    
    try:
        import config
        print("[OK] config module")
    except ImportError as e:
        print(f"[FAIL] config module: {e}")
        return False
    
    try:
        from core.app import create_app
        print("[OK] core.app module")
    except ImportError as e:
        print(f"[FAIL] core.app module: {e}")
        return False
    
    try:
        from api.routes import router
        print("[OK] api.routes module")
    except ImportError as e:
        print(f"[FAIL] api.routes module: {e}")
        return False
    
    try:
        from core.image_handler import ImageHandler
        print("[OK] core.image_handler module")
    except ImportError as e:
        print(f"[FAIL] core.image_handler module: {e}")
        return False
    
    try:
        from core.part_processor import PartProcessor
        print("[OK] core.part_processor module")
    except ImportError as e:
        print(f"[FAIL] core.part_processor module: {e}")
        return False
    
    try:
        from services.vision_api import VisionAPI
        print("[OK] services.vision_api module")
    except ImportError as e:
        print(f"[FAIL] services.vision_api module: {e}")
        return False
    
    try:
        from services.gemini_api import GeminiAPI
        print("[OK] services.gemini_api module")
    except ImportError as e:
        print(f"[FAIL] services.gemini_api module: {e}")
        return False
    
    try:
        from utils.file_io import read_prompt, ensure_directories
        print("[OK] utils.file_io module")
    except ImportError as e:
        print(f"[FAIL] utils.file_io module: {e}")
        return False
    
    try:
        from utils.validators import validate_image_file
        print("[OK] utils.validators module")
    except ImportError as e:
        print(f"[FAIL] utils.validators module: {e}")
        return False
    
    return True

def test_directories():
    """Test that required directories exist"""
    print("\nChecking directories...")
    from utils.file_io import ensure_directories
    ensure_directories()
    
    import config
    dirs_to_check = [
        config.TEMPLATES_DIR,
        config.STATIC_DIR,
        config.STATIC_DIR / "css",
        config.STATIC_DIR / "js",
        config.PROMPTS_DIR,
        config.UPLOAD_DIR,
        config.PROCESSED_DIR
    ]
    
    for dir_path in dirs_to_check:
        if dir_path.exists():
            print(f"[OK] {dir_path}")
        else:
            print(f"[FAIL] {dir_path} - MISSING")
            return False
    
    return True

def test_static_files():
    """Test that static files exist"""
    print("\nChecking static files...")
    import config
    
    files_to_check = [
        config.TEMPLATES_DIR / "base.html",
        config.TEMPLATES_DIR / "index.html",
        config.STATIC_DIR / "css" / "style.css",
        config.STATIC_DIR / "js" / "app.js",
        config.STATIC_DIR / "js" / "upload.js",
        config.STATIC_DIR / "js" / "debug.js",
        config.PROMPTS_DIR / "part_identifier.txt"
    ]
    
    for file_path in files_to_check:
        if file_path.exists():
            print(f"[OK] {file_path}")
        else:
            print(f"[FAIL] {file_path} - MISSING")
            return False
    
    return True

def test_app_creation():
    """Test that the FastAPI app can be created"""
    print("\nTesting app creation...")
    try:
        from core.app import create_app
        app = create_app()
        print("[OK] FastAPI app created successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Failed to create app: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Testing New eBay Auto Parts Lister Structure")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Run tests
    if not test_imports():
        all_tests_passed = False
    
    if not test_directories():
        all_tests_passed = False
    
    if not test_static_files():
        all_tests_passed = False
    
    if not test_app_creation():
        all_tests_passed = False
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("ALL TESTS PASSED - Ready to deploy!")
    else:
        print("SOME TESTS FAILED - Fix issues before deploying")
    print("=" * 50)
