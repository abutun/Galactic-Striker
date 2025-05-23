import pygame

class SpriteAnimation:
    def __init__(self, sprite_sheet, frame_width, frame_height, rows, cols, frames=None):
        self.sprite_sheet = sprite_sheet
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.rows = rows
        self.cols = cols
        self.current_frame = 0
        self.animation_speed = 0.1  # Seconds per frame
        self.last_update = 0
        
        # Use provided frames or extract new ones
        if frames is not None:
            self.frames = frames
        else:
            self.frames = []
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

    def copy(self):
        """Create a copy of the animation that shares the same frames but has independent counters"""
        return SpriteAnimation(
            sprite_sheet=self.sprite_sheet,
            frame_width=self.frame_width,
            frame_height=self.frame_height,
            rows=self.rows,
            cols=self.cols,
            frames=self.frames  # Pass the existing frames to avoid re-extraction
        ) 