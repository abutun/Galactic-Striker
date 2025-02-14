import pygame
import json
import os

# Available object types for grid mode.
AVAILABLE_TYPES = ["grunt", "swarmer", "boss"]


class LevelEditor:
    def __init__(self):
        # Grid settings.
        self.grid_cols = 20
        self.grid_rows = 25
        self.grid = [[None for _ in range(self.grid_cols)] for _ in range(self.grid_rows)]
        self.cell_size = None  # Will be computed based on screen dimensions.
        self.offset_x = 0
        self.offset_y = 0

        # Path editing: list of finalized paths and current path being drawn.
        # Each path is stored as a dictionary: {"points": [ (rel_x, rel_y), ... ], "group_speed": speed }
        self.paths = []
        self.current_path = []  # Points in absolute coordinates.

        # Modes: "grid" or "path".
        self.mode = "grid"
        self.selected_type = AVAILABLE_TYPES[0]  # Default type.
        self.selected_speed = 2  # Default speed for objects.

        # For level selection / editing:
        self.level_number = None  # Current level number (if editing an existing level).
        self.level_data = None  # Loaded level data.

        # Font for on-screen text.
        self.font = pygame.font.Font(None, 20)

    def calculate_grid(self, screen):
        sw, sh = screen.get_size()
        # Fit grid into the screen.
        self.cell_size = min(sw / self.grid_cols, sh / self.grid_rows)
        # Center the grid.
        self.offset_x = (sw - (self.cell_size * self.grid_cols)) / 2
        self.offset_y = (sh - (self.cell_size * self.grid_rows)) / 2

    def update(self):
        # This method is called every frame.
        # Currently, there's no dynamic update logic required in the editor,
        # but you can add animations or other functionality here if needed.
        pass

    def handle_event(self, event):
        screen = pygame.display.get_surface()
        if not screen:
            return
        self.calculate_grid(screen)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.selected_type = AVAILABLE_TYPES[0]
            elif event.key == pygame.K_2:
                self.selected_type = AVAILABLE_TYPES[1]
            elif event.key == pygame.K_3:
                self.selected_type = AVAILABLE_TYPES[2]
            elif event.key == pygame.K_p:
                # Toggle mode between grid and path.
                self.mode = "path" if self.mode == "grid" else "grid"
                if self.mode == "path":
                    self.current_path = []
            elif event.key == pygame.K_RETURN:
                # In path mode, finalize current path.
                if self.mode == "path" and len(self.current_path) > 0:
                    sw, sh = screen.get_size()
                    rel_points = [[pt[0] / sw, pt[1] / sh] for pt in self.current_path]
                    self.paths.append({
                        "points": rel_points,
                        "group_speed": self.selected_speed
                    })
                    self.current_path = []
            elif event.key == pygame.K_s:
                self.save_level("custom_level")
            elif event.key == pygame.K_l:
                level_num_str = input("Enter level number to load: ")
                try:
                    self.level_number = int(level_num_str)
                    self.load_level(f"{self.level_number:02d}.json")
                except ValueError:
                    print("Invalid level number.")
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if self.mode == "grid":
                col = int((x - self.offset_x) // self.cell_size)
                row = int((y - self.offset_y) // self.cell_size)
                if 0 <= row < self.grid_rows and 0 <= col < self.grid_cols:
                    if event.button == 1:
                        self.grid[row][col] = {"type": self.selected_type, "speed": self.selected_speed}
                    elif event.button == 3:
                        self.grid[row][col] = None
            elif self.mode == "path":
                if event.button == 1:
                    self.current_path.append((x, y))
                elif event.button == 3:
                    if self.current_path:
                        self.current_path.pop()

    def draw(self, screen):
        sw, sh = screen.get_size()
        self.calculate_grid(screen)
        info_text = f"Mode: {self.mode.upper()} | Selected Type: {self.selected_type}"
        mode_surface = self.font.render(info_text, True, (255, 255, 255))
        screen.blit(mode_surface, (10, 10))

        # Draw grid.
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                rect = pygame.Rect(self.offset_x + col * self.cell_size,
                                   self.offset_y + row * self.cell_size,
                                   self.cell_size, self.cell_size)
                pygame.draw.rect(screen, (50, 50, 50), rect, 1)
                cell_obj = self.grid[row][col]
                if cell_obj:
                    text = f"{cell_obj['type']}({cell_obj['speed']})"
                    text_surface = self.font.render(text, True, (255, 255, 255))
                    screen.blit(text_surface, (rect.x + 2, rect.y + 2))

        # Draw current path (if in path mode).
        if self.mode == "path":
            if len(self.current_path) > 1:
                pygame.draw.lines(screen, (0, 255, 0), False, self.current_path, 3)
            for pt in self.current_path:
                pygame.draw.circle(screen, (255, 0, 0), pt, 4)

        # Draw finalized paths.
        for path_obj in self.paths:
            abs_points = [[pt[0] * sw, pt[1] * sh] for pt in path_obj["points"]]
            if len(abs_points) > 1:
                pygame.draw.lines(screen, (0, 0, 255), False, abs_points, 3)
            for pt in abs_points:
                pygame.draw.circle(screen, (0, 255, 255), (int(pt[0]), int(pt[1])), 4)

        instructions = [
            "Level Editor Mode:",
            "Left Click: Place object (in grid mode) / Add point (in path mode)",
            "Right Click: Remove object (grid) / Remove last point (path)",
            "Press 1-3: Select object type (grunt, swarmer, boss)",
            "Press P: Toggle between GRID and PATH mode",
            "Press Enter (in path mode): Finalize current path",
            "Press S: Save level, L: Load level (via console)"
        ]
        y_offset = 40
        for line in instructions:
            line_surface = self.font.render(line, True, (255, 255, 255))
            screen.blit(line_surface, (10, y_offset))
            y_offset += line_surface.get_height() + 2

    def save_level(self, filename):
        level_data = {
            "grid_objects": [],
            "paths": self.paths
        }
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                obj = self.grid[row][col]
                if obj is not None:
                    level_data["grid_objects"].append({
                        "row": row,
                        "col": col,
                        "type": obj["type"],
                        "speed": obj["speed"]
                    })
        filepath = os.path.join("assets", "levels", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(level_data, f, indent=4)
        print(f"Level saved as {filepath}")

    def load_level(self, filename):
        filepath = os.path.join("assets", "levels", filename)
        if not os.path.exists(filepath):
            print(f"Level file {filepath} not found.")
            return
        with open(filepath, "r") as f:
            level_data = json.load(f)
        self.grid = [[None for _ in range(self.grid_cols)] for _ in range(self.grid_rows)]
        self.paths = []
        self.current_path = []
        if "grid_objects" in level_data:
            for obj in level_data["grid_objects"]:
                row = obj["row"]
                col = obj["col"]
                self.grid[row][col] = {"type": obj["type"], "speed": obj["speed"]}
        if "paths" in level_data:
            self.paths = level_data["paths"]
        self.level_data = level_data
        print(f"Level {filename} loaded.")
