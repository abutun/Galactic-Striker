# Galactic-Striker

---

# **Game Design & Development Guide**  
**Title**: *Galactic Striker* (Placeholder)  
**Version**: 2.0  
**Engine**: Python 3.x + pygame  
**Target Platforms**: Windows, macOS, Linux, Android (via Pygame Subset for Android)  

---

## **1. Core Game Design**  
### **1.1 Gameplay Overview**  
- **Genre**: Vertical-scrolling arcade shooter.  
- **Objective**: Survive waves of enemies, defeat bosses, and achieve high scores.  
- **Key Features**:  
  - Customizable ships and weapons.  
  - User-generated levels via an in-game editor.  
  - Retro pixel art and chiptune soundtrack.  

---

## **2. Technical Architecture**  
### **2.1 Framework & Tools**  
- **Language**: Python 3.x  
- **Libraries**:  
  - **pygame**: Core rendering, input, and audio.  
  - **pygame_gui**: Level editor UI.  
  - **pytmx**: For importing Tiled map editor files (optional).  
  - **numpy**: Efficient math operations (e.g., collision grids).  
- **Tools**:  
  - **Aseprite/Tiled**: Pixel art and level design.  
  - **Bosca Ceoil/BFXR**: Music and SFX generation.  

### **2.2 Folder Structure**  
```plaintext
/galactic_striker  
  ├── /assets  
  │   ├── /sprites (ships, enemies, bullets)  
  │   ├── /backgrounds (parallax layers)  
  │   ├── /audio (music, SFX)  
  │   └── /levels (pre-built and custom levels)  
  ├── /src  
  │   ├── main.py (game loop)  
  │   ├── player.py (player logic)  
  │   ├── enemies.py (enemy classes)  
  │   ├── level_editor.py (editor logic)  
  │   └── utils.py (helper functions)  
  └── requirements.txt  
```

---

## **3. Core Mechanics**  
### **3.1 Player Mechanics**  
- **Movement**: 8-directional controls using arrow keys/WASD.  
  ```python  
  # pygame code snippet for movement  
  def update(self):  
      keys = pygame.key.get_pressed()  
      self.rect.x += (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * self.speed  
      self.rect.y += (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * self.speed  
  ```  
- **Weapons**:  
  - Primary fire: Auto-shooting lasers.  
  - Secondary: Chargeable missiles (hold SPACE).  
- **Health**: Shield (regenerates after 3 seconds of no damage) + 3 hit points.  

### **3.2 Enemy Design**  
| Type       | Behavior                          | Attack Pattern          |  
|------------|-----------------------------------|-------------------------|  
| Grunt      | Straight path, slow fire          | Single shots            |  
| Swarmer    | Zigzag movement                   | Spread shots            |  
| Boss       | Multi-phase (e.g., shield → core) | Homing missiles + lasers|  

### **3.3 Level Editor**  
- **Features**:  
  - Drag-and-drop placement of enemies, power-ups, and obstacles.  
  - Pathing tools for enemy movement.  
  - Event scripting (e.g., spawn boss after 60 seconds).  
  - Export/import levels as JSON files.  
- **UI Layout**:  
  ![Level Editor UI](https://via.placeholder.com/400x300?text=Grid+Workspace+%7C+Entity+Palette+%7C+Property+Panel)  

---

## **4. Art & Audio**  
### **4.1 Visual Style**  
- **Resolution**: 640x800 (portrait mode for mobile).  
- **Color Palette**: Retro 16-bit (e.g., #C0C0C0 for ships, #FF0000 for lasers).  
- **Sprite Sheets**: 32x32px for enemies, 64x64px for player ships.  

### **4.2 Audio Design**  
- **Music**: Looping chiptune tracks (BOSS-1.ogg, LEVEL-3.ogg).  
- **SFX**:  
  - `laser.wav`: Short, high-pitched beep.  
  - `explosion.wav`: Low-frequency boom.  

---

## **5. Python/pygame Implementation**  
### **5.1 Game Loop**  
```python  
def main():  
    pygame.init()  
    screen = pygame.display.set_mode((640, 800))  
    clock = pygame.time.Clock()  

    while running:  
        # Handle input  
        for event in pygame.event.get():  
            if event.type == pygame.QUIT:  
                running = False  

        # Update sprites  
        all_sprites.update()  

        # Render  
        screen.fill((0, 0, 0))  
        all_sprites.draw(screen)  
        pygame.display.flip()  
        clock.tick(60)  
```  

### **5.2 Level Editor Code**  
```python  
class LevelEditor:  
    def __init__(self):  
        self.selected_tile = None  
        self.grid = [[None for _ in range(20)] for _ in range(25)]  # 20x25 grid  

    def place_tile(self, x, y, tile_type):  
        grid_x = x // 32  # 32px grid snapping  
        grid_y = y // 32  
        self.grid[grid_y][grid_x] = tile_type  

    def save_level(self, filename):  
        with open(f"assets/levels/{filename}.json", "w") as f:  
            json.dump(self.grid, f)  
```  

### **5.3 JSON Level Format**  
```json  
{  
  "name": "Asteroid Belt",  
  "enemies": [  
    { "type": "grunt", "x": 320, "y": 200, "path": "straight" },  
    { "type": "boss", "x": 320, "y": 600, "phases": 3 }  
  ],  
  "triggers": [  
    { "condition": "time > 60", "action": "spawn_swarmers" }  
  ]  
}  
```  

---

## **6. Testing & Optimization**  
### **6.1 Testing Phases**  
1. **Prototype**: Validate movement, shooting, and collisions.  
2. **Alpha**: Test first 3 levels + editor (ensure no memory leaks).  
3. **Beta**: Community playtest for balancing and bug reports.  

### **6.2 Performance Tips**  
- Use `pygame.sprite.LayeredDirty()` for efficient rendering.  
- Preload all assets during startup to avoid lag.  
- Limit particle effects to 50 on screen.  

---

## **7. Monetization & Distribution**  
### **7.1 Models**  
- **Free-to-Play**:  
  - Ads between levels (optional rewarded ads for power-ups).  
  - Cosmetic DLC (ship skins, bullet trails).  
- **Paid**: $4.99 on Steam/itch.io with no ads.  

### **7.2 Platforms**  
- **PC**: Build executables via `pyinstaller`.  
- **Mobile**: Use `pygame Subset for Android` (pgs4a).  

---

## **8. Post-Launch Roadmap**  
- **Month 1**: Bug fixes + 2 free levels.  
- **Month 3**: Steam Workshop integration for sharing custom levels.  
- **Month 6**: Co-op multiplayer update.  

---

## **9. Appendix**  
### **9.1 Code Examples**  
- **Sprite Class**:  
  ```python  
  class Enemy(pygame.sprite.Sprite):  
      def __init__(self, x, y):  
          super().__init__()  
          self.image = pygame.image.load("assets/sprites/enemy_grunt.png")  
          self.rect = self.image.get_rect(center=(x, y))  
  ```  

### **9.2 Resources**  
- **Tutorials**: [Pygame Docs](https://www.pygame.org/docs/), [KidsCanCode Game Tutorials](https://kidscancode.org/blog/)  
- **Assets**: [OpenGameArt](https://opengameart.org/), [Kenney.nl](https://kenney.nl/)  

---

**Deliverables**:  
- Playable prototype with 1 level + editor (Week 4).  
- Full game with 10 levels (Month 3).  

Let me know if you need help with specific systems (e.g., collision, UI)! 🕹️