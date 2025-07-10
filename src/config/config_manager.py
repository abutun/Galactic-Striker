import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """Centralized configuration manager for game settings."""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config: Dict[str, Any] = {}
        self.default_config = self._get_default_config()
        self.load_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            "display": {
                "screen_width": 1920,
                "screen_height": 1080,
                "fullscreen": True,
                "vsync": True,
                "fps": 60
            },
            "audio": {
                "music_volume": 0.7,
                "sfx_volume": 0.8,
                "master_volume": 1.0,
                "enable_audio": True
            },
            "gameplay": {
                "difficulty": 1,
                "auto_save": True,
                "dev_mode": False,
                "show_fps": False,
                "pause_on_focus_loss": True
            },
            "controls": {
                "left": "LEFT",
                "right": "RIGHT",
                "fire": "SPACE",
                "secondary_fire": "LSHIFT",
                "pause": "p",
                "menu": "ESCAPE"
            },
            "performance": {
                "max_particles": 500,
                "max_bullets": 200,
                "enable_object_pooling": True,
                "particle_quality": "high",
                "enable_vsync": True
            },
            "debug": {
                "show_debug_info": False,
                "log_level": "INFO",
                "enable_profiling": False,
                "show_hitboxes": False
            }
        }
    
    def load_config(self):
        """Load configuration from file or create default."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    self.config = self._merge_config(self.default_config, loaded_config)
            else:
                self.config = self.default_config.copy()
                self.save_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.config = self.default_config.copy()
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'display.screen_width')."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value using dot notation."""
        keys = key.split('.')
        config_ref = self.config
        
        for k in keys[:-1]:
            if k not in config_ref:
                config_ref[k] = {}
            config_ref = config_ref[k]
        
        config_ref[keys[-1]] = value
    
    def _merge_config(self, default: Dict, loaded: Dict) -> Dict:
        """Merge loaded config with default config."""
        result = default.copy()
        
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def reset_to_defaults(self):
        """Reset configuration to default values."""
        self.config = self.default_config.copy()
        self.save_config()
    
    def get_display_settings(self) -> Dict[str, Any]:
        """Get display-related settings."""
        return self.config.get("display", {})
    
    def get_audio_settings(self) -> Dict[str, Any]:
        """Get audio-related settings."""
        return self.config.get("audio", {})
    
    def get_gameplay_settings(self) -> Dict[str, Any]:
        """Get gameplay-related settings."""
        return self.config.get("gameplay", {})
    
    def get_control_settings(self) -> Dict[str, Any]:
        """Get control-related settings."""
        return self.config.get("controls", {})


# Global instance
config_manager = ConfigManager() 