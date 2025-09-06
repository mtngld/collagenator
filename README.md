# Collagenator

A Python script that creates photo collages from a folder of images. Generates 12 collages with intelligent orientation-based layouts - 6 portrait images in a 2x3 grid or 4 landscape images in a 2x2 grid.

## Features

- **Smart orientation detection**: Automatically analyzes images and creates appropriate layouts
- **Professional A3 sizing**: Outputs at 4961 x 3508 pixels for high-quality printing
- **Multiple image formats**: Supports JPG, JPEG, PNG, BMP, TIFF, WebP
- **Optional filename overlays**: Add image names as text overlays
- **Deterministic results**: Use seed parameter for reproducible collages
- **High-quality processing**: Uses Lanczos resampling with smart cropping

## Installation

1. Clone or download this repository
2. Set up a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install pillow
   ```

## Usage

```bash
# Basic usage - creates 12 collages in 'collages' folder
./create_collages.py /path/to/images

# Custom output folder
./create_collages.py /path/to/images --output my_collages

# Add filename text overlays to each image
./create_collages.py /path/to/images --add-filenames

# Use seed for reproducible results
./create_collages.py /path/to/images --seed 42

# With virtual environment
source .venv/bin/activate && python create_collages.py /path/to/images
```

## How It Works

The script analyzes your images to determine their orientation (portrait vs landscape) and creates appropriate layouts:

- **Portrait collages**: 6 images in a 2×3 grid (2 rows, 3 columns)
- **Landscape collages**: 4 images in a 2×2 grid
- **Mixed mode**: Falls back intelligently when there aren't enough images of one orientation

Each collage is sized for A3 printing (4961 × 3508 pixels) with professional quality output.

## Requirements

- Python 3.6+
- Pillow (PIL) library
- At least 4 images (6 for portrait-only collages, 4 for landscape-only)