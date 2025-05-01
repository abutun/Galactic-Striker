# 🚀 Galactic Striker
A sophisticated vertical-scrolling space shooter built with Python and Pygame, featuring dynamic gameplay, extensive weapon systems, and procedurally generated content.

## 📖 Table of Contents
- [Features](#-features)
- [Installation](#-installation)
- [Gameplay](#-gameplay)
- [Technical Details](#-technical-details)
- [Development](#-development)
- [Contributing](#-contributing)
- [Testing](#-testing)
- [Asset Management](#-asset-management)
- [Known Issues](#-known-issues)
- [Roadmap](#-roadmap)
- [License](#-license)

## 🎮 Features

### Core Game Mechanics
- **Dynamic Combat System**
  - Real-time space combat with fluid controls
  - Screen boundary system with play area borders
  - Collision detection with pixel-perfect accuracy
  - Particle effects for explosions and impacts

### Weapon Systems
1. **Primary Weapons**
   - Weapon1: Basic single shot - Fast, reliable starter
   - Weapon2: Double parallel - Two-way projectiles
   - Weapon3: Triple spread - Three-way projectiles
   - Weapon4: Quadriple parallel - Four-way projectiles
   - Weapon5: Heavy shot - Maximum damage, slow rate
   - Weapon6: Five-way spread - Wide area coverage
   - Weapon7: Fireball - Explosive area damage

2. **Secondary Systems**
   - Missile system with lock-on capability
   - Shield system with regeneration
   - Special weapons (unlockable)

### Enemy System
- **Types & Behaviors**
  - Small Aliens: Fast, agile, basic attacks
  - Large Aliens: Slower, tougher, complex attack patterns
  - Boss Aliens: Unique mechanics and multiple phases
  
- **AI & Patterns**
  - Advanced pathfinding
  - Formation-based movement
  - Dynamic difficulty adjustment
  - Behavioral trees for complex enemy decisions

### Progression System
1. **Player Development**
   - Experience-based ranking system
   - Collectible rank markers
   - Skill-based upgrades
   - Permanent ship improvements

2. **Level Structure**
   - 250 handcrafted levels
   - Boss encounters every 25 levels
   - Increasing complexity and challenge
   - Special bonus levels

### Bonus System
1. **Power-ups**
   - Weapon upgrades
   - Speed boosts
   - Shield enhancements
   - Extra lives
   - Time bonuses

2. **Special Items**
   - Score multipliers
   - Money bonuses (10, 50, 100, 200)
   - Letter collection system
   - Hidden bonus items

3. **Unique Modifiers**
   - Mirror mode
   - Drunk mode
   - Freeze mode
   - Warp capability

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Pygame 2.0 or higher
- Additional dependencies listed in requirements.txt

### Standard Installation
```bash
# Clone the repository
git clone https://github.com/abutun/Galactic-Striker
cd galactic-striker

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run the game
python run.py
```

### Development Installation
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

## 🎯 Gameplay

### Controls
- **Movement**
  - Arrow keys: Ship movement
  - WASD: Alternative movement controls
  
- **Combat**
  - SPACE: Primary weapon
  - LEFT SHIFT: Secondary weapon/missiles
  - CTRL: Special ability
  
- **System**
  - ESC: Pause/Menu
  - P: Quick pause
  - M: Mute audio
  - F: Toggle fullscreen

### Game Modes
1. **Campaign Mode**
   - Progressive level system
   - Story-driven missions
   - Boss encounters
   - Achievement tracking

2. **Arcade Mode**
   - Endless gameplay
   - High score focus
   - Progressive difficulty
   - Daily challenges

3. **Practice Mode**
   - Level selection
   - Boss practice
   - Weapon testing
   - Pattern learning

## 🔧 Technical Details

### Engine Architecture
- **Core Systems**
  - Custom game loop
  - Entity Component System
  - Event management
  - Resource management
  
- **Performance Features**
  - Sprite batching
  - Quadtree collision detection
  - Asset preloading
  - Memory management

### Display System
- Fullscreen support
- Multiple resolution handling
- Vsync support
- Dynamic scaling

### Audio System
- Dynamic music system
- Positional audio
- Sound pooling
- Real-time mixing

## 💻 Development

### Project Structure
Detailed breakdown of the modular architecture:

```plaintext
galactic-striker/
├── assets/              # Game resources
│   ├── aliens/         # Enemy sprites
│   ├── background/     # Background assets
│   ├── bonuses/        # Bonus sprites
│   ├── levels/         # Level definitions
│   ├── music/          # Audio tracks
│   ├── sounds/         # Sound effects
│   └── sprites/        # General sprites
│
├── src/                # Source code
│   ├── bonus/         # Bonus system
│   ├── config/        # Configuration
│   ├── enemy/         # Enemy system
│   ├── level/         # Level system
│   ├── scripts/       # Utility scripts
│   ├── weapon/        # Weapon system
│   └── ...            # Core modules
│
└── tests/             # Test suite
```

### Development Tools
- **Level Editor**
  ```bash
  python src/level_editor.py
  ```
  
- **Asset Verification**
  ```bash
  python src/scripts/verify_assets.py
  ```
  
- **Sprite Generation**
  ```bash
  python src/scripts/generate_alien_sprites.py
  ```

## 🤝 Contributing

### Getting Started
1. Fork the repository
2. Create a feature branch
3. Implement changes
4. Submit pull request

### Coding Standards
- Follow PEP 8
- Use type hints
- Document all functions
- Write unit tests

### Pull Request Process
1. Update documentation
2. Add tests
3. Update CHANGELOG
4. Request review

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run specific test category
pytest tests/test_weapons.py
pytest tests/test_enemies.py
```

### Coverage Reports
```bash
pytest --cov=src tests/
```

## 📦 Asset Management

### Required Assets
- Sprite sheets
- Sound effects
- Music tracks
- Level definitions

### Asset Creation Guidelines
- Sprite dimensions
- Color palettes
- Audio formats
- File naming conventions

## 🐛 Known Issues
- See [GitHub Issues](https://github.com/abutun/Galactic-Striker/issues)

## 🗺️ Roadmap
- Multiplayer support
- Additional weapon types
- Mobile port
- Level editor improvements

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments
- Pygame community
- Asset contributors
- Beta testers
- Community feedback

## 📞 Contact
- GitHub Issues
- Discord: [Join our server](https://discord.gg/VDpPSrwRvu)
- Email: contact@cosmicmeta.io

---

**Note**: This is an active project under development. Features and documentation are regularly updated.