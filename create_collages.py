#!/usr/bin/env python3

import os
import sys
import argparse
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def main():
    parser = argparse.ArgumentParser(description='Create 12 collages from images in a folder')
    parser.add_argument('folder', help='Path to folder containing images')
    parser.add_argument('--output', '-o', default='collages', help='Output folder for collages (default: collages)')
    parser.add_argument('--add-filenames', action='store_true', help='Add filename text overlay to each image')
    parser.add_argument('--seed', type=int, help='Random seed for deterministic results')
    parser.add_argument('--border-width', type=int, default=0, help='Width of white border around each image in pixels (default: 0)')
    parser.add_argument('--must-include', nargs='+', help='Specific image files that must be included in collages (each file used exactly once)')
    
    args = parser.parse_args()
    
    # Set random seed if provided
    if args.seed is not None:
        random.seed(args.seed)
        print(f"Using random seed: {args.seed}")
    
    input_folder = Path(args.folder)
    output_folder = Path(args.output)
    
    if not input_folder.exists():
        print(f"Error: Input folder '{input_folder}' does not exist")
        sys.exit(1)
    
    output_folder.mkdir(exist_ok=True)
    
    # Get all image files
    image_files = get_image_files(input_folder)
    
    if len(image_files) < 4:
        print(f"Error: Need at least 4 images in folder, found {len(image_files)}")
        sys.exit(1)
    
    print(f"Found {len(image_files)} images")
    
    # Process must-include files if specified
    must_include_files = []
    if args.must_include:
        for file_path in args.must_include:
            path = Path(file_path)
            # Convert to absolute path if relative
            if not path.is_absolute():
                path = input_folder / path
            
            if not path.exists():
                print(f"Error: Must-include file '{file_path}' does not exist")
                sys.exit(1)
            
            if path not in image_files:
                print(f"Error: Must-include file '{file_path}' is not a valid image in the input folder")
                sys.exit(1)
            
            must_include_files.append(path)
        
        print(f"Must include {len(must_include_files)} specific files in collages (each used exactly once)")
        
        # Create a copy of must_include_files to track usage
        remaining_must_include = must_include_files.copy()
    else:
        remaining_must_include = []
    
    # Create 12 collages
    for i in range(12):
        image_files, remaining_must_include = create_collage(image_files, output_folder / f"collage_{i+1:02d}.png", args.add_filenames, args.border_width, remaining_must_include)
        print(f"Created collage {i+1}/12 (remaining image files {len(image_files)}, must-include files left: {len(remaining_must_include)})")

def get_image_files(folder):
    """Get all valid image files from folder"""
    if not folder.exists():
        return []
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    return [f for f in folder.iterdir() 
            if f.is_file() and f.suffix.lower() in image_extensions]

def load_and_resize_image(image_path, target_size, add_filename=False, border_width=0):
    """Load image and resize to fill target size with minimal whitespace"""
    try:
        with Image.open(image_path) as img:
            img = img.convert('RGB')
            
            # Calculate effective target size (accounting for border)
            target_width, target_height = target_size
            effective_width = target_width - (2 * border_width)
            effective_height = target_height - (2 * border_width)
            
            # Ensure we have positive dimensions after border
            if effective_width <= 0 or effective_height <= 0:
                effective_width = target_width
                effective_height = target_height
                border_width = 0
            
            img_width, img_height = img.size
            
            # Calculate scale factors for width and height using effective size
            scale_w = effective_width / img_width
            scale_h = effective_height / img_height
            
            # Use the larger scale factor to ensure the image fills the effective target size
            scale = max(scale_w, scale_h)
            
            # Resize image with the calculated scale
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Create new image with target size (includes border space)
            new_img = Image.new('RGB', target_size, (255, 255, 255))
            
            # Calculate cropping/centering for the resized image
            x = (new_width - effective_width) // 2
            y = (new_height - effective_height) // 2
            
            if new_width > effective_width or new_height > effective_height:
                # Crop the image to fit the effective size
                img = img.crop((x, y, x + effective_width, y + effective_height))
            
            # Paste the image with border offset
            paste_x = border_width
            paste_y = border_width
            new_img.paste(img, (paste_x, paste_y))
            
            # Add filename overlay if requested
            if add_filename:
                filename = Path(image_path).stem  # Get filename without extension
                draw = ImageDraw.Draw(new_img)
                
                # Try to use a system font, fall back to default if not available
                try:
                    font = ImageFont.truetype("Arial.ttf", size=24)
                except (OSError, IOError):
                    try:
                        font = ImageFont.load_default()
                    except:
                        font = None
                
                if font:
                    # Get text dimensions for positioning
                    bbox = draw.textbbox((0, 0), filename, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
                    # Position text at bottom-left with some padding
                    text_x = 10
                    text_y = target_size[1] - text_height - 10
                    
                    # Draw text with black background for better visibility
                    draw.rectangle([text_x-5, text_y-5, text_x + text_width + 5, text_y + text_height + 5], fill='black')
                    draw.text((text_x, text_y), filename, fill='white', font=font)
            
            return new_img
    except Exception as e:
        print(f"Error loading {image_path}: {e}")
        return None

def get_image_orientation(image_path):
    """Determine if image is portrait or landscape"""
    try:
        with Image.open(image_path) as img:
            return 'portrait' if img.height > img.width else 'landscape'
    except Exception:
        return 'landscape'  # Default to landscape if can't read

def separate_images_by_orientation(image_files):
    """Separate images into portrait and landscape lists"""
    portrait_images = []
    landscape_images = []
    
    for image_path in image_files:
        orientation = get_image_orientation(image_path)
        if orientation == 'portrait':
            portrait_images.append(image_path)
        else:
            landscape_images.append(image_path)
    
    return portrait_images, landscape_images

def create_collage(image_files, output_path, add_filenames=False, border_width=0, remaining_must_include=None):
    """Create orientation-based collages: 6 portraits or 4 landscapes per page"""
    if remaining_must_include is None:
        remaining_must_include = []
    
    # Separate images by orientation
    portrait_images, landscape_images = separate_images_by_orientation(image_files)
    
    # Separate must-include files by orientation
    must_include_portraits, must_include_landscapes = separate_images_by_orientation(remaining_must_include)
    
    # Decide whether to create portrait or landscape collage based on available images
    if len(portrait_images) >= 6 and len(landscape_images) >= 4:
        # If we have both, randomly choose orientation
        use_portrait = random.choice([True, False])
    elif len(portrait_images) >= 6:
        use_portrait = True
    elif len(landscape_images) >= 4:
        use_portrait = False
    else:
        # Not enough images of either orientation, fall back to mixed
        use_portrait = len(portrait_images) >= len(landscape_images)
    
    # A3 landscape dimensions: 4961 x 3508 pixels
    a3_width, a3_height = 4961, 3508
    
    if use_portrait and len(portrait_images) >= 6:
        # Portrait collage: 6 images in 2x3 grid (2 rows, 3 columns)
        selected_images = []
        used_must_include = []
        
        # Start with must-include portraits that fit this orientation
        available_must_include = [img for img in must_include_portraits if img in portrait_images]
        slots_to_fill = min(6, len(available_must_include))
        selected_images.extend(available_must_include[:slots_to_fill])
        used_must_include.extend(available_must_include[:slots_to_fill])
        
        # Fill remaining spots with random portraits (excluding already selected must-includes)
        remaining_portraits = [img for img in portrait_images if img not in selected_images]
        remaining_needed = 6 - len(selected_images)
        
        if remaining_needed > 0 and len(remaining_portraits) >= remaining_needed:
            selected_images.extend(random.sample(remaining_portraits, remaining_needed))
        elif remaining_needed > 0:
            # If not enough portraits, fill with any remaining images
            remaining_images = [img for img in image_files if img not in selected_images]
            selected_images.extend(random.sample(remaining_images, min(remaining_needed, len(remaining_images))))
        
        grid = (2, 3)  # 2 rows, 3 columns
        
        # Calculate cell dimensions for portrait images
        cell_width = a3_width // grid[1]  # 1653 pixels wide
        cell_height = a3_height // grid[0]  # 1754 pixels tall
        
        # Use calculated dimensions to fill the canvas
        collage_width = grid[1] * cell_width
        collage_height = grid[0] * cell_height
        
    else:
        # Landscape collage: 4 images in 2x2 grid
        selected_images = []
        used_must_include = []
        
        if len(landscape_images) >= 4:
            # Start with must-include landscapes that fit this orientation
            available_must_include = [img for img in must_include_landscapes if img in landscape_images]
            slots_to_fill = min(4, len(available_must_include))
            selected_images.extend(available_must_include[:slots_to_fill])
            used_must_include.extend(available_must_include[:slots_to_fill])
            
            # Fill remaining spots with random landscapes (excluding already selected must-includes)
            remaining_landscapes = [img for img in landscape_images if img not in selected_images]
            remaining_needed = 4 - len(selected_images)
            
            if remaining_needed > 0 and len(remaining_landscapes) >= remaining_needed:
                selected_images.extend(random.sample(remaining_landscapes, remaining_needed))
        else:
            # Fall back to any available images, but still prioritize must-includes
            available_must_include = [img for img in remaining_must_include if img in image_files]
            slots_to_fill = min(4, len(available_must_include))
            selected_images.extend(available_must_include[:slots_to_fill])
            used_must_include.extend(available_must_include[:slots_to_fill])
            
            # Fill remaining spots with any remaining images
            remaining_images = [img for img in image_files if img not in selected_images]
            remaining_needed = 4 - len(selected_images)
            
            if remaining_needed > 0 and len(remaining_images) >= remaining_needed:
                selected_images.extend(random.sample(remaining_images, min(remaining_needed, len(remaining_images))))
        
        grid = (2, 2)  # 2 rows, 2 columns
        
        # Calculate larger cell dimensions for landscape images to minimize whitespace
        # Use slightly larger cells to reduce gaps between images and borders
        cell_width = a3_width // grid[1]  # ~2490 pixels wide (slightly larger)
        cell_height = a3_height // grid[0]  # ~1764 pixels tall (slightly larger)
        
        # Use the exact A3 dimensions for the canvas
        collage_width = a3_width  # 4961 pixels
        collage_height = a3_height  # 3508 pixels
    
    # Calculate unused images and update remaining must-include
    unused_images = [img for img in image_files if img not in selected_images]
    remaining_must_include_updated = [img for img in remaining_must_include if img not in used_must_include]
    
    # Create collage canvas
    collage = Image.new('RGB', (collage_width, collage_height), (255, 255, 255))
    
    # Load and place images
    for i, image_path in enumerate(selected_images):
        img = load_and_resize_image(image_path, (cell_width, cell_height), add_filenames, border_width)
        if img is None:
            continue
            
        # Calculate position in grid
        row = i // grid[1]
        col = i % grid[1]
        x = col * cell_width
        y = row * cell_height
        
        collage.paste(img, (x, y))
    
    # Save collage
    collage.save(output_path, 'PNG')

    return unused_images, remaining_must_include_updated 

if __name__ == '__main__':
    main()