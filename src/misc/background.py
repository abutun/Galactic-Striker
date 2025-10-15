import math
import random
from dataclasses import dataclass
from typing import List, Tuple

import pygame

from src.config.game_settings import PLAY_AREA


@dataclass
class Star:
    x: float
    y: float
    speed: float
    radius: int
    color: Tuple[int, int, int, int]
    twinkle_speed: float
    twinkle_phase: float


class Background:
    """Procedurally generated starfield background with animated borders."""

    def __init__(self, width: int, height: int, scroll_speed: float = 1.0, density: float = 0.00025):
        self.screen_width = width
        self.screen_height = height
        self.scroll_speed = scroll_speed
        self.star_density = density

        self.play_area_left = int(width * PLAY_AREA.get("left_boundary", 0.115))
        self.play_area_right = int(width * PLAY_AREA.get("right_boundary", 0.885))
        self.play_area_width = self.play_area_right - self.play_area_left
        self.border_width = self.play_area_left

        self._glow_cache = {}
        self._create_star_layers()
        self._init_border_surfaces()

        self.border_wave_phase = 0.0
        self.border_wave_speed = 1.4
        self._blend_mode = getattr(pygame, "BLEND_PREMULTIPLIED", pygame.BLEND_ADD)

    # ------------------------------------------------------------------ #
    # Starfield generation
    # ------------------------------------------------------------------ #
    def _create_star_layers(self) -> None:
        base_count = max(120, int(self.screen_width * self.screen_height * self.star_density))
        layer_specs = [
            {"count": int(base_count * 0.6), "speed": 32, "radius": (1, 2), "alpha": (130, 190)},
            {"count": int(base_count * 0.4), "speed": 60, "radius": (2, 3), "alpha": (170, 230)},
        ]

        self.star_layers: List[List[Star]] = []
        for spec in layer_specs:
            stars: List[Star] = []
            for _ in range(spec["count"]):
                radius = random.randint(*spec["radius"])
                alpha = random.randint(*spec["alpha"])
                color = random.choice([(220, 230, 255, alpha), (200, 210, 255, alpha), (255, 240, 220, alpha)])
                star = Star(
                    x=random.uniform(self.play_area_left, self.play_area_right),
                    y=random.uniform(0, self.screen_height),
                    speed=spec["speed"] * random.uniform(0.6, 1.4),
                    radius=radius,
                    color=color,
                    twinkle_speed=random.uniform(1.0, 2.5),
                    twinkle_phase=random.uniform(0, math.tau),
                )
                stars.append(star)
            self.star_layers.append(stars)

    def _init_border_surfaces(self) -> None:
        """Precompute base gradient surfaces for borders."""
        self.left_border_base = self._create_border_surface(self.border_width, self.screen_height, is_left=True)
        self.right_border_base = self._create_border_surface(self.border_width, self.screen_height, is_left=False)
        self.border_effect_surface = pygame.Surface((self.border_width, self.screen_height), pygame.SRCALPHA)

    @staticmethod
    def _create_border_surface(width: int, height: int, is_left: bool) -> pygame.Surface:
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        for x in range(width):
            t = x / max(1, width - 1)
            if not is_left:
                t = 1 - t
            base_color = (
                int(25 + 40 * (1 - t)),
                int(40 + 70 * (1 - t)),
                int(70 + 120 * (1 - t)),
                255,
            )
            pygame.draw.line(surface, base_color, (x, 0), (x, height))
        return surface

    def set_density(self, density: float) -> None:
        """Adjust star density and regenerate layers."""
        self.star_density = max(0.00005, min(0.0015, density))
        self._create_star_layers()

    # ------------------------------------------------------------------ #
    # Update & draw
    # ------------------------------------------------------------------ #
    def update(self, dt: float) -> None:
        """Update star positions and animated border accents."""
        scroll_multiplier = self.scroll_speed * dt
        for stars in self.star_layers:
            for star in stars:
                star.y += star.speed * scroll_multiplier
                star.twinkle_phase += star.twinkle_speed * dt

                if star.y > self.screen_height:
                    star.y = -random.uniform(5, 40)
                    star.x = random.uniform(self.play_area_left, self.play_area_right)

        self.border_wave_phase = (self.border_wave_phase + self.border_wave_speed * dt) % math.tau

    def draw(self, screen: pygame.Surface) -> None:
        """Render the starfield within the play area."""
        # Fill play area with deep-space gradient
        play_area_rect = pygame.Rect(self.play_area_left, 0, self.play_area_width, self.screen_height)
        pygame.draw.rect(screen, (6, 10, 24), play_area_rect)

        for stars in self.star_layers:
            for star in stars:
                self._draw_star(screen, star)

    def _draw_star(self, screen: pygame.Surface, star: Star) -> None:
        radius = star.radius
        glow_surface = self._get_glow_surface(radius, star.color)

        # Twinkle by modulating alpha
        alpha_variation = 0.4 * math.sin(star.twinkle_phase)
        current_alpha = max(20, min(255, int(star.color[3] * (0.7 + alpha_variation))))
        glow_surface.set_alpha(current_alpha)

        rect = glow_surface.get_rect(center=(int(star.x), int(star.y)))
        screen.blit(glow_surface, rect)

    def _get_glow_surface(self, radius: int, color: Tuple[int, int, int, int]) -> pygame.Surface:
        key = (radius, color[:3])
        if key in self._glow_cache:
            return self._glow_cache[key]

        size = radius * 6
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        max_radius = size // 2
        for r in range(max_radius, 0, -1):
            fade = (r / max_radius) ** 3
            alpha = int(color[3] * fade)
            pygame.draw.circle(surface, (*color[:3], alpha), (center, center), r)
        self._glow_cache[key] = surface
        return surface

    def draw_borders(self, screen: pygame.Surface) -> None:
        """Render animated borders with energy pulses."""
        # Base gradient
        screen.blit(self.left_border_base, (0, 0))
        screen.blit(self.right_border_base, (self.screen_width - self.border_width, 0))

        # Animated pulses
        self.border_effect_surface.fill((0, 0, 0, 0))

        pulse_height = 80
        for offset in range(0, self.screen_height + pulse_height, pulse_height):
            phase = self.border_wave_phase + offset * 0.04
            brightness = 60 + int(40 * (math.sin(phase) + 1) / 2)
            base_values = (80 + brightness, 110 + brightness, 220 + brightness)
            clamped_rgb = tuple(max(0, min(255, value)) for value in base_values)
            color = (*clamped_rgb, 120)
            pygame.draw.rect(
                self.border_effect_surface,
                color,
                pygame.Rect(0, (offset + int(phase * 20)) % (self.screen_height + pulse_height) - pulse_height, self.border_width, 16),
            )

        screen.blit(self.border_effect_surface, (0, 0), special_flags=self._blend_mode)
        screen.blit(
            pygame.transform.flip(self.border_effect_surface, True, False),
            (self.screen_width - self.border_width, 0),
            special_flags=self._blend_mode,
        )
