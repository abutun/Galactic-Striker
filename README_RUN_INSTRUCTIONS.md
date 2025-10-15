# 🚀 Galactic Striker - Run Instructions

## How to Run the Game

### 📦 **First Time Setup** (Required)
Install the required dependencies:
```bash
pip install -r requirements.txt
```

### ✅ **Run the Game** (After setup)
Run the game using the main entry point:
```bash
python run.py
```

### ❌ **Incorrect Way** (Will cause import errors)
Do NOT run the game directly from the src directory:
```bash
python src/main.py  # This will cause "ModuleNotFoundError: No module named 'src'"
```

## Why Use run.py?

The `run.py` file properly sets up the Python path and imports, ensuring all modules can be found correctly. It's the intended entry point for the game.

## Troubleshooting

### Import Error: "ModuleNotFoundError: No module named 'pygame'"
**Solution**: Install dependencies first: `pip install -r requirements.txt`

### Import Error: "ModuleNotFoundError: No module named 'src'"
**Solution**: Always run `python run.py` from the project root directory.

### Other Issues
1. **Dependencies**: Ensure all dependencies are installed: `pip install -r requirements.txt`
2. **Directory**: Make sure you're in the project root directory when running the game
3. **Python Version**: Check that you're using Python 3.8 or higher
4. **Virtual Environment**: If using conda/venv, make sure it's activated

## Directory Structure
```
Galactic-Striker/
├── run.py          ← Use this to start the game
├── src/
│   ├── main.py     ← Don't run this directly
│   └── ...         ← Game modules
└── assets/         ← Game resources
```

## Development
When developing, always import modules relative to the project root, and test by running `python run.py`. 

## Updated In-game Controls
- `ESC` toggles the pause overlay.
- `ENTER` resumes play when paused.
- `R` restarts the current level from the pause overlay.
- `Q` quits to desktop from the pause overlay.
