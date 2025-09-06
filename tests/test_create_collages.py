#!/usr/bin/env python3

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch
import sys

# Add parent directory to path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent))
import create_collages

class TestCreateCollages(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_images_dir = Path(__file__).parent / "test_images"
        self.temp_output_dir = Path(tempfile.mkdtemp())
        
        # Ensure test images exist
        if not self.test_images_dir.exists():
            # Run the test image creation script
            create_test_images_script = Path(__file__).parent / "create_test_images.py"
            if create_test_images_script.exists():
                exec(open(create_test_images_script).read())
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.temp_output_dir.exists():
            shutil.rmtree(self.temp_output_dir)
    
    def test_get_image_files(self):
        """Test getting image files from directory"""
        image_files = create_collages.get_image_files(self.test_images_dir)
        
        # Should find multiple image files
        self.assertGreater(len(image_files), 0)
        
        # All files should have valid image extensions
        valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        for file_path in image_files:
            self.assertIn(file_path.suffix.lower(), valid_extensions)
            self.assertTrue(file_path.exists())
    
    def test_get_image_orientation(self):
        """Test image orientation detection"""
        # Find a portrait and landscape image
        image_files = create_collages.get_image_files(self.test_images_dir)
        
        portrait_files = [f for f in image_files if 'portrait' in f.name.lower()]
        landscape_files = [f for f in image_files if 'landscape' in f.name.lower()]
        
        if portrait_files:
            orientation = create_collages.get_image_orientation(portrait_files[0])
            self.assertEqual(orientation, 'portrait')
        
        if landscape_files:
            orientation = create_collages.get_image_orientation(landscape_files[0])
            self.assertEqual(orientation, 'landscape')
    
    def test_separate_images_by_orientation(self):
        """Test separating images by orientation"""
        image_files = create_collages.get_image_files(self.test_images_dir)
        portrait_images, landscape_images = create_collages.separate_images_by_orientation(image_files)
        
        # Should have both portrait and landscape images
        self.assertGreater(len(portrait_images), 0)
        self.assertGreater(len(landscape_images), 0)
        
        # Total should equal original count
        self.assertEqual(len(portrait_images) + len(landscape_images), len(image_files))
        
        # Check that orientations are correctly identified
        for img in portrait_images:
            orientation = create_collages.get_image_orientation(img)
            self.assertEqual(orientation, 'portrait')
        
        for img in landscape_images:
            orientation = create_collages.get_image_orientation(img)
            self.assertEqual(orientation, 'landscape')
    
    def test_load_and_resize_image(self):
        """Test image loading and resizing"""
        image_files = create_collages.get_image_files(self.test_images_dir)
        if not image_files:
            self.skipTest("No test images available")
        
        test_image = image_files[0]
        target_size = (400, 300)
        
        # Test without filename overlay
        resized_img = create_collages.load_and_resize_image(test_image, target_size, False)
        self.assertIsNotNone(resized_img)
        self.assertEqual(resized_img.size, target_size)
        
        # Test with filename overlay
        resized_img_with_text = create_collages.load_and_resize_image(test_image, target_size, True)
        self.assertIsNotNone(resized_img_with_text)
        self.assertEqual(resized_img_with_text.size, target_size)
    
    def test_load_and_resize_nonexistent_image(self):
        """Test handling of non-existent image"""
        fake_path = Path("nonexistent_image.jpg")
        result = create_collages.load_and_resize_image(fake_path, (400, 300), False)
        self.assertIsNone(result)
    
    def test_create_collage(self):
        """Test collage creation"""
        image_files = create_collages.get_image_files(self.test_images_dir)
        if len(image_files) < 4:
            self.skipTest("Not enough test images available")
        
        output_path = self.temp_output_dir / "test_collage.png"
        
        # Test collage creation without filenames
        create_collages.create_collage(image_files, output_path, False)
        self.assertTrue(output_path.exists())
        
        # Verify output is a valid image
        from PIL import Image
        with Image.open(output_path) as img:
            self.assertGreater(img.width, 0)
            self.assertGreater(img.height, 0)
    
    def test_create_collage_with_filenames(self):
        """Test collage creation with filename overlays"""
        image_files = create_collages.get_image_files(self.test_images_dir)
        if len(image_files) < 4:
            self.skipTest("Not enough test images available")
        
        output_path = self.temp_output_dir / "test_collage_with_names.png"
        
        # Test collage creation with filenames
        create_collages.create_collage(image_files, output_path, True)
        self.assertTrue(output_path.exists())
    
    def test_create_collage_portrait_mode(self):
        """Test portrait collage creation when enough portrait images available"""
        image_files = create_collages.get_image_files(self.test_images_dir)
        portrait_images, _ = create_collages.separate_images_by_orientation(image_files)
        
        if len(portrait_images) < 6:
            self.skipTest("Not enough portrait images for test")
        
        output_path = self.temp_output_dir / "portrait_collage.png"
        
        # Force portrait mode by providing only portrait images
        create_collages.create_collage(portrait_images, output_path, False)
        self.assertTrue(output_path.exists())
    
    def test_create_collage_landscape_mode(self):
        """Test landscape collage creation when enough landscape images available"""
        image_files = create_collages.get_image_files(self.test_images_dir)
        _, landscape_images = create_collages.separate_images_by_orientation(image_files)
        
        if len(landscape_images) < 4:
            self.skipTest("Not enough landscape images for test")
        
        output_path = self.temp_output_dir / "landscape_collage.png"
        
        # Force landscape mode by providing only landscape images
        create_collages.create_collage(landscape_images, output_path, False)
        self.assertTrue(output_path.exists())
    
    @patch('random.sample')
    def test_deterministic_collage_creation(self, mock_sample):
        """Test that collage creation is deterministic with seed"""
        image_files = create_collages.get_image_files(self.test_images_dir)
        if len(image_files) < 4:
            self.skipTest("Not enough test images available")
        
        # Mock random.sample to return first 4 images
        mock_sample.return_value = image_files[:4]
        
        output_path = self.temp_output_dir / "deterministic_collage.png"
        create_collages.create_collage(image_files, output_path, False)
        
        self.assertTrue(output_path.exists())
        mock_sample.assert_called()


class TestMainFunction(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_images_dir = Path(__file__).parent / "test_images"
        self.temp_output_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.temp_output_dir.exists():
            shutil.rmtree(self.temp_output_dir)
    
    @patch('sys.argv')
    def test_main_with_basic_args(self, mock_argv):
        """Test main function with basic arguments"""
        mock_argv.__getitem__.side_effect = lambda i: [
            'create_collages.py',
            str(self.test_images_dir),
            '--output', str(self.temp_output_dir)
        ][i]
        mock_argv.__len__.return_value = 4
        
        # Mock sys.exit to prevent actual exit
        with patch('sys.exit'):
            try:
                create_collages.main()
            except SystemExit:
                pass
        
        # Check that some collages were created
        output_files = list(self.temp_output_dir.glob("*.png"))
        self.assertGreater(len(output_files), 0)
    
    def test_main_with_insufficient_images(self):
        """Test main function behavior with insufficient images"""
        empty_dir = Path(tempfile.mkdtemp())
        
        try:
            with patch('sys.argv', ['create_collages.py', str(empty_dir)]):
                with patch('sys.exit') as mock_exit:
                    create_collages.main()
                    mock_exit.assert_called_with(1)
        finally:
            shutil.rmtree(empty_dir)
    
    def test_main_with_nonexistent_folder(self):
        """Test main function behavior with non-existent input folder"""
        fake_dir = Path("/nonexistent/directory")
        
        with patch('sys.argv', ['create_collages.py', str(fake_dir)]):
            with patch('sys.exit') as mock_exit:
                with patch('builtins.print'):  # Suppress error output
                    create_collages.main()
                mock_exit.assert_called_with(1)


if __name__ == '__main__':
    # Run the create_test_images script first if needed
    test_images_dir = Path(__file__).parent / "test_images"
    if not test_images_dir.exists() or not any(test_images_dir.iterdir()):
        print("Creating test images...")
        exec(open(Path(__file__).parent / "create_test_images.py").read())
    
    unittest.main()