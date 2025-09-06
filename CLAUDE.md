# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python script that creates photo collages from a folder of images. The `create_collages.py` script generates 12 collages with intelligent orientation-based layouts: 6 portrait images in a 2x3 grid or 4 landscape images in a 2x2 grid, automatically chosen based on available images.

## Development Setup

The project uses a Python virtual environment located at `.venv/`. To set up development:

```bash
# Activate the virtual environment
source .venv/bin/activate

# Install dependencies (only Pillow is required)
.venv/bin/pip install pillow
```

Note: The virtual environment may need to be recreated if Python paths are broken.

## Core Architecture

- **Single script architecture**: The entire functionality is contained in `create_collages.py`
- **Main functions**:
  - `main()`: CLI argument parsing and orchestration
  - `create_collage()`: Core collage creation logic with orientation-based layouts
  - `load_and_resize_image()`: Image processing with aspect ratio preservation and cropping
  - `separate_images_by_orientation()`: Analyzes images to determine portrait vs landscape
  - `get_image_files()`: File discovery for supported image formats

## Key Features

- **Orientation-aware layouts**: Automatically creates 2x3 grids for portraits or 2x2 grids for landscapes
- **A3 canvas sizing**: Outputs at 4961 x 3508 pixels (A3 landscape dimensions)
- **Smart image selection**: Randomly samples from appropriate orientation groups
- **Filename overlays**: Optional text overlays on images via `--add-filenames` flag
- **Deterministic output**: Supports `--seed` parameter for reproducible results

## Usage

```bash
# Basic usage
.venv/bin/python create_collages.py /path/to/images

# Custom output folder
.venv/bin/python create_collages.py /path/to/images --output custom_output

# With filename overlays and deterministic seed
.venv/bin/python create_collages.py /path/to/images --add-filenames --seed 42

# Using executable directly (if shebang works)
./create_collages.py /path/to/images
```

## Testing

The project includes comprehensive unit and integration tests:

```bash
# Run all tests
.venv/bin/python tests/run_tests.py

# Run specific test modules
.venv/bin/python -m pytest tests/test_create_collages.py -v
.venv/bin/python -m pytest tests/test_integration.py -v

# Run tests with coverage (if coverage is installed)
.venv/bin/python -m coverage run tests/run_tests.py
.venv/bin/python -m coverage report
```

Test structure:
- `tests/test_create_collages.py`: Unit tests for core functions
- `tests/test_integration.py`: End-to-end integration tests
- `tests/test_images/`: Auto-generated test images for testing
- `tests/create_test_images.py`: Script to generate test images

## Key Implementation Details

- **Supported formats**: jpg, jpeg, png, bmp, tiff, webp
- **Grid layouts**: 2x3 (portrait) or 2x2 (landscape) based on image orientation analysis
- **Image processing**: Uses PIL/Pillow with Lanczos resampling and smart cropping
- **Canvas dimensions**: A3 landscape (4961x3508 pixels) for professional printing
- **Output format**: PNG files saved in specified output directory
- **Minimum requirements**: Needs at least 4 images total, 6 portraits for portrait layout, or 4 landscapes for landscape layout