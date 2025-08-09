"""
Image Processing Module
Handles image optimization, cropping, rotation, and enhancement for auto parts
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import os
from pathlib import Path
import asyncio
import re
from typing import Tuple, Optional

class ImageProcessor:
    def __init__(self):
        self.processed_dir = "processed"
        self.static_dir = "static/processed"
        os.makedirs(self.processed_dir, exist_ok=True)
        os.makedirs(self.static_dir, exist_ok=True)
        
        # SEO optimization settings
        self.ebay_main_size = (1600, 1600)  # eBay's recommended main image size
        self.ebay_secondary_size = (1200, 1200)  # Secondary images
        self.jpeg_quality = 88  # Optimal quality/size balance
        self.max_file_size = 500 * 1024  # 500KB max for fast loading
        
        # Watermark settings
        self.watermark_opacity = 0.15
        self.watermark_position = 'bottom_right'
        self.store_name = "AutoParts Pro"  # Can be made configurable
    
    async def process_image(self, image_path: str) -> str:
        """
        Main image processing pipeline
        Returns path to processed image
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Apply processing pipeline
            processed_image = await self._apply_processing_pipeline(image)
            
            # Save processed image
            filename = Path(image_path).stem + "_processed.jpg"
            output_path = os.path.join(self.static_dir, filename)
            cv2.imwrite(output_path, processed_image, [cv2.IMWRITE_JPEG_QUALITY, 95])
            
            return output_path
            
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            return os.path.basename(image_path)
    
    async def _apply_processing_pipeline(self, image: np.ndarray) -> np.ndarray:
        """Apply the complete image processing pipeline"""
        
        # 1. Auto-rotate if needed
        image = self._auto_rotate(image)
        
        # 2. Remove background and focus on part
        image = self._smart_crop(image)
        
        # 3. Enhance image quality
        image = self._enhance_image(image)
        
        # 4. Resize for optimal eBay display
        image = self._resize_for_ebay(image)
        
        return image
    
    def _auto_rotate(self, image: np.ndarray) -> np.ndarray:
        """Auto-rotate image based on content analysis"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect edges to find dominant orientation
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
        
        if lines is not None:
            angles = []
            for rho, theta in lines[:10]:  # Use top 10 lines
                angle = theta * 180 / np.pi
                if angle > 90:
                    angle = angle - 180
                angles.append(angle)
            
            if angles:
                # Get median angle for rotation
                median_angle = np.median(angles)
                if abs(median_angle) > 5:  # Only rotate if significant
                    image = self._rotate_image(image, -median_angle)
        
        return image
    
    def _rotate_image(self, image: np.ndarray, angle: float) -> np.ndarray:
        """Rotate image by specified angle"""
        height, width = image.shape[:2]
        center = (width // 2, height // 2)
        
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, rotation_matrix, (width, height), 
                                flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
        return rotated
    
    def _smart_crop(self, image: np.ndarray) -> np.ndarray:
        """Intelligently crop to focus on the auto part"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Use adaptive thresholding to find object boundaries
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY_INV, 11, 2)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Find the largest contour (likely the main part)
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(largest_contour)
            
            # Add padding around the part
            padding = 50
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(image.shape[1] - x, w + 2 * padding)
            h = min(image.shape[0] - y, h + 2 * padding)
            
            # Crop the image
            cropped = image[y:y+h, x:x+w]
            
            # Only use cropped version if it's reasonable size
            if w > 100 and h > 100:
                return cropped
        
        return image
    
    def _enhance_image(self, image: np.ndarray) -> np.ndarray:
        """Enhance image quality for better visibility"""
        
        # Convert to PIL for enhancement
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(pil_image)
        pil_image = enhancer.enhance(1.2)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(pil_image)
        pil_image = enhancer.enhance(1.1)
        
        # Enhance brightness slightly
        enhancer = ImageEnhance.Brightness(pil_image)
        pil_image = enhancer.enhance(1.05)
        
        # Apply subtle unsharp mask
        pil_image = pil_image.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
        
        # Convert back to OpenCV format
        enhanced = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        return enhanced
    
    def _resize_for_ebay(self, image: np.ndarray, max_size: int = 1600) -> np.ndarray:
        """Resize image for optimal eBay display"""
        height, width = image.shape[:2]
        
        # Calculate new dimensions maintaining aspect ratio
        if max(height, width) > max_size:
            if width > height:
                new_width = max_size
                new_height = int(height * (max_size / width))
            else:
                new_height = max_size
                new_width = int(width * (max_size / height))
            
            # Resize using high-quality interpolation
            resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
            return resized
        
        return image
    
    def get_image_dimensions(self, image_path: str) -> Tuple[int, int]:
        """Get image dimensions (width, height)"""
        image = cv2.imread(image_path)
        if image is not None:
            height, width = image.shape[:2]
            return width, height
        return 0, 0
    
    def estimate_part_dimensions(self, image_path: str, reference_object: Optional[str] = None) -> dict:
        """
        Estimate physical dimensions of the part
        This is a placeholder for more advanced dimension estimation
        """
        width, height = self.get_image_dimensions(image_path)
        
        # Basic estimation based on common auto part sizes
        # In a real implementation, this would use computer vision techniques
        # or reference objects for scale
        
        estimated_dimensions = {
            "length_inches": round(width / 100, 1),  # Rough estimation
            "width_inches": round(height / 100, 1),
            "estimated_weight_lbs": 2.5,  # Default weight
            "confidence": "low"
        }
        
        return estimated_dimensions
    
    def generate_seo_filename(self, part_info: dict, image_index: int = 0, is_main: bool = False) -> str:
        """
        Generate SEO-optimized filename based on part information
        Format: {Years}-{Make}-{Model}-{Part}-{PartNumber}-{Color}-{OEM}-{ImageType}.jpg
        """
        try:
            # Extract part information from the full name or individual fields
            full_name = part_info.get('name', '')
            
            # Parse the SEO title format: "Years Make Model Part PartNumber Color OEM"
            # Example: "2014-2018 Toyota Camry Headlight Assembly 81170-06291 Clear OEM"
            years = ''
            make = ''
            model = ''
            part_name = ''
            part_number = part_info.get('part_number', '')
            color = part_info.get('color', '')
            oem_status = 'OEM' if part_info.get('is_oem', False) else 'Aftermarket'
            
            # Try to parse from the full name first
            if full_name:
                parts = full_name.split()
                if len(parts) >= 6:  # Should have at least Years Make Model Part PartNumber Color
                    # Extract years (first part, e.g., "2014-2018")
                    if '-' in parts[0] and any(char.isdigit() for char in parts[0]):
                        years = parts[0]
                        
                    # Extract make (second part, e.g., "Toyota")
                    if len(parts) > 1:
                        make = parts[1]
                        
                    # Extract model (third part, e.g., "Camry")
                    if len(parts) > 2:
                        model = parts[2]
                        
                    # Extract part name (everything between model and part number)
                    # Find where part number starts (look for alphanumeric with dashes)
                    part_start_idx = 3
                    part_end_idx = len(parts)
                    
                    for i, part in enumerate(parts[3:], 3):
                        # If this looks like a part number (contains numbers and dashes/letters)
                        if any(char.isdigit() for char in part) and any(char.isalpha() or char == '-' for char in part) and len(part) > 5:
                            part_end_idx = i
                            break
                    
                    if part_end_idx > part_start_idx:
                        part_name = ' '.join(parts[part_start_idx:part_end_idx])
            
            # Fallback to individual fields if parsing failed
            if not years:
                years = part_info.get('year_range', part_info.get('years', ''))
            if not make:
                make = part_info.get('make', '')
            if not model:
                model = part_info.get('model', '')
            if not part_name:
                part_name = part_info.get('part_name', part_info.get('category', ''))
            
            # NEW: Parse from vehicle_compatibility if individual fields are missing
            vehicle_compat = part_info.get('vehicle_compatibility', '')
            if vehicle_compat and vehicle_compat != 'Unknown Vehicle':
                # Parse "2004-2006 Subaru Outback" format
                compat_parts = vehicle_compat.split()
                if len(compat_parts) >= 3:
                    # Extract years (first part with dash and digits)
                    if not years and '-' in compat_parts[0] and any(char.isdigit() for char in compat_parts[0]):
                        years = compat_parts[0]
                    # Extract make (second part)
                    if not make and len(compat_parts) > 1:
                        make = compat_parts[1]
                    # Extract model (remaining parts)
                    if not model and len(compat_parts) > 2:
                        model = ' '.join(compat_parts[2:])
            
            # Clean up extracted values
            years = years.replace(' ', '-').replace('–', '-')
            make = make.replace(' ', '-')
            model = model.replace(' ', '-')
            part_name = part_name.replace(' ', '-')
            part_number = part_number.replace(' ', '-')
            color = color.replace(' ', '-')
            
            # Smart color logic - only include color for interior parts visible to driver
            color = self._should_include_color(part_name, part_info.get('category', '')) and color
            
            # Determine image type
            if is_main:
                image_type = 'Main'
            elif image_index == 0:
                image_type = 'Front'
            elif image_index == 1:
                image_type = 'Side'
            elif image_index == 2:
                image_type = 'Back'
            elif image_index == 3:
                image_type = 'Detail'
            else:
                image_type = f'View{image_index + 1}'
            
            # Build filename components
            components = []
            if years: components.append(years)
            if make: components.append(make)
            if model: components.append(model)
            if part_name: components.append(part_name)
            if part_number: components.append(part_number)
            if color: components.append(color)
            components.append(oem_status)
            components.append(image_type)
            
            # Join with hyphens and clean up
            filename = '-'.join(components)
            filename = re.sub(r'[^a-zA-Z0-9-]', '', filename)  # Remove special chars
            filename = re.sub(r'-+', '-', filename)  # Remove multiple hyphens
            filename = filename.strip('-')  # Remove leading/trailing hyphens
            
            return f"{filename}.jpg"
            
        except Exception as e:
            print(f"Error generating SEO filename: {e}")
            return f"auto-part-{image_index + 1}.jpg"
    
    def resize_for_ebay_seo(self, image: Image.Image, is_main: bool = False) -> Image.Image:
        """
        Resize image to optimal eBay dimensions with SEO considerations
        """
        target_size = self.ebay_main_size if is_main else self.ebay_secondary_size
        
        # Calculate aspect ratio and resize
        original_ratio = image.width / image.height
        target_ratio = target_size[0] / target_size[1]
        
        if original_ratio > target_ratio:
            # Image is wider, fit to width
            new_width = target_size[0]
            new_height = int(target_size[0] / original_ratio)
        else:
            # Image is taller, fit to height
            new_height = target_size[1]
            new_width = int(target_size[1] * original_ratio)
        
        # Resize with high-quality resampling
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create square canvas with white background
        canvas = Image.new('RGB', target_size, 'white')
        
        # Center the image on the canvas
        x_offset = (target_size[0] - new_width) // 2
        y_offset = (target_size[1] - new_height) // 2
        canvas.paste(resized, (x_offset, y_offset))
        
        return canvas
    
    def enhance_background_seo(self, image: Image.Image) -> Image.Image:
        """
        Enhance image background and overall quality for SEO
        """
        # Convert to numpy array for OpenCV processing
        img_array = np.array(image)
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Enhance contrast and brightness
        alpha = 1.1  # Contrast control (1.0-3.0)
        beta = 10    # Brightness control (0-100)
        enhanced = cv2.convertScaleAbs(img_bgr, alpha=alpha, beta=beta)
        
        # Apply slight Gaussian blur to reduce noise
        denoised = cv2.GaussianBlur(enhanced, (3, 3), 0)
        
        # Sharpen the image
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(denoised, -1, kernel)
        
        # Convert back to PIL Image
        img_rgb = cv2.cvtColor(sharpened, cv2.COLOR_BGR2RGB)
        return Image.fromarray(img_rgb)
    
    def add_seo_watermark(self, image: Image.Image, part_info: dict) -> Image.Image:
        """
        Add subtle SEO watermark with part information
        """
        try:
            # Create a copy to avoid modifying original
            watermarked = image.copy()
            
            # Create drawing context
            draw = ImageDraw.Draw(watermarked)
            
            # Try to use a nice font, fall back to default
            try:
                font_size = max(24, watermarked.width // 50)
                font = ImageFont.truetype("arial.ttf", font_size)
                small_font = ImageFont.truetype("arial.ttf", font_size // 2)
            except:
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            # Prepare watermark text
            store_text = self.store_name
            part_number = part_info.get('part_number', '')
            
            # Calculate text positions
            img_width, img_height = watermarked.size
            
            # Store name in bottom right
            try:
                store_bbox = draw.textbbox((0, 0), store_text, font=font)
                store_width = store_bbox[2] - store_bbox[0]
                store_height = store_bbox[3] - store_bbox[1]
            except:
                # Fallback for older PIL versions
                store_width, store_height = draw.textsize(store_text, font=font)
            
            store_x = img_width - store_width - 20
            store_y = img_height - store_height - 20
            
            # Part number above store name
            if part_number:
                try:
                    part_bbox = draw.textbbox((0, 0), part_number, font=small_font)
                    part_width = part_bbox[2] - part_bbox[0]
                    part_height = part_bbox[3] - part_bbox[1]
                except:
                    part_width, part_height = draw.textsize(part_number, font=small_font)
                
                part_x = img_width - part_width - 20
                part_y = store_y - part_height - 5
                
                # Draw part number with semi-transparent background
                padding = 5
                draw.rectangle(
                    [part_x - padding, part_y - padding, 
                     part_x + part_width + padding, part_y + part_height + padding],
                    fill=(255, 255, 255, int(255 * 0.7))
                )
                draw.text((part_x, part_y), part_number, fill=(0, 0, 0), font=small_font)
            
            # Draw store name with semi-transparent background
            padding = 5
            draw.rectangle(
                [store_x - padding, store_y - padding, 
                 store_x + store_width + padding, store_y + store_height + padding],
                fill=(255, 255, 255, int(255 * 0.7))
            )
            draw.text((store_x, store_y), store_text, fill=(0, 0, 0), font=font)
            
            return watermarked
            
        except Exception as e:
            print(f"Error adding watermark: {e}")
            return image
    
    def optimize_compression(self, image: Image.Image) -> Image.Image:
        """
        Optimize image compression for web while maintaining quality
        """
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'LA', 'P'):
            # Create white background
            background = Image.new('RGB', image.size, 'white')
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        return image
    
    async def seo_process_image(self, image_path: str, part_info: dict, image_index: int = 0, is_main: bool = False) -> tuple:
        """
        Complete SEO optimization pipeline for a single image
        Returns: (processed_filename, seo_filename, alt_text)
        """
        try:
            # Load the image
            image = Image.open(image_path)
            
            # Step 1: Resize for eBay
            resized_image = self.resize_for_ebay_seo(image, is_main)
            
            # Step 2: Enhance background and quality
            enhanced_image = self.enhance_background_seo(resized_image)
            
            # Step 3: Add SEO watermark
            watermarked_image = self.add_seo_watermark(enhanced_image, part_info)
            
            # Step 4: Optimize compression
            final_image = self.optimize_compression(watermarked_image)
            
            # Step 5: Generate SEO filename
            seo_filename = self.generate_seo_filename(part_info, image_index, is_main)
            
            # Step 6: Save with optimal quality
            output_path = os.path.join(self.static_dir, seo_filename)
            
            # Save with progressive JPEG for better loading
            final_image.save(
                output_path, 
                'JPEG', 
                quality=self.jpeg_quality, 
                progressive=True, 
                optimize=True
            )
            
            # Step 7: Generate alt text for SEO
            alt_text = self.generate_alt_text(part_info, image_index, is_main)
            
            print(f"SEO optimized image saved: {seo_filename}")
            return seo_filename, seo_filename, alt_text
            
        except Exception as e:
            print(f"Error in SEO processing {image_path}: {e}")
            # Fallback to basic processing
            basic_filename = await self.process_image(image_path)
            return basic_filename, basic_filename, f"Auto part image {image_index + 1}"
    
    def generate_alt_text(self, part_info: dict, image_index: int, is_main: bool) -> str:
        """
        Generate SEO-friendly alt text for images
        """
        try:
            part_name = part_info.get('part_name', 'Auto Part')
            make = part_info.get('make', '')
            model = part_info.get('model', '')
            year_range = part_info.get('year_range', '')
            color = part_info.get('color', '')
            part_number = part_info.get('part_number', '')
            
            # Build descriptive alt text
            alt_parts = []
            
            if is_main:
                alt_parts.append("Main image of")
            elif image_index == 0:
                alt_parts.append("Front view of")
            elif image_index == 1:
                alt_parts.append("Side view of")
            elif image_index == 2:
                alt_parts.append("Back view of")
            else:
                alt_parts.append(f"Detailed view {image_index + 1} of")
            
            if year_range:
                alt_parts.append(year_range)
            if make:
                alt_parts.append(make)
            if model:
                alt_parts.append(model)
            
            alt_parts.append(part_name.lower())
            
            if part_number:
                alt_parts.append(f"part number {part_number}")
            if color:
                alt_parts.append(f"in {color.lower()}")
            
            return " ".join(alt_parts)
            
        except Exception as e:
            print(f"Error generating alt text: {e}")
            return f"Auto part image {image_index + 1}"
    
    def _should_include_color(self, part_name: str, category: str) -> bool:
        """
        Determine if color should be included in SEO filename based on part type
        Only include color for interior parts visible to the driver
        """
        part_name_lower = part_name.lower()
        category_lower = category.lower()
        
        # Interior parts where color matters (visible to driver)
        interior_keywords = [
            'dashboard', 'dash', 'trim', 'panel', 'console', 'cup holder',
            'door panel', 'armrest', 'seat', 'steering wheel', 'shift knob',
            'interior', 'cabin', 'glove box', 'center console', 'bezel',
            'vent', 'air vent', 'climate control', 'radio bezel', 'gauge cluster',
            'pillar trim', 'kick panel', 'floor mat', 'carpet', 'headliner',
            'sun visor', 'mirror', 'dome light', 'courtesy light'
        ]
        
        # Check if this is an interior part
        for keyword in interior_keywords:
            if keyword in part_name_lower or keyword in category_lower:
                return True
        
        # Exterior parts - color usually not relevant for SEO
        exterior_keywords = [
            'headlight', 'tail light', 'fog light', 'bumper', 'grille',
            'fender', 'hood', 'door', 'mirror', 'antenna', 'spoiler',
            'body', 'exterior', 'wheel', 'tire', 'rim'
        ]
        
        # Internal/Electronics - color not relevant
        internal_keywords = [
            'engine', 'transmission', 'alternator', 'starter', 'battery',
            'radiator', 'fan', 'pump', 'filter', 'sensor', 'module',
            'ecu', 'pcm', 'bcm', 'abs', 'airbag', 'brake', 'suspension',
            'strut', 'shock', 'spring', 'control arm', 'tie rod',
            'ball joint', 'cv joint', 'axle', 'differential', 'catalytic',
            'exhaust', 'muffler', 'fuel', 'injector', 'throttle', 'intake',
            'turbo', 'supercharger', 'compressor', 'condenser', 'evaporator'
        ]
        
        # If it's exterior or internal, don't include color
        for keyword in exterior_keywords + internal_keywords:
            if keyword in part_name_lower or keyword in category_lower:
                return False
        
        # Default: include color if we're unsure (safer for SEO)
        return True
