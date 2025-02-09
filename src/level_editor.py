# src/level_editor.py
import pygame
import json

class LevelEditor:
    def __init__(self):
        self.grid_width = 20    # Number of columns.
        self.grid_height = 25   # Number of rows.
        # Initialize an empty grid.
        self.grid = [[None for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        self.font = pygame.font.SysFont(None, 20)
        self.selected_type = "grunt"  # Default selected object.

    def get_grid_params(self, screen):
        sw, sh = screen.get_size()
        # Compute a cell size that fits the grid in the current screen.
        cell_size = min(sw / self.grid_width, sh / self.grid_height)
        offset_x = (sw - (cell_size * self.grid_width)) / 2
        offset_y = (sh - (cell_size * self.grid_height)) / 2
        return cell_size, offset_x, offset_y

    def handle_event(self, event):
        screen = pygame.display.get_surface()
        if not screen:
            return
        cell_size, offset_x, offset_y = self.get_grid_params(screen)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.selected_type = "grunt"
            elif event.key == pygame.K_2:
                self.selected_type = "swarmer"
            elif event.key == pygame.K_3:
                self.selected_type = "boss"
            elif event.key == pygame.K_4:
                self.selected_type = "powerup_shield"
            elif event.key == pygame.K_5:
                self.selected_type = "powerup_weapon"
            elif event.key == pygame.K_s:
                self.save_level("custom_level")
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            grid_x = int((x - offset_x) // cell_size)
            grid_y = int((y - offset_y) // cell_size)
            if event.button == 1:  # Left-click places the selected object.
                self.place_object(grid_x, grid_y, self.selected_type)
            elif event.button == 3:  # Right-click removes an object.
                self.remove_object(grid_x, grid_y)

    def place_object(self, grid_x, grid_y, obj_type):
        if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
            self.grid[grid_y][grid_x] = obj_type

    def remove_object(self, grid_x, grid_y):
        if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
            self.grid[grid_y][grid_x] = None

    def save_level(self, filename):
        level_data = {
            "name": "Custom Level",
            "grid": self.grid
        }
        with open(f"assets/levels/{filename}.json", "w") as f:
            json.dump(level_data, f, indent=4)
        print(f"Level saved as assets/levels/{filename}.json")

    def update(self):
        # (Any dynamic updates for the editor can go here)
        pass

    def draw(self, screen):
        sw, sh = screen.get_size()
        cell_size, offset_x, offset_y = self.get_grid_params(screen)
        # Draw the grid.
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                rect = pygame.Rect(offset_x + x * cell_size, offset_y + y * cell_size, cell_size, cell_size)
                pygame.draw.rect(screen, (50, 50, 50), rect, 1)
                if self.grid[y][x]:
                    text_surface = self.font.render(self.grid[y][x], True, (255, 255, 255))
                    screen.blit(text_surface, (rect.x + 2, rect.y + 2))
        # Display editor instructions (left aligned at the top).
        instructions = [
            "Level Editor Mode:",
            "Left Click: Place object",
            "Right Click: Remove object",
            "Press 1: Grunt, 2: Swarmer, 3: Boss",
            "Press 4: Shield PU, 5: Weapon PU",
            "Press S: Save Level, E: Exit Editor"
        ]
        for i, line in enumerate(instructions):
            text_surface = self.font.render(line, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 20))
