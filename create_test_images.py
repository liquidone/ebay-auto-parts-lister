"""
Create challenging test images for Gemini headless browser feature testing
These images simulate real-world challenging auto part identification scenarios
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random

def create_challenging_brake_rotor():
    """Create a challenging brake rotor image with rust and wear"""
    
    # Create base image
    img = Image.new('RGB', (800, 600), color=(40, 40, 40))
    draw = ImageDraw.Draw(img)
    
    # Draw brake rotor shape
    center_x, center_y = 400, 300
    
    # Outer circle (rotor edge)
    draw.ellipse([center_x-200, center_y-200, center_x+200, center_y+200], 
                fill=(80, 80, 80), outline=(60, 60, 60), width=3)
    
    # Inner circle (hub)
    draw.ellipse([center_x-80, center_y-80, center_x+80, center_y+80], 
                fill=(50, 50, 50), outline=(40, 40, 40), width=2)
    
    # Add rust patches (brown/orange spots)
    for _ in range(20):
        x = random.randint(center_x-180, center_x+180)
        y = random.randint(center_y-180, center_y+180)
        size = random.randint(10, 40)
        rust_color = (random.randint(120, 180), random.randint(60, 100), random.randint(20, 40))
        draw.ellipse([x-size//2, y-size//2, x+size//2, y+size//2], fill=rust_color)
    
    # Add wear grooves
    for i in range(8):
        angle = i * 45
        x1 = center_x + 100 * (1 if angle % 90 == 0 else 0.7)
        y1 = center_y + 100 * (1 if angle % 90 == 45 else 0.7)
        x2 = center_x + 150 * (1 if angle % 90 == 0 else 0.7)
        y2 = center_y + 150 * (1 if angle % 90 == 45 else 0.7)
        draw.line([x1, y1, x2, y2], fill=(30, 30, 30), width=3)
    
    # Add dirt/grime overlay
    overlay = Image.new('RGBA', (800, 600), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    for _ in range(100):
        x = random.randint(0, 800)
        y = random.randint(0, 600)
        size = random.randint(5, 25)
        dirt_color = (random.randint(40, 80), random.randint(35, 70), random.randint(20, 50), random.randint(30, 80))
        overlay_draw.ellipse([x-size//2, y-size//2, x+size//2, y+size//2], fill=dirt_color)
    
    # Composite the overlay
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    
    # Add some blur to simulate poor focus
    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    return img

def create_worn_engine_part():
    """Create a worn engine part with partially visible part numbers"""
    
    img = Image.new('RGB', (600, 400), color=(30, 35, 40))
    draw = ImageDraw.Draw(img)
    
    # Draw engine part shape (rectangular with rounded corners)
    draw.rounded_rectangle([50, 50, 550, 350], radius=20, fill=(70, 75, 80), outline=(50, 55, 60), width=2)
    
    # Add mounting holes
    for x, y in [(100, 100), (500, 100), (100, 300), (500, 300)]:
        draw.ellipse([x-15, y-15, x+15, y+15], fill=(20, 20, 20), outline=(10, 10, 10))
    
    # Add partially visible part number (worn/dirty)
    try:
        # Try to use a basic font, fallback to default if not available
        font = ImageFont.load_default()
    except:
        font = None
    
    # Simulate worn part number
    part_text = "AC-DELCO-12345678"
    text_x, text_y = 150, 200
    
    # Draw text with wear effect (multiple layers with slight offsets)
    for offset in [(2, 2), (1, 1), (0, 0)]:
        color = (200, 200, 200) if offset == (0, 0) else (100, 100, 100)
        draw.text((text_x + offset[0], text_y + offset[1]), part_text, fill=color, font=font)
    
    # Add scratches and wear marks
    for _ in range(15):
        x1 = random.randint(50, 550)
        y1 = random.randint(50, 350)
        x2 = x1 + random.randint(-50, 50)
        y2 = y1 + random.randint(-20, 20)
        draw.line([x1, y1, x2, y2], fill=(40, 40, 40), width=random.randint(1, 3))
    
    # Add oil stains
    for _ in range(10):
        x = random.randint(50, 550)
        y = random.randint(50, 350)
        size = random.randint(20, 60)
        stain_color = (20, 25, 30)
        draw.ellipse([x-size//2, y-size//2, x+size//2, y+size//2], fill=stain_color)
    
    return img

def create_multiple_parts_image():
    """Create an image with multiple auto parts (challenging for AI)"""
    
    img = Image.new('RGB', (800, 600), color=(45, 50, 55))
    draw = ImageDraw.Draw(img)
    
    # Part 1: Spark plug (top left)
    draw.rectangle([50, 50, 150, 250], fill=(180, 180, 180), outline=(160, 160, 160))
    draw.rectangle([75, 50, 125, 80], fill=(200, 200, 200))  # ceramic top
    draw.rectangle([85, 220, 115, 250], fill=(120, 120, 120))  # threaded bottom
    
    # Part 2: Air filter (top right)
    draw.rectangle([450, 50, 650, 200], fill=(240, 220, 180), outline=(200, 180, 140))
    # Add filter pleats
    for i in range(10):
        x = 450 + i * 20
        draw.line([x, 50, x, 200], fill=(200, 180, 140), width=2)
    
    # Part 3: Brake pad (bottom left)
    draw.rectangle([50, 350, 200, 500], fill=(80, 70, 60), outline=(60, 50, 40))
    draw.rectangle([50, 350, 200, 380], fill=(120, 100, 80))  # friction material
    
    # Part 4: Oil filter (bottom right)
    draw.ellipse([450, 350, 600, 500], fill=(100, 100, 120), outline=(80, 80, 100))
    draw.rectangle([500, 320, 550, 350], fill=(80, 80, 80))  # mounting thread
    
    # Add labels that are partially obscured
    try:
        font = ImageFont.load_default()
    except:
        font = None
    
    labels = [
        (100, 260, "NGK-BKR6E"),
        (520, 210, "K&N-33-2304"),
        (100, 510, "AKEBONO-ACT787"),
        (500, 510, "FRAM-PH3593A")
    ]
    
    for x, y, text in labels:
        # Make text partially worn/dirty
        draw.text((x, y), text, fill=(150, 150, 150), font=font)
        # Add dirt overlay on some letters
        for i in range(len(text) // 3):
            char_x = x + i * 8
            draw.rectangle([char_x, y, char_x + 6, y + 12], fill=(60, 55, 50))
    
    return img

def main():
    """Create all test images"""
    
    print("Creating challenging test images for Gemini browser fallback...")
    
    # Create test images directory
    test_dir = "test_images"
    os.makedirs(test_dir, exist_ok=True)
    
    # Create challenging images
    images = [
        (create_challenging_brake_rotor(), "challenging_brake_rotor.jpg", "Heavily rusted brake rotor"),
        (create_worn_engine_part(), "worn_engine_part.jpg", "Engine part with worn part number"),
        (create_multiple_parts_image(), "multiple_auto_parts.jpg", "Multiple parts in one image")
    ]
    
    for img, filename, description in images:
        filepath = os.path.join(test_dir, filename)
        img.save(filepath, "JPEG", quality=85)
        print(f"Created: {filepath} - {description}")
    
    print(f"\nTest images created in '{test_dir}' directory!")
    print("These images are designed to challenge the standard AI and trigger browser fallback.")
    print("\nTo test:")
    print("1. Upload these images to https://143.198.55.193")
    print("2. Watch which identification phase activates")
    print("3. The browser fallback should engage for enhanced accuracy!")

if __name__ == "__main__":
    main()
