import math
from typing import Optional, Tuple

import pygame


class LevelIntroOverlay:
    """Non-blocking level intro countdown overlay."""

    def __init__(
        self,
        level_number: int,
        level_name: Optional[str] = None,
        countdown_seconds: float = 3.0,
        hold_seconds: float = 1.0,
        screen_size: Optional[Tuple[int, int]] = None,
    ):
        self.level_number = level_number
        self.level_name = level_name or f"Level {level_number}"
        self.countdown_seconds = countdown_seconds
        self.hold_seconds = hold_seconds
        self.elapsed = 0.0
        self.spawn_triggered = False

        width, height = screen_size if screen_size else pygame.display.get_surface().get_size()
        self.overlay_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        self.title_font = pygame.font.Font(None, 96)
        self.count_font = pygame.font.Font(None, 120)
        self.detail_font = pygame.font.Font(None, 36)

    def resize(self, screen_size: Tuple[int, int]) -> None:
        self.overlay_surface = pygame.Surface(screen_size, pygame.SRCALPHA)

    def update(self, dt: float) -> None:
        self.elapsed += dt

    def should_spawn(self) -> bool:
        return (not self.spawn_triggered) and self.elapsed >= self.countdown_seconds

    def mark_spawned(self) -> None:
        self.spawn_triggered = True

    def is_finished(self) -> bool:
        total_required = self.countdown_seconds + self.hold_seconds
        return self.spawn_triggered and self.elapsed >= total_required

    def draw(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        self.overlay_surface.fill((10, 12, 24, 180))

        title = self.title_font.render(self.level_name.upper(), True, (255, 255, 255))
        title_rect = title.get_rect(center=(width // 2, height // 2 - 120))
        self.overlay_surface.blit(title, title_rect)

        remaining = max(0.0, self.countdown_seconds - self.elapsed)
        countdown_value = max(0, math.ceil(remaining))
        countdown_text = self.count_font.render(str(countdown_value), True, (255, 215, 120))
        countdown_rect = countdown_text.get_rect(center=(width // 2, height // 2))
        self.overlay_surface.blit(countdown_text, countdown_rect)

        if self.spawn_triggered:
            message = "Engage!"
            if self.hold_seconds > 0:
                progress = (self.elapsed - self.countdown_seconds) / self.hold_seconds
            else:
                progress = 1.0
            alpha = max(0, 255 - int(255 * progress))
            engage_text = self.count_font.render(message, True, (180, 235, 255))
            engage_text.set_alpha(alpha)
            self.overlay_surface.blit(engage_text, engage_text.get_rect(center=(width // 2, height // 2 + 120)))
        else:
            detail = self.detail_font.render("Prepare for incoming hostiles...", True, (210, 220, 255))
            self.overlay_surface.blit(detail, detail.get_rect(center=(width // 2, height // 2 + 120)))

        surface.blit(self.overlay_surface, (0, 0))
