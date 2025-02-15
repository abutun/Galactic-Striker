from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import pygame
import logging

logger = logging.getLogger(__name__)

class GameState(ABC):
    @abstractmethod
    def update(self, dt: float) -> None:
        pass
    
    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        pass
    
    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        pass

class PlayingState(GameState):
    def __init__(self, game_context: Dict[str, Any]):
        self.game_context = game_context
        self.paused = False
        
    def update(self, dt: float) -> None:
        if self.paused:
            return
            
        try:
            self.game_context['all_sprites'].update()
            self.game_context['level_manager'].update()
            self.game_context['score_manager'].update(dt)
        except Exception as e:
            logger.error(f"Error updating game state: {e}")
            
    def draw(self, screen: pygame.Surface) -> None:
        try:
            self.game_context['background'].draw(screen)
            self.game_context['all_sprites'].draw(screen)
            self.game_context['score_manager'].draw(screen)
        except Exception as e:
            logger.error(f"Error drawing game state: {e}")
            
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.paused = not self.paused

class GameStateManager:
    def __init__(self):
        self.states: Dict[str, GameState] = {}
        self.current_state: Optional[str] = None
        
    def add_state(self, name: str, state: GameState) -> None:
        self.states[name] = state
        
    def set_state(self, name: str) -> None:
        if name in self.states:
            self.current_state = name
        else:
            logger.error(f"Attempted to set unknown state: {name}")
            
    def update(self, dt: float) -> None:
        if self.current_state:
            self.states[self.current_state].update(dt)
            
    def draw(self, screen: pygame.Surface) -> None:
        if self.current_state:
            self.states[self.current_state].draw(screen)
            
    def handle_event(self, event: pygame.event.Event) -> None:
        if self.current_state:
            self.states[self.current_state].handle_event(event) 