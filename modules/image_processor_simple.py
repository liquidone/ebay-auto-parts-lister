import os
import io
from typing import List, Tuple
from PIL import Image, ImageEnhance, ImageFilter
import base64

class ImageProcessor:
    def __init__(self):
        """Initialize the simplified image processor using only Pillow"""
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
        print("Initialized simplified image processor (Pillow only)")

    def process_images(self, image_paths: List[str], output_dir: str = "processed") -> List[str]:
        """Process multiple images with basic enhancement"""
        processed_paths = []
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        for image_path in image_paths:
            try:
                processed_path = self._process_single_image(image_path, output_dir)
                if processed_path:
                    processed_paths.append(processed_path)
            except Exception as e:
                print(f"Error processing {image_path}: {e}")
                # Use original image if processing fails
                processed_paths.append(image_path)
        
        return processed_paths

    def _process_single_image(self, image_path: str, output_dir: str) -> str:
        """Process a single image with basic enhancements"""
        try:
            # Load image
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Basic enhancements
                img = self._enhance_image(img)
                
                # Resize if too large (max 1200px on longest side)
                img = self._resize_image(img, max_size=1200)
                
                # Save processed image
                filename = os.path.basename(image_path)
                name, ext = os.path.splitext(filename)
                processed_filename = f"{name}_processed{ext}"
                processed_path = os.path.join(output_dir, processed_filename)
                
                img.save(processed_path, quality=85, optimize=True)
                return processed_path
                
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            return image_path

    def _enhance_image(self, img: Image.Image) -> Image.Image:
        """Apply basic image enhancements"""
        try:
            # Enhance contrast slightly
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.1)
            
            # Enhance sharpness slightly
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.1)
            
            # Apply a subtle unsharp mask
            img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
            
            return img
        except Exception as e:
            print(f"Error enhancing image: {e}")
            return img

    def _resize_image(self, img: Image.Image, max_size: int = 1200) -> Image.Image:
        """Resize image if it's too large"""
        try:
            width, height = img.size
            
            if max(width, height) > max_size:
                # Calculate new dimensions maintaining aspect ratio
                if width > height:
                    new_width = max_size
                    new_height = int((height * max_size) / width)
                else:
                    new_height = max_size
                    new_width = int((width * max_size) / height)
                
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            return img
        except Exception as e:
            print(f"Error resizing image: {e}")
            return img

    def encode_image_base64(self, image_path: str) -> str:
        """Encode image as base64 string"""
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return encoded_string
        except Exception as e:
            print(f"Error encoding image {image_path}: {e}")
            return ""

    def get_image_info(self, image_path: str) -> dict:
        """Get basic image information"""
        try:
            with Image.open(image_path) as img:
                return {
                    "filename": os.path.basename(image_path),
                    "format": img.format,
                    "mode": img.mode,
                    "size": img.size,
                    "width": img.width,
                    "height": img.height
                }
        except Exception as e:
            print(f"Error getting image info for {image_path}: {e}")
            return {"error": str(e)}

    def is_supported_format(self, filename: str) -> bool:
        """Check if image format is supported"""
        ext = os.path.splitext(filename.lower())[1]
        return ext in self.supported_formats
