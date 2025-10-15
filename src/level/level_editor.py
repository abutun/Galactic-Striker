import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import pygame

from src.level.level_data import AlienGroup, EntryPoint, Formation, LevelData, Movement, PathPoint

logger = logging.getLogger(__name__)

LEVELS_DIR = Path("assets/levels")


# --------------------------------------------------------------------------- #
# Helpers to convert between JSON and dataclasses
# --------------------------------------------------------------------------- #
def _group_from_dict(data: Dict) -> AlienGroup:
    path = [
        PathPoint(p["x"], p["y"], p.get("wait_time", 0), p.get("shoot", False))
        for p in data.get("path", [])
    ]
    return AlienGroup(
        alien_type=data.get("alien_type", "alien_01_small_type1"),
        count=int(data.get("count", 3)),
        formation=Formation[data.get("formation", "line").upper()],
        spacing=int(data.get("spacing", 40)),
        entry_point=EntryPoint[data.get("entry_point", "top_center").upper()],
        path=path,
        movement_pattern=Movement[data.get("movement_pattern", "straight").upper()],
        speed=float(data.get("speed", 1.0)),
        life=int(data.get("life", 1)),
        shoot_interval=float(data.get("shoot_interval", 2.0)),
        group_behavior=bool(data.get("group_behavior", False)),
    )


def _group_to_dict(group: AlienGroup) -> Dict:
    return {
        "alien_type": group.alien_type,
        "count": group.count,
        "formation": group.formation.value,
        "spacing": group.spacing,
        "entry_point": group.entry_point.value,
        "path": [
            {
                "x": point.x,
                "y": point.y,
                "wait_time": point.wait_time,
                "shoot": point.shoot,
            }
            for point in group.path
        ],
        "movement_pattern": group.movement_pattern.value,
        "speed": round(group.speed, 3),
        "life": group.life,
        "shoot_interval": round(group.shoot_interval, 3),
        "group_behavior": group.group_behavior,
    }


def _level_from_dict(data: Dict) -> LevelData:
    groups = [_group_from_dict(item) for item in data.get("alien_groups", [])]
    return LevelData(
        level_number=int(data.get("level_number", 1)),
        name=data.get("name", f"Level {data.get('level_number', 1)}"),
        difficulty=int(data.get("difficulty", 1)),
        alien_groups=groups,
        boss_data=data.get("boss_data"),
        background_speed=float(data.get("background_speed", 1.0)),
        music_track=data.get("music_track"),
        special_effects=data.get("special_effects", []),
        power_up_frequency=float(data.get("power_up_frequency", 0.2)),
        minimum_clear_time=float(data.get("minimum_clear_time", 30.0)),
        bonus_objectives=data.get("bonus_objectives", []),
        hazard_types=data.get("hazard_types", []),
    )


def _level_to_dict(level: LevelData) -> Dict:
    result = {
        "level_number": level.level_number,
        "name": level.name,
        "difficulty": level.difficulty,
        "alien_groups": [_group_to_dict(group) for group in level.alien_groups],
        "boss_data": level.boss_data,
        "background_speed": level.background_speed,
        "music_track": level.music_track,
        "special_effects": level.special_effects,
        "power_up_frequency": level.power_up_frequency,
        "minimum_clear_time": level.minimum_clear_time,
        "bonus_objectives": level.bonus_objectives,
        "hazard_types": level.hazard_types,
    }
    return result


# --------------------------------------------------------------------------- #
# UI helpers
# --------------------------------------------------------------------------- #
PROPERTY_DEFS = [
    {"name": "alien_type", "label": "Alien Type", "type": "text"},
    {"name": "count", "label": "Count", "type": "int", "min": 1, "max": 20, "step": 1},
    {"name": "formation", "label": "Formation", "type": "choice", "choices": [f.value for f in Formation]},
    {"name": "spacing", "label": "Spacing", "type": "int", "min": 20, "max": 200, "step": 5},
    {"name": "entry_point", "label": "Entry", "type": "choice", "choices": [e.value for e in EntryPoint]},
    {"name": "movement_pattern", "label": "Movement", "type": "choice", "choices": [m.value for m in Movement]},
    {"name": "speed", "label": "Speed", "type": "float", "min": 0.1, "max": 10.0, "step": 0.1},
    {"name": "life", "label": "Life", "type": "int", "min": 1, "max": 50, "step": 1},
    {"name": "shoot_interval", "label": "Shoot Interval", "type": "float", "min": 0.1, "max": 10.0, "step": 0.1},
    {"name": "group_behavior", "label": "Group Behaviour", "type": "bool"},
]


class LevelEditorApp:
    """Interactive level editor running in Pygame."""

    def __init__(self, screen_size: Tuple[int, int] = (1280, 720)):
        self.screen_width, self.screen_height = screen_size
        self.screen = pygame.display.set_mode(screen_size)
        pygame.display.set_caption("Galactic Striker Level Editor")

        self.clock = pygame.time.Clock()
        self.running = True

        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)

        self.preview_rect = pygame.Rect(320, 80, 640, 520)

        self.level: LevelData = LevelData(1, "Level 1", 1, [])
        self.selected_group = 0
        self.focus_on_properties = False
        self.selected_property = 0
        self.path_edit_mode = False
        self.selected_path_index: Optional[int] = None
        self.modified = False

        self.current_file: Optional[Path] = None

    # ------------------------------------------------------------------ #
    # Level IO
    # ------------------------------------------------------------------ #
    def load_level(self, level_identifier: Union[int, str, Path]) -> None:
        if isinstance(level_identifier, int):
            path = (LEVELS_DIR / f"{level_identifier:03d}.json").resolve()
        else:
            if isinstance(level_identifier, Path):
                path = level_identifier
            else:
                raw = level_identifier.strip()
                if raw.endswith(".json"):
                    path = Path(raw)
                elif raw.isdigit():
                    path = LEVELS_DIR / f"{int(raw):03d}.json"
                else:
                    path = LEVELS_DIR / f"{raw}.json"
            if not path.is_absolute():
                if path.parts[:len(LEVELS_DIR.parts)] == LEVELS_DIR.parts:
                    path = (Path.cwd() / path).resolve()
                else:
                    path = (LEVELS_DIR / path).resolve()
            else:
                path = path.resolve()
        if not path.exists():
            logger.warning("Level file %s not found, creating new level.", path)
            level_number = int(path.stem) if path.stem.isdigit() else 1
            self.level = LevelData(level_number, f"Level {level_number}", 1, [])
            self.current_file = path
            self.selected_group = 0
            self.modified = False
            return

        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        self.level = _level_from_dict(data)
        self.current_file = path
        self.selected_group = 0
        self.selected_property = 0
        self.modified = False
        logger.info("Loaded level %s", path)

    def save_level(self, target: Optional[Path] = None) -> None:
        if target is not None:
            self.current_file = target
        if not self.current_file:
            self.current_file = LEVELS_DIR / f"{self.level.level_number:03d}.json"
        target_path = self.current_file
        if not target_path.is_absolute():
            target_path = (LEVELS_DIR / target_path).resolve()
        else:
            target_path = target_path.resolve()
        target_path.parent.mkdir(parents=True, exist_ok=True)
        if target_path.stem.isdigit():
            self.level.level_number = int(target_path.stem)
        with target_path.open("w", encoding="utf-8") as fh:
            json.dump(_level_to_dict(self.level), fh, indent=2)
        self.current_file = target_path
        self.modified = False
        logger.info("Saved level to %s", target_path)

    def save_level_as(self) -> None:
        default_name = self.current_file.name if self.current_file else f"{self.level.level_number:03d}.json"
        response = self.prompt_text("Save level as (name or path):", default_name)
        if not response:
            return
        path = Path(response.strip())
        if path.suffix.lower() != ".json":
            path = path.with_suffix(".json")
        self.save_level(path)

    # ------------------------------------------------------------------ #
    # Editing operations
    # ------------------------------------------------------------------ #
    def add_group(self) -> None:
        new_group = AlienGroup(
            alien_type="alien_01_small_type1",
            count=5,
            formation=Formation.LINE,
            spacing=50,
            entry_point=EntryPoint.TOP_CENTER,
            path=[],
            movement_pattern=Movement.STRAIGHT,
            speed=1.0,
            life=1,
            shoot_interval=2.0,
            group_behavior=False,
        )
        insert_index = self.selected_group + 1 if self.level.alien_groups else 0
        self.level.alien_groups.insert(insert_index, new_group)
        self.selected_group = insert_index
        self.modified = True

    def duplicate_group(self) -> None:
        if not self.level.alien_groups:
            return
        group = self.level.alien_groups[self.selected_group]
        clone = AlienGroup(
            alien_type=group.alien_type,
            count=group.count,
            formation=group.formation,
            spacing=group.spacing,
            entry_point=group.entry_point,
            path=[PathPoint(p.x, p.y, p.wait_time, p.shoot) for p in group.path],
            movement_pattern=group.movement_pattern,
            speed=group.speed,
            life=group.life,
            shoot_interval=group.shoot_interval,
            group_behavior=group.group_behavior,
        )
        self.level.alien_groups.insert(self.selected_group + 1, clone)
        self.selected_group += 1
        self.modified = True

    def delete_group(self) -> None:
        if not self.level.alien_groups:
            return
        self.level.alien_groups.pop(self.selected_group)
        self.selected_group = max(0, self.selected_group - 1)
        self.modified = True

    def move_group(self, direction: int) -> None:
        if not self.level.alien_groups:
            return
        new_index = self.selected_group + direction
        if not 0 <= new_index < len(self.level.alien_groups):
            return
        groups = self.level.alien_groups
        groups[self.selected_group], groups[new_index] = groups[new_index], groups[self.selected_group]
        self.selected_group = new_index
        self.modified = True

    def adjust_property(self, delta: float) -> None:
        if not self.level.alien_groups:
            return
        prop_def = PROPERTY_DEFS[self.selected_property]
        group = self.level.alien_groups[self.selected_group]
        attr = prop_def["name"]

        if prop_def["type"] == "bool":
            setattr(group, attr, not getattr(group, attr))
        elif prop_def["type"] == "choice":
            choices = prop_def["choices"]
            current_value = getattr(group, attr).value if isinstance(getattr(group, attr), (Formation, EntryPoint, Movement)) else getattr(group, attr)
            index = choices.index(current_value)
            index = (index + int(delta)) % len(choices)
            new_value = choices[index]
            enum_map = {
                "formation": Formation,
                "entry_point": EntryPoint,
                "movement_pattern": Movement,
            }
            if attr in enum_map:
                setattr(group, attr, enum_map[attr][new_value.upper()])
            else:
                setattr(group, attr, new_value)
        elif prop_def["type"] in {"int", "float"}:
            step = prop_def.get("step", 1)
            value = getattr(group, attr)
            value += step * delta
            if prop_def["type"] == "int":
                value = int(round(value))
            else:
                value = round(value, 3)
            if prop_def.get("min") is not None:
                value = max(prop_def["min"], value)
            if prop_def.get("max") is not None:
                value = min(prop_def["max"], value)
            setattr(group, attr, value)
        elif prop_def["type"] == "text":
            text = self.prompt_text(f"Enter value for {prop_def['label']}", getattr(group, attr))
            if text is not None:
                setattr(group, attr, text.strip())
        self.modified = True

    def prompt_text(self, prompt: str, initial: str = "") -> Optional[str]:
        """Blocking text input dialog."""
        text = initial
        active = True
        input_rect = pygame.Rect(self.screen_width // 2 - 200, self.screen_height // 2 - 40, 400, 80)
        shadow = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 180))

        while active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return text
                    if event.key == pygame.K_ESCAPE:
                        return None
                    if event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        if event.unicode and event.unicode.isprintable():
                            text += event.unicode

            self.screen.blit(shadow, (0, 0))
            pygame.draw.rect(self.screen, (28, 32, 48), input_rect, border_radius=12)
            pygame.draw.rect(self.screen, (120, 150, 255), input_rect, width=2, border_radius=12)

            prompt_surface = self.font_medium.render(prompt, True, (220, 230, 255))
            text_surface = self.font_medium.render(text or "", True, (255, 255, 255))
            self.screen.blit(prompt_surface, prompt_surface.get_rect(midtop=(input_rect.centerx, input_rect.top + 10)))
            self.screen.blit(text_surface, text_surface.get_rect(midtop=(input_rect.centerx, input_rect.top + 42)))
            pygame.display.flip()
            self.clock.tick(30)
        return None

    # ------------------------------------------------------------------ #
    # Path editing
    # ------------------------------------------------------------------ #
    def add_path_point(self, pos: Tuple[int, int], shoot: bool = False) -> None:
        if not self.level.alien_groups:
            return
        group = self.level.alien_groups[self.selected_group]
        rel_x = (pos[0] - self.preview_rect.left) / self.preview_rect.width
        rel_y = (pos[1] - self.preview_rect.top) / self.preview_rect.height
        rel_x = max(0.0, min(1.0, rel_x))
        rel_y = max(0.0, min(1.0, rel_y))
        group.path.append(PathPoint(rel_x, rel_y, 0, shoot))
        self.selected_path_index = len(group.path) - 1
        self.modified = True

    def remove_nearest_path_point(self, pos: Tuple[int, int]) -> None:
        if not self.level.alien_groups:
            return
        group = self.level.alien_groups[self.selected_group]
        if not group.path:
            return
        px, py = pos
        best_index = None
        best_dist = 1e9
        for idx, point in enumerate(group.path):
            x = self.preview_rect.left + point.x * self.preview_rect.width
            y = self.preview_rect.top + point.y * self.preview_rect.height
            dist = (x - px) ** 2 + (y - py) ** 2
            if dist < best_dist:
                best_dist = dist
                best_index = idx
        if best_index is not None:
            group.path.pop(best_index)
            self.selected_path_index = None
            self.modified = True

    def select_nearest_path_point(self, pos: Tuple[int, int]) -> None:
        if not self.level.alien_groups:
            return
        group = self.level.alien_groups[self.selected_group]
        if not group.path:
            self.selected_path_index = None
            return
        px, py = pos
        best_index = None
        best_dist = 1e9
        for idx, point in enumerate(group.path):
            x = self.preview_rect.left + point.x * self.preview_rect.width
            y = self.preview_rect.top + point.y * self.preview_rect.height
            dist = (x - px) ** 2 + (y - py) ** 2
            if dist < best_dist:
                best_dist = dist
                best_index = idx
        if best_index is not None:
            self.selected_path_index = best_index

    def move_selected_point(self, dx: float, dy: float) -> None:
        if not self.level.alien_groups or self.selected_path_index is None:
            return
        group = self.level.alien_groups[self.selected_group]
        point = group.path[self.selected_path_index]
        point.x = max(0.0, min(1.0, point.x + dx))
        point.y = max(0.0, min(1.0, point.y + dy))
        self.modified = True

    def toggle_selected_point_shoot(self) -> None:
        if not self.level.alien_groups or self.selected_path_index is None:
            return
        group = self.level.alien_groups[self.selected_group]
        point = group.path[self.selected_path_index]
        point.shoot = not point.shoot
        self.modified = True

    # ------------------------------------------------------------------ #
    # Drawing helpers
    # ------------------------------------------------------------------ #
    def draw(self) -> None:
        self.screen.fill((10, 14, 28))
        self._draw_header()
        self._draw_groups_panel()
        self._draw_properties_panel()
        self._draw_preview()
        self._draw_footer()
        pygame.display.flip()

    def _draw_header(self) -> None:
        title_text = f"Level {self.level.level_number} - {self.level.name}"
        if self.modified:
            title_text += " *"
        title_surface = self.font_large.render(title_text, True, (235, 240, 255))
        self.screen.blit(title_surface, (20, 20))

    def _draw_groups_panel(self) -> None:
        panel = pygame.Rect(20, 80, 280, 520)
        pygame.draw.rect(self.screen, (22, 26, 42), panel, border_radius=12)
        pygame.draw.rect(self.screen, (90, 120, 210), panel, width=2, border_radius=12)

        header = self.font_medium.render("Alien Groups", True, (200, 210, 255))
        self.screen.blit(header, (panel.left + 12, panel.top + 10))

        if not self.level.alien_groups:
            hint = self.font_small.render("Press N to add a group", True, (180, 190, 210))
            self.screen.blit(hint, hint.get_rect(center=panel.center))
            return

        for idx, group in enumerate(self.level.alien_groups):
            item_rect = pygame.Rect(panel.left + 10, panel.top + 50 + idx * 48, panel.width - 20, 40)
            is_selected = idx == self.selected_group and not self.focus_on_properties
            color = (60, 80, 140, 180) if is_selected else (40, 48, 70, 160)
            item_surface = pygame.Surface((item_rect.width, item_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(item_surface, color, item_surface.get_rect(), border_radius=10)
            self.screen.blit(item_surface, item_rect.topleft)

            text = f"{idx + 1}. {group.alien_type} x{group.count}"
            text_surface = self.font_small.render(text, True, (220, 225, 250))
            self.screen.blit(text_surface, (item_rect.left + 10, item_rect.top + 10))

    def _draw_properties_panel(self) -> None:
        panel = pygame.Rect(self.screen_width - 300, 80, 280, 520)
        pygame.draw.rect(self.screen, (22, 26, 42), panel, border_radius=12)
        pygame.draw.rect(self.screen, (90, 120, 210), panel, width=2, border_radius=12)

        header = self.font_medium.render("Properties", True, (200, 210, 255))
        self.screen.blit(header, (panel.left + 12, panel.top + 10))

        if not self.level.alien_groups:
            return

        group = self.level.alien_groups[self.selected_group]
        for idx, prop_def in enumerate(PROPERTY_DEFS):
            item_rect = pygame.Rect(panel.left + 10, panel.top + 50 + idx * 46, panel.width - 20, 38)
            is_selected = idx == self.selected_property and self.focus_on_properties
            color = (70, 100, 200, 190) if is_selected else (40, 48, 70, 150)
            item_surface = pygame.Surface((item_rect.width, item_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(item_surface, color, item_surface.get_rect(), border_radius=10)
            self.screen.blit(item_surface, item_rect.topleft)

            label_surface = self.font_small.render(prop_def["label"], True, (215, 220, 245))
            value = getattr(group, prop_def["name"])
            if isinstance(value, (Formation, EntryPoint, Movement)):
                value_text = value.value
            elif isinstance(value, bool):
                value_text = "True" if value else "False"
            else:
                value_text = str(value)
            value_surface = self.font_small.render(value_text, True, (255, 255, 255))
            self.screen.blit(label_surface, (item_rect.left + 10, item_rect.top + 8))
            self.screen.blit(value_surface, value_surface.get_rect(topright=(item_rect.right - 10, item_rect.top + 8)))

    def _draw_preview(self) -> None:
        pygame.draw.rect(self.screen, (14, 18, 32), self.preview_rect, border_radius=12)
        pygame.draw.rect(self.screen, (70, 120, 200), self.preview_rect, width=2, border_radius=12)

        grid_color = (40, 50, 80)
        for i in range(1, 10):
            x = self.preview_rect.left + int(i * self.preview_rect.width / 10)
            y = self.preview_rect.top + int(i * self.preview_rect.height / 10)
            pygame.draw.line(self.screen, grid_color, (x, self.preview_rect.top), (x, self.preview_rect.bottom), 1)
            pygame.draw.line(self.screen, grid_color, (self.preview_rect.left, y), (self.preview_rect.right, y), 1)

        if not self.level.alien_groups:
            hint = self.font_small.render("Add a group to begin editing its path.", True, (170, 180, 200))
            self.screen.blit(hint, hint.get_rect(center=self.preview_rect.center))
            return

        group = self.level.alien_groups[self.selected_group]
        last_point = None
        for idx, point in enumerate(group.path):
            x = self.preview_rect.left + int(point.x * self.preview_rect.width)
            y = self.preview_rect.top + int(point.y * self.preview_rect.height)
            if last_point:
                pygame.draw.line(self.screen, (120, 180, 255), last_point, (x, y), 2)
            radius = 8 if idx == self.selected_path_index else 6
            color = (255, 150, 120) if point.shoot else (130, 200, 255)
            pygame.draw.circle(self.screen, color, (x, y), radius)
            last_point = (x, y)

    def _draw_footer(self) -> None:
        footer_rect = pygame.Rect(0, self.screen_height - 70, self.screen_width, 60)
        pygame.draw.rect(self.screen, (16, 20, 36), footer_rect)
        pygame.draw.line(self.screen, (60, 80, 130), footer_rect.topleft, footer_rect.topright, 2)
        hints = [
            "Arrows: Navigate | Tab: Toggle Focus | N: Add | D: Duplicate | Del: Delete | [ / ] Move",
            "P: Path Mode | LMB: Add/Select | RMB: Remove | Space: Toggle shoot | Ctrl+S: Save | Ctrl+Shift+S: Save As | Ctrl+O: Open",
        ]
        for idx, hint in enumerate(hints):
            surface = self.font_small.render(hint, True, (200, 210, 230))
            self.screen.blit(surface, (20, footer_rect.top + 8 + idx * 22))

    # ------------------------------------------------------------------ #
    # Event loop
    # ------------------------------------------------------------------ #
    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()
                if mods & pygame.KMOD_CTRL:
                    if event.key == pygame.K_s:
                        if mods & pygame.KMOD_SHIFT:
                            self.save_level_as()
                        else:
                            self.save_level()
                    elif event.key == pygame.K_o:
                        ident = self.prompt_text(
                            "Open level (number, name, or path):",
                            self.current_file.name if self.current_file else f"{self.level.level_number:03d}.json",
                        )
                        if ident:
                            self.load_level(ident)
                    elif event.key == pygame.K_n:
                        number = self.prompt_text("New level number:", str(self.level.level_number + 1))
                        if number:
                            level_number = int(number) if number.isdigit() else self.level.level_number + 1
                            self.level = LevelData(level_number, f"Level {level_number}", 1, [])
                            self.current_file = None
                            self.selected_group = 0
                            self.modified = True
                    continue

                if event.key == pygame.K_TAB:
                    self.focus_on_properties = not self.focus_on_properties
                elif event.key == pygame.K_p:
                    self.path_edit_mode = not self.path_edit_mode
                    self.selected_path_index = None
                elif event.key == pygame.K_n:
                    self.add_group()
                elif event.key == pygame.K_d:
                    self.duplicate_group()
                elif event.key == pygame.K_DELETE:
                    self.delete_group()
                elif event.key == pygame.K_LEFTBRACKET:
                    self.move_group(-1)
                elif event.key == pygame.K_RIGHTBRACKET:
                    self.move_group(1)
                elif event.key in (pygame.K_UP, pygame.K_DOWN):
                    if self.path_edit_mode and self.selected_path_index is not None and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        step = 0.01 if not (pygame.key.get_mods() & pygame.KMOD_CTRL) else 0.05
                        self.move_selected_point(0, -step if event.key == pygame.K_UP else step)
                    elif self.focus_on_properties:
                        direction = -1 if event.key == pygame.K_UP else 1
                        self.selected_property = (self.selected_property + direction) % len(PROPERTY_DEFS)
                    else:
                        if self.level.alien_groups:
                            direction = -1 if event.key == pygame.K_UP else 1
                            self.selected_group = (self.selected_group + direction) % len(self.level.alien_groups)
                            self.selected_path_index = None
                elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    direction = -1 if event.key == pygame.K_LEFT else 1
                    if self.path_edit_mode and self.selected_path_index is not None and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        step = 0.01 if not (pygame.key.get_mods() & pygame.KMOD_CTRL) else 0.05
                        self.move_selected_point(-step if direction < 0 else step, 0)
                    elif self.focus_on_properties:
                        self.adjust_property(direction)
                elif event.key == pygame.K_SPACE and self.path_edit_mode and self.selected_path_index is not None:
                    self.toggle_selected_point_shoot()

            if self.path_edit_mode and event.type == pygame.MOUSEBUTTONDOWN:
                if self.preview_rect.collidepoint(event.pos):
                    if event.button == 1:
                        if pygame.key.get_mods() & pygame.KMOD_ALT:
                            self.select_nearest_path_point(event.pos)
                        else:
                            shoot = pygame.key.get_mods() & pygame.KMOD_SHIFT
                            self.add_path_point(event.pos, shoot=bool(shoot))
                    elif event.button == 3:
                        self.remove_nearest_path_point(event.pos)

    # ------------------------------------------------------------------ #
    # Main loop
    # ------------------------------------------------------------------ #
    def run(self) -> None:
        while self.running:
            self.clock.tick(60)
            self.handle_events()
            self.draw()


def main() -> None:
    pygame.init()
    app = LevelEditorApp()
    app.load_level(1)
    app.run()
    pygame.quit()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
