import os
import sys

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.main import Game

if __name__ == "__main__":
    game = Game()
    game.run()  # We need to add this method to Game class 