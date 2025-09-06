#!/usr/bin/env python3

import unittest
import tempfile
import shutil
import subprocess
from pathlib import Path
from PIL import Image

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete collage creation workflow"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_images_dir = Path(__file__).parent / "test_images"
        self.temp_output_dir = Path(tempfile.mkdtemp())
        self.script_path = Path(__file__).parent.parent / "create_collages.py"
        self.python_executable = Path(__file__).parent.parent / ".venv" / "bin" / "python"
        
        # Ensure test images exist
        if not self.test_images_dir.exists() or not any(self.test_images_dir.iterdir()):
            # Run the test image creation script
            create_test_images_script = Path(__file__).parent / "create_test_images.py"
            if create_test_images_script.exists():
                subprocess.run([str(self.python_executable), str(create_test_images_script)], check=True)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.temp_output_dir.exists():
            shutil.rmtree(self.temp_output_dir)
    
    def test_full_collage_creation_workflow(self):
        """Test the complete collage creation process via command line"""
        # Run the script via command line
        cmd = [
            str(self.python_executable),
            str(self.script_path),
            str(self.test_images_dir),
            "--output", str(self.temp_output_dir)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Check that the script ran successfully
        self.assertEqual(result.returncode, 0, f"Script failed with error: {result.stderr}")
        
        # Check that 12 collages were created
        collage_files = list(self.temp_output_dir.glob("collage_*.png"))
        self.assertEqual(len(collage_files), 12, f"Expected 12 collages, found {len(collage_files)}")
        
        # Verify each collage is a valid image
        for collage_file in collage_files:
            self.assertTrue(collage_file.exists())
            self.assertGreater(collage_file.stat().st_size, 1000)  # Should be reasonably large
            
            # Verify it's a valid PNG image
            with Image.open(collage_file) as img:
                self.assertEqual(img.format, 'PNG')
                self.assertGreater(img.width, 1000)  # Should be substantial size
                self.assertGreater(img.height, 1000)
    
    def test_collage_creation_with_seed(self):
        """Test that collages are identical with the same seed"""
        output_dir1 = self.temp_output_dir / "seed_test_1"
        output_dir2 = self.temp_output_dir / "seed_test_2"
        output_dir1.mkdir()
        output_dir2.mkdir()
        
        seed_value = "12345"
        
        # Create collages with same seed twice
        for output_dir in [output_dir1, output_dir2]:
            cmd = [
                str(self.python_executable),
                str(self.script_path),
                str(self.test_images_dir),
                "--output", str(output_dir),
                "--seed", seed_value
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0)
        
        # Compare the collages
        collages1 = sorted(output_dir1.glob("collage_*.png"))
        collages2 = sorted(output_dir2.glob("collage_*.png"))
        
        self.assertEqual(len(collages1), len(collages2))
        self.assertEqual(len(collages1), 12)
        
        # Compare image contents (they should be identical)
        for c1, c2 in zip(collages1, collages2):
            with Image.open(c1) as img1, Image.open(c2) as img2:
                self.assertEqual(img1.size, img2.size)
                # Convert to same format for comparison
                img1_data = list(img1.convert('RGB').getdata())
                img2_data = list(img2.convert('RGB').getdata())
                self.assertEqual(img1_data, img2_data, f"Images {c1.name} and {c2.name} differ")
    
    def test_collage_creation_with_filename_overlays(self):
        """Test collage creation with filename overlays"""
        cmd = [
            str(self.python_executable),
            str(self.script_path),
            str(self.test_images_dir),
            "--output", str(self.temp_output_dir),
            "--add-filenames"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0)
        
        # Check that collages were created
        collage_files = list(self.temp_output_dir.glob("collage_*.png"))
        self.assertEqual(len(collage_files), 12)
        
        # Verify collages exist and are valid
        for collage_file in collage_files:
            self.assertTrue(collage_file.exists())
            with Image.open(collage_file) as img:
                self.assertEqual(img.format, 'PNG')
    
    def test_error_handling_insufficient_images(self):
        """Test error handling when there are insufficient images"""
        # Create a directory with only 2 images
        insufficient_dir = self.temp_output_dir / "insufficient"
        insufficient_dir.mkdir()
        
        # Copy only 2 test images
        test_images = list(self.test_images_dir.glob("*.jpg"))[:2]
        for img in test_images:
            shutil.copy(img, insufficient_dir)
        
        cmd = [
            str(self.python_executable),
            str(self.script_path),
            str(insufficient_dir),
            "--output", str(self.temp_output_dir / "output_fail")
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Should fail with exit code 1
        self.assertEqual(result.returncode, 1)
        self.assertIn("Need at least 4 images", result.stdout)
    
    def test_error_handling_nonexistent_directory(self):
        """Test error handling when input directory doesn't exist"""
        fake_dir = Path("/nonexistent/directory/path")
        
        cmd = [
            str(self.python_executable),
            str(self.script_path),
            str(fake_dir),
            "--output", str(self.temp_output_dir)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Should fail with exit code 1
        self.assertEqual(result.returncode, 1)
        self.assertIn("does not exist", result.stdout)
    
    def test_different_image_formats(self):
        """Test that the script handles different image formats correctly"""
        # Create a directory with mixed format images
        mixed_format_dir = self.temp_output_dir / "mixed_formats"
        mixed_format_dir.mkdir()
        
        # Copy various format images
        for ext in ['.jpg', '.png', '.bmp', '.webp', '.tiff']:
            source_files = list(self.test_images_dir.glob(f"*{ext}"))
            if source_files:
                shutil.copy(source_files[0], mixed_format_dir)
        
        # Ensure we have at least 4 images
        all_test_images = list(self.test_images_dir.iterdir())
        copied_count = len(list(mixed_format_dir.iterdir()))
        if copied_count < 4:
            for img in all_test_images[:4-copied_count]:
                if img.is_file():
                    shutil.copy(img, mixed_format_dir)
        
        cmd = [
            str(self.python_executable),
            str(self.script_path),
            str(mixed_format_dir),
            "--output", str(self.temp_output_dir)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0)
        
        # Verify collages were created
        collage_files = list(self.temp_output_dir.glob("collage_*.png"))
        self.assertEqual(len(collage_files), 12)
    
    def test_custom_output_directory(self):
        """Test that custom output directory works correctly"""
        custom_output = self.temp_output_dir / "my_custom_collages"
        
        cmd = [
            str(self.python_executable),
            str(self.script_path),
            str(self.test_images_dir),
            "--output", str(custom_output)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0)
        
        # Check that collages were created in the custom directory
        self.assertTrue(custom_output.exists())
        collage_files = list(custom_output.glob("collage_*.png"))
        self.assertEqual(len(collage_files), 12)
    
    def test_collage_dimensions(self):
        """Test that generated collages have correct A3 dimensions"""
        cmd = [
            str(self.python_executable),
            str(self.script_path),
            str(self.test_images_dir),
            "--output", str(self.temp_output_dir)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        
        collage_files = list(self.temp_output_dir.glob("collage_*.png"))
        
        # Check dimensions of generated collages
        for collage_file in collage_files:
            with Image.open(collage_file) as img:
                # Should be A3 dimensions (4961 x 3508) or close to it
                # Allow for some variation in landscape vs portrait layouts
                self.assertGreaterEqual(img.width, 3000)
                self.assertGreaterEqual(img.height, 2000)
                self.assertLessEqual(img.width, 5000)
                self.assertLessEqual(img.height, 4000)


if __name__ == '__main__':
    unittest.main()