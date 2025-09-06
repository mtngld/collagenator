#!/usr/bin/env python3

import os
from PIL import Image, ImageDraw
from pathlib import Path

def create_test_images():
    """Create test images for the test suite"""
    test_images_dir = Path(__file__).parent / "test_images"
    test_images_dir.mkdir(exist_ok=True)
    
    # Create portrait images (taller than wide)
    for i in range(8):
        img = Image.new('RGB', (400, 600), color=(i * 30 % 255, (i * 50) % 255, (i * 70) % 255))
        draw = ImageDraw.Draw(img)
        draw.text((50, 50), f"Portrait {i+1}", fill='white')
        img.save(test_images_dir / f"portrait_{i+1}.jpg")
    
    # Create landscape images (wider than tall)
    for i in range(6):
        img = Image.new('RGB', (800, 500), color=((i * 40) % 255, (i * 60) % 255, (i * 80) % 255))
        draw = ImageDraw.Draw(img)
        draw.text((50, 50), f"Landscape {i+1}", fill='white')
        img.save(test_images_dir / f"landscape_{i+1}.png")
    
    # Create square images
    for i in range(3):
        img = Image.new('RGB', (500, 500), color=((i * 90) % 255, (i * 110) % 255, (i * 130) % 255))
        draw = ImageDraw.Draw(img)
        draw.text((50, 50), f"Square {i+1}", fill='white')
        img.save(test_images_dir / f"square_{i+1}.bmp")
    
    # Create different format images
    formats = [('.webp', 'WEBP'), ('.tiff', 'TIFF')]
    for i, (ext, format_name) in enumerate(formats):
        img = Image.new('RGB', (600, 400), color=(200, 100 + i * 50, 150))
        draw = ImageDraw.Draw(img)
        draw.text((50, 50), f"Format {ext}", fill='white')
        img.save(test_images_dir / f"format_test_{i+1}{ext}", format_name)
    
    print(f"Created test images in {test_images_dir}")

if __name__ == '__main__':
    create_test_images()