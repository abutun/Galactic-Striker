import json
import pygame
import logging
import tkinter as tk
from tkinter import filedialog

from src.level.level_data import AlienGroup, EntryPoint, LevelData, MovementPattern, PathPoint

logger = logging.getLogger(__name__)

class LevelEditor:
    def __init__(self):
        self.screen_width = 1024
        self.screen_height = 768

        self.current_level = None
        self.selected_group = None
        self.editing_path = False
        self.current_path = []

        # UI elements
        self.buttons = self.create_buttons()
        self.load_level(1)  # Start with level 1

    def create_buttons(self):
        buttons = {
            "load": pygame.Rect(10, 10, 100, 30),
            "save": pygame.Rect(120, 10, 100, 30),
            "add_group": pygame.Rect(230, 10, 100, 30),
            "edit_path": pygame.Rect(340, 10, 100, 30)
        }
        return buttons

    def json_to_level_data(self, data) -> LevelData:
        """Convert JSON data to LevelData object."""
        alien_groups = []
        for group_data in data.get('alien_groups', []):
            path_points = [
                PathPoint(p['x'], p['y'], p.get('wait_time', 0), p.get('shoot', False))
                for p in group_data.get('path', [])
            ]
            
            group = AlienGroup(
                alien_type=group_data['alien_type'],
                count=group_data['count'],
                formation=group_data['formation'],
                spacing=group_data['spacing'],
                entry_point=EntryPoint(group_data['entry_point']),
                path=path_points,
                movement_pattern=MovementPattern(group_data['movement_pattern']),
                speed=group_data['speed'],
                health=group_data['health'],
                shoot_interval=group_data['shoot_interval'],
                group_behavior=group_data.get('group_behavior', False)
            )
            alien_groups.append(group)

        return LevelData(
            level_number=data['level_number'],
            name=data['name'],
            difficulty=data['difficulty'],
            alien_groups=alien_groups,
            boss_data=data.get('boss_data'),
            background_speed=data.get('background_speed', 1.0),
            music_track=data.get('music_track'),
            special_effects=data.get('special_effects', [])
        )

    def level_data_to_json(self):
        """Convert LevelData object to JSON-serializable dict."""
        if not self.current_level:
            return {}
            
        return {
            'level_number': self.current_level.level_number,
            'name': self.current_level.name,
            'difficulty': self.current_level.difficulty,
            'alien_groups': [
                {
                    'alien_type': group.alien_type,
                    'count': group.count,
                    'formation': group.formation,
                    'spacing': group.spacing,
                    'entry_point': group.entry_point.value,
                    'path': [
                        {
                            'x': point.x,
                            'y': point.y,
                            'wait_time': point.wait_time,
                            'shoot': point.shoot
                        }
                        for point in group.path
                    ],
                    'movement_pattern': group.movement_pattern.value,
                    'speed': group.speed,
                    'health': group.health,
                    'shoot_interval': group.shoot_interval,
                    'group_behavior': group.group_behavior
                }
                for group in self.current_level.alien_groups
            ],
            'boss_data': self.current_level.boss_data,
            'background_speed': self.current_level.background_speed,
            'music_track': self.current_level.music_track,
            'special_effects': self.current_level.special_effects
        }

    def load_level(self, level_number):
        try:
            with open(f"assets/levels/{level_number:03d}.json", "r") as f:
                data = json.load(f)
                self.current_level = self.json_to_level_data(data)
        except FileNotFoundError:
            self.current_level = LevelData(level_number, f"Level {level_number}", 1, [])

    def save_level(self):
        if self.current_level:
            with open(f"assets/levels/{self.current_level.level_number:03d}.json", "w") as f:
                json.dump(self.level_data_to_json(), f, indent=2)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                pos = event.pos
                for button_name, rect in self.buttons.items():
                    if rect.collidepoint(pos):
                        self.handle_button_click(button_name)
                
                if self.editing_path:
                    # Convert screen coordinates to relative coordinates
                    rel_x = pos[0] / self.screen_width
                    rel_y = pos[1] / self.screen_height
                    self.current_path.append(PathPoint(rel_x, rel_y, 0, False))

    def handle_button_click(self, button_name):
        if button_name == "load":
            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.askopenfilename(
                initialdir="assets/levels",
                filetypes=[("JSON files", "*.json")]
            )
            if file_path:
                level_number = int(file_path.split("/")[-1].split(".")[0])
                self.load_level(level_number)

        elif button_name == "save":
            self.save_level()

        elif button_name == "add_group":
            if self.current_level:
                new_group = AlienGroup(
                    alien_type="grunt",
                    count=5,
                    formation="line",
                    spacing=40,
                    entry_point=EntryPoint.TOP,
                    path=[],
                    movement_pattern=MovementPattern.STRAIGHT,
                    speed=1.0,
                    health=1,
                    shoot_interval=2.0
                )
                self.current_level.alien_groups.append(new_group)
                self.selected_group = len(self.current_level.alien_groups) - 1

        elif button_name == "edit_path":
            self.editing_path = not self.editing_path
            if self.editing_path:
                self.current_path = []
            elif self.selected_group is not None and self.current_path:
                self.current_level.alien_groups[self.selected_group].path = self.current_path

    def draw(self):
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Level Editor")
    
        self.screen.fill((0, 0, 0))
        
        # Draw buttons
        for name, rect in self.buttons.items():
            pygame.draw.rect(self.screen, (100, 100, 100), rect)
            # Add text to buttons...

        # Draw current level data
        if self.current_level:
            # Draw alien groups and paths
            for i, group in enumerate(self.current_level.alien_groups):
                color = (0, 255, 0) if i == self.selected_group else (255, 0, 0)
                
                # Draw path
                if group.path:
                    points = [(p.x * self.screen_width, p.y * self.screen_height) 
                             for p in group.path]
                    if len(points) > 1:
                        pygame.draw.lines(self.screen, color, False, points, 2)

        # Draw current path being edited
        if self.editing_path and self.current_path:
            points = [(p.x * self.screen_width, p.y * self.screen_height) 
                     for p in self.current_path]
            if len(points) > 1:
                pygame.draw.lines(self.screen, (0, 255, 255), False, points, 2)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.handle_event(event)
            
            self.draw()

if __name__ == "__main__":
    pygame.init()
    editor = LevelEditor()
    editor.run()
    pygame.quit()
