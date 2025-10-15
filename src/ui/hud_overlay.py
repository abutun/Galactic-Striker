import pygame
from typing import Optional, Tuple


class HUDOverlay:
    """Draws an elevated-looking HUD with player and score information."""

    def __init__(self, screen_size: Tuple[int, int]):
        self.screen_width, self.screen_height = screen_size

        # Visual constants
        self.panel_color = (18, 24, 42, 205)
        self.panel_border_color = (70, 150, 240)
        self.panel_border_width = 2
        self.combo_flash_interval = 220  # milliseconds

        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)

        # Animation helpers
        self._last_flash_switch = pygame.time.get_ticks()
        self._combo_flash_on = True

    def resize(self, screen_size: Tuple[int, int]) -> None:
        """Update cached screen metrics when the window size changes."""
        self.screen_width, self.screen_height = screen_size

    def draw(
        self,
        surface: pygame.Surface,
        player: Optional[pygame.sprite.Sprite],
        score_manager,
        level_manager,
        paused: bool = False,
    ) -> None:
        """Render the full HUD overlay."""
        self._update_flash_state()

        self._draw_score_block(surface, score_manager, level_manager, player)
        self._draw_player_block(surface, player)
        self._draw_combo_block(surface, score_manager, paused)
        self._draw_footer(surface)

    # ------------------------------------------------------------------ #
    # Panel helpers
    # ------------------------------------------------------------------ #
    def _draw_panel(self, size: Tuple[int, int]) -> pygame.Surface:
        panel = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(
            panel,
            self.panel_color,
            panel.get_rect(),
            border_radius=14,
        )
        pygame.draw.rect(
            panel,
            self.panel_border_color,
            panel.get_rect(),
            width=self.panel_border_width,
            border_radius=14,
        )
        return panel

    def _draw_score_block(
        self,
        surface: pygame.Surface,
        score_manager,
        level_manager,
        player: Optional[pygame.sprite.Sprite],
    ) -> None:
        width = 320
        height = 150
        panel = self._draw_panel((width, height))
        rect = panel.get_rect()
        rect.topleft = (20, 20)

        # Level info
        level_number = getattr(level_manager, "current_level", 1)
        level_name = getattr(getattr(level_manager, "level_data", None), "name", None)
        if not level_name:
            level_name = f"Level {level_number}"
        level_text = self.font_small.render(level_name.upper(), True, (160, 200, 255))
        panel.blit(level_text, (20, 20))

        # Score and high score
        score_value = self.font_large.render(f"{score_manager.score:,}", True, (255, 255, 255))
        score_label = self.font_small.render("Score", True, (120, 160, 220))
        panel.blit(score_label, (20, 48))
        panel.blit(score_value, (20, 72))

        high_score_value = self.font_medium.render(f"High {score_manager.high_score:,}", True, (200, 215, 255))
        panel.blit(high_score_value, (20, 112))

        if player and hasattr(player, "money"):
            money_surface = self.font_small.render(f"Credits {player.money:,}", True, (190, 240, 180))
            panel.blit(money_surface, (width - money_surface.get_width() - 20, 112))

        surface.blit(panel, rect)

    def _draw_player_block(self, surface: pygame.Surface, player: Optional[pygame.sprite.Sprite]) -> None:
        width = 360
        height = 130
        panel = self._draw_panel((width, height))
        rect = panel.get_rect()
        rect.bottomleft = (20, self.screen_height - 20)

        if player and hasattr(player, "life"):
            # Lives
            lives_label = self.font_small.render("Lives", True, (140, 190, 255))
            panel.blit(lives_label, (20, 18))
            self._draw_life_hearts(panel, (20, 44), getattr(player, "life", 0), getattr(player, "max_life", 3))

            stats_y = 84
            shield_value = getattr(player, "shield", 0)
            rockets_value = getattr(player, "rockets", 0)
            weapon_level = getattr(player, "primary_weapon", 1)

            stats_text = [
                self.font_small.render(f"Shield {shield_value}", True, (200, 230, 255)),
                self.font_small.render(f"Missiles {rockets_value}", True, (200, 230, 255)),
                self.font_small.render(f"Weapon {weapon_level}", True, (200, 230, 255)),
            ]

            for idx, text_surface in enumerate(stats_text):
                panel.blit(text_surface, (20 + idx * 110, stats_y))
        else:
            waiting_text = self.font_medium.render("Awaiting pilot...", True, (220, 230, 255))
            panel.blit(waiting_text, waiting_text.get_rect(center=panel.get_rect().center))

        surface.blit(panel, rect)

    def _draw_combo_block(self, surface: pygame.Surface, score_manager, paused: bool) -> None:
        width = 240
        height = 140
        panel = self._draw_panel((width, height))
        rect = panel.get_rect()
        rect.topright = (self.screen_width - 20, 20)

        # Title
        state_label = "Paused" if paused else "Multiplier"
        label_color = (255, 220, 120) if paused else (150, 200, 255)
        label_surface = self.font_small.render(state_label.upper(), True, label_color)
        panel.blit(label_surface, (20, 20))

        if paused:
            paused_text = self.font_large.render("||", True, (255, 220, 120))
            panel.blit(paused_text, (width // 2 - paused_text.get_width() // 2, 58))
        else:
            multiplier_value = getattr(score_manager, "multiplier", 1)
            if multiplier_value > 1 and abs(multiplier_value - round(multiplier_value)) > 0.01:
                multiplier_text = f"x{multiplier_value:.1f}"
            else:
                multiplier_text = f"x{int(round(max(1, multiplier_value)))}"

            multiplier_surface = self.font_large.render(multiplier_text, True, (255, 255, 255))
            panel.blit(multiplier_surface, (20, 56))

            if getattr(score_manager, "combo", 0) > 1:
                combo_color = (255, 140, 90) if self._combo_flash_on else (255, 220, 180)
                combo_surface = self.font_medium.render(f"COMBO {score_manager.combo}", True, combo_color)
                panel.blit(combo_surface, (20, 98))
            else:
                hint_surface = self.font_small.render("Keep streaking!", True, (180, 205, 255))
                panel.blit(hint_surface, (20, 102))

        surface.blit(panel, rect)

    def _draw_footer(self, surface: pygame.Surface) -> None:
        footer_text = "ESC Pause  •  ENTER Resume  •  R Restart  •  Q Quit"
        footer_surface = self.font_small.render(footer_text, True, (180, 195, 230))
        footer_rect = footer_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 26))
        surface.blit(footer_surface, footer_rect)

    def _draw_life_hearts(self, surface: pygame.Surface, start_pos: Tuple[int, int], life: int, max_life: int) -> None:
        x, y = start_pos
        spacing = 26
        for i in range(max_life):
            filled = i < life
            color = (255, 105, 130) if filled else (80, 80, 90)
            border_color = (255, 220, 230) if filled else (120, 120, 130)
            center = (x + i * spacing, y)
            pygame.draw.circle(surface, color, center, 8)
            pygame.draw.circle(surface, border_color, center, 8, width=2)

    def _update_flash_state(self) -> None:
        now = pygame.time.get_ticks()
        if now - self._last_flash_switch >= self.combo_flash_interval:
            self._combo_flash_on = not self._combo_flash_on
            self._last_flash_switch = now
