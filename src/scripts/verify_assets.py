import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from enemy.alien_types import AlienCategory, AlienSubType, AlienType

def verify_sprites():
    missing_sprites = []
    
    # Check regular aliens
    for type_num in range(1, 26):
        for category in [AlienCategory.SMALL, AlienCategory.LARGE]:
            for subtype in [AlienSubType.TYPE1, AlienSubType.TYPE2]:
                alien = AlienType(type_num, category, subtype)
                for frame in alien.sprite_frames:
                    if not os.path.exists(frame):
                        missing_sprites.append(frame)
    
    # Check boss aliens
    for boss_num in range(1, 26):
        alien = AlienType(boss_num, AlienCategory.BOSS)
        for frame in alien.sprite_frames:
            if not os.path.exists(frame):
                missing_sprites.append(frame)
    
    if missing_sprites:
        print("Missing sprite files:")
        for sprite in missing_sprites:
            print(f"  {sprite}")
        print("\nPlease run generate_alien_sprites.py to create missing sprites.")
        return False
    
    print("All sprite files exist!")
    return True

if __name__ == "__main__":
    # Print current directory and Python path for debugging
    print(f"Current directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    
    verify_sprites() 