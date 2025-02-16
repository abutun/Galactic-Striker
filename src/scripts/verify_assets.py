import os
import logging
import sys
from typing import List, Set

# Add the project root to Python path instead of src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.utils import load_image, load_sound  # Now we can import from src
from enemy.alien_types import AlienCategory
from config.game_settings import (
    ALIEN_SETTINGS
)

logger = logging.getLogger(__name__)

class AssetVerifier:
    def __init__(self):
        self.base_path = "assets/aliens"
        self.required_files: Set[str] = set()
        self.missing_files: List[str] = []
        self.invalid_files: List[str] = []

    def generate_required_filenames(self):
        """Generate list of all required alien sprite filenames."""
        # Regular aliens (25 types, 2 sizes, 2 subtypes)
        for type_num in range(1, 26):
            for category in [AlienCategory.SMALL, AlienCategory.LARGE]:
                for subtype in [1, 2]:
                    filename = f"alien_{type_num:02d}_{category.value}_{subtype:02d}.png"
                    self.required_files.add(filename)

        # Boss aliens (25 types)
        for boss_num in range(1, 26):
            self.required_files.add(f"boss_{boss_num:02d}.png")

    def verify_assets(self) -> bool:
        """Verify all required assets exist and are valid."""
        self.generate_required_filenames()
        
        # Check existing files
        existing_files = set(os.listdir(self.base_path))
        
        # Find missing files
        self.missing_files = [f for f in self.required_files if f not in existing_files]
        
        # Find invalid files
        self.invalid_files = [f for f in existing_files if not self._is_valid_filename(f)]
        
        # Verify file sizes
        for file in existing_files:
            if file in self.required_files:
                full_path = os.path.join(self.base_path, file)
                if not self._verify_file_size(full_path, file):
                    self.invalid_files.append(file)

        # Log results
        if self.missing_files:
            logger.error(f"Missing asset files: {len(self.missing_files)}")
            for file in self.missing_files[:5]:  # Show first 5
                logger.error(f"Missing: {file}")
            if len(self.missing_files) > 5:
                logger.error(f"... and {len(self.missing_files) - 5} more")

        if self.invalid_files:
            logger.error(f"Invalid asset files: {len(self.invalid_files)}")
            for file in self.invalid_files[:5]:
                logger.error(f"Invalid: {file}")
            if len(self.invalid_files) > 5:
                logger.error(f"... and {len(self.invalid_files) - 5} more")

        return not (self.missing_files or self.invalid_files)

    def _is_valid_filename(self, filename: str) -> bool:
        """Check if filename follows the correct format."""
        if filename.startswith("boss_"):
            # boss_XX.png
            parts = filename.split("_")
            return (len(parts) == 2 and 
                   parts[1].endswith(".png") and 
                   parts[1][:-4].isdigit() and 
                   1 <= int(parts[1][:-4]) <= 25)
        
        elif filename.startswith("alien_"):
            # alien_XX_size_YY.png
            parts = filename.replace(".png", "").split("_")
            if len(parts) != 4:
                return False
            
            try:
                type_num = int(parts[1])
                category = parts[2]
                subtype = int(parts[3])
                
                return (1 <= type_num <= 25 and
                       category in [c.value for c in AlienCategory] and
                       1 <= subtype <= 2)
            except ValueError:
                return False
        
        return False

    def _verify_file_size(self, filepath: str, filename: str) -> bool:
        """Verify the file size matches expected dimensions."""
        try:
            import pygame
            image = pygame.image.load(filepath)
            size = image.get_size()
            
            if filename.startswith("boss_"):
                expected_size = ALIEN_SETTINGS["boss"]["size"]
            elif "_small_" in filename:
                expected_size = ALIEN_SETTINGS["small"]["size"]
            else:
                expected_size = ALIEN_SETTINGS["large"]["size"]
                
            return size == expected_size
        except Exception as e:
            logger.error(f"Error verifying {filename}: {e}")
            return False

if __name__ == "__main__":
    verifier = AssetVerifier()
    if verifier.verify_assets():
        print("✅ All assets verified successfully!")
    else:
        print("❌ Asset verification failed!") 