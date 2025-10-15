import math
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Sequence, Tuple, Union

import pygame


SettingValue = Union[float, int, bool, str]


@dataclass
class SettingOption:
    label: str
    getter: Callable[[], SettingValue]
    setter: Callable[[SettingValue], None]
    kind: str = "toggle"  # toggle | range | choice
    step: float = 0.1
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    choices: Optional[Sequence[SettingValue]] = None
    formatter: Optional[Callable[[SettingValue], str]] = None
    description: Optional[str] = None
    _pulse_offset: float = field(default=0.0, init=False, repr=False)

    def formatted_value(self) -> str:
        value = self.getter()
        if self.formatter:
            return self.formatter(value)
        if self.kind == "toggle":
            return "ON" if bool(value) else "OFF"
        if isinstance(value, float):
            return f"{value:.2f}"
        return str(value)


class SettingsMenu:
    """Lightweight in-game settings overlay."""

    def __init__(self, screen_size: Tuple[int, int]):
        self.screen_width, self.screen_height = screen_size
        self.active = False
        self.options: List[SettingOption] = []
        self.selected_index = 0

        self.title_font = pygame.font.Font(None, 68)
        self.item_font = pygame.font.Font(None, 36)
        self.desc_font = pygame.font.Font(None, 24)

        self.backdrop = pygame.Surface(screen_size, pygame.SRCALPHA)
        self.backdrop.fill((8, 12, 28, 220))
        self.panel_rect = pygame.Rect(0, 0, int(self.screen_width * 0.6), int(self.screen_height * 0.7))
        self.panel_rect.center = (self.screen_width // 2, self.screen_height // 2)

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #
    def open(self) -> None:
        self.active = True
        pygame.mouse.set_visible(True)

    def close(self) -> None:
        self.active = False
        pygame.mouse.set_visible(False)

    def toggle(self) -> None:
        if self.active:
            self.close()
        else:
            self.open()

    def resize(self, screen_size: Tuple[int, int]) -> None:
        self.screen_width, self.screen_height = screen_size
        self.backdrop = pygame.Surface(screen_size, pygame.SRCALPHA)
        self.backdrop.fill((8, 12, 28, 220))
        self.panel_rect = pygame.Rect(0, 0, int(self.screen_width * 0.6), int(self.screen_height * 0.7))
        self.panel_rect.center = (self.screen_width // 2, self.screen_height // 2)

    # ------------------------------------------------------------------ #
    # Options
    # ------------------------------------------------------------------ #
    def add_option(
        self,
        label: str,
        getter: Callable[[], SettingValue],
        setter: Callable[[SettingValue], None],
        *,
        kind: str = "toggle",
        step: float = 0.1,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        choices: Optional[Sequence[SettingValue]] = None,
        formatter: Optional[Callable[[SettingValue], str]] = None,
        description: Optional[str] = None,
    ) -> None:
        option = SettingOption(
            label=label,
            getter=getter,
            setter=setter,
            kind=kind,
            step=step,
            min_value=min_value,
            max_value=max_value,
            choices=choices,
            formatter=formatter,
            description=description,
        )
        self.options.append(option)

    # ------------------------------------------------------------------ #
    # Interaction
    # ------------------------------------------------------------------ #
    def handle_event(self, event: pygame.event.Event) -> None:
        if not self.active or not self.options:
            return

        option = self.options[self.selected_index]
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_s):
                self.close()
            elif event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key == pygame.K_LEFT:
                self._adjust_option(option, -1)
            elif event.key == pygame.K_RIGHT:
                self._adjust_option(option, 1)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._activate_option(option)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_mouse_click(event.pos)

    def _handle_mouse_click(self, pos: Tuple[int, int]) -> None:
        if not self.panel_rect.collidepoint(pos):
            self.close()
            return

        item_height = 60
        top = self.panel_rect.top + 110
        relative_y = pos[1] - top
        index = relative_y // item_height
        if 0 <= index < len(self.options):
            self.selected_index = int(index)
            option = self.options[self.selected_index]
            center_line = top + self.selected_index * item_height + item_height // 2
            if pos[0] > self.panel_rect.centerx:
                self._adjust_option(option, 1)
            else:
                self._adjust_option(option, -1)

    def _activate_option(self, option: SettingOption) -> None:
        if option.kind == "toggle":
            option.setter(not bool(option.getter()))
        elif option.kind == "choice":
            self._adjust_option(option, 1)

    def _adjust_option(self, option: SettingOption, direction: int) -> None:
        value = option.getter()
        if option.kind == "toggle":
            option.setter(not bool(value))
            return

        if option.kind == "choice" and option.choices:
            choices = list(option.choices)
            try:
                idx = choices.index(value)
            except ValueError:
                idx = 0
            idx = (idx + direction) % len(choices)
            option.setter(choices[idx])
            return

        if option.kind == "range":
            step = option.step * direction
            if isinstance(value, int):
                new_value = value + int(step)
            else:
                new_value = value + step
            if option.min_value is not None:
                new_value = max(option.min_value, new_value)
            if option.max_value is not None:
                new_value = min(option.max_value, new_value)
            option.setter(new_value)

    # ------------------------------------------------------------------ #
    # Rendering
    # ------------------------------------------------------------------ #
    def update(self, dt: float) -> None:
        if not self.active:
            return
        for option in self.options:
            option._pulse_offset = (option._pulse_offset + dt) % 1.0

    def draw(self, surface: pygame.Surface) -> None:
        if not self.active:
            return

        surface.blit(self.backdrop, (0, 0))
        panel_surface = pygame.Surface(self.panel_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (26, 32, 74, 240), panel_surface.get_rect(), border_radius=24)
        pygame.draw.rect(panel_surface, (90, 140, 255, 220), panel_surface.get_rect(), width=2, border_radius=24)

        title = self.title_font.render("SETTINGS", True, (255, 255, 255))
        panel_surface.blit(title, title.get_rect(midtop=(self.panel_rect.width // 2, 20)))

        item_height = 60
        list_top = 110
        for index, option in enumerate(self.options):
            line_rect = pygame.Rect(30, list_top + index * item_height, self.panel_rect.width - 60, item_height - 10)
            is_selected = index == self.selected_index
            if is_selected:
                glow_alpha = 90 + int(40 * math.sin(option._pulse_offset * math.tau))
                pygame.draw.rect(panel_surface, (80, 110, 200, glow_alpha), line_rect, border_radius=14)

            label_surface = self.item_font.render(option.label, True, (220, 230, 255))
            value_surface = self.item_font.render(option.formatted_value(), True, (255, 255, 255))
            panel_surface.blit(label_surface, label_surface.get_rect(midleft=(line_rect.left + 10, line_rect.centery)))
            panel_surface.blit(value_surface, value_surface.get_rect(midright=(line_rect.right - 10, line_rect.centery)))

            if option.description and is_selected:
                desc_surface = self.desc_font.render(option.description, True, (180, 195, 230))
                panel_surface.blit(desc_surface, (line_rect.left, line_rect.bottom + 6))

        hints = [
            "Arrow Keys: Navigate / Adjust",
            "Enter: Toggle / Apply",
            "S or ESC: Close",
        ]
        for idx, hint in enumerate(hints):
            hint_surface = self.desc_font.render(hint, True, (170, 185, 220))
            hint_rect = hint_surface.get_rect(midbottom=(self.panel_rect.width // 2, self.panel_rect.height - 20 - idx * 22))
            panel_surface.blit(hint_surface, hint_rect)

        surface.blit(panel_surface, self.panel_rect)
