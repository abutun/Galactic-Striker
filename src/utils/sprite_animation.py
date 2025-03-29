import pygame

class SpriteAnimation:
    def __init__(self, sprite_sheet, frame_width, frame_height, rows, cols):
        self.sprite_sheet = sprite_sheet
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.rows = rows
        self.cols = cols
        self.frames = []
        self.current_frame = 0
        self.animation_speed = 0.2  # Seconds per frame
        self.last_update = 0
        
        # Extract frames from sprite sheet
        self._extract_frames()
    
    def _extract_frames(self):
        for row in range(self.rows):
            for col in range(self.cols):
                x = col * self.frame_width
                y = row * self.frame_height
                frame = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
                frame.blit(self.sprite_sheet, (0, 0), (x, y, self.frame_width, self.frame_height))
                self.frames.append(frame)
    
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed * 1000:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)
    
    def get_current_frame(self):
        return self.frames[self.current_frame] 