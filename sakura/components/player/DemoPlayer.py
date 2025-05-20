import os
import time
from functools import lru_cache
from typing import Dict, List, Optional

import pygame

from sakura.config.sakura_logging import logger
from sakura.interface.Player import Player


class DemoPlayer(Player):
    key_mapping = {
        "C4": "0", "D4": "1", "E4": "2", "F4": "3", "G4": "4",
        "A4": "5", "B4": "6", "C5": "7", "D5": "8", "E5": "9",
        "F5": "10", "G5": "11", "A5": "12", "B5": "13", "C6": "14"
    }

    def __init__(self, conf):
        super().__init__(conf)
        self._audio_initialized = False
        self._audio_cache: Dict[str, pygame.mixer.Sound] = {}
        self.audio: List[Optional[pygame.mixer.Sound]] = []
        self.channels: List[pygame.mixer.Channel] = []
        self.num_channels = 0
        self._channel_index = 0
        self._base_volume = conf.player.volume
        
        pygame.init()
        
        # pre_init configures audio parameters before mixer initialization
        pygame.mixer.pre_init(
            frequency=44100,    # Sampling frequency in Hz (samples per second)
                                # Common values:
                                # 8000  - Telephone quality
                                # 22050 - FM radio quality
                                # 32000 - DAT quality
                                # 44100 - CD quality (standard)
                                # 48000 - DVD/Professional quality
                                # 96000 - HD audio
                                # 192000 - Studio quality
                                # Higher frequency = better quality but more memory usage
            
            size=-16,           # Sound bit depth (bits per sample)
                                # Available values:
                                # ±8  - 8-bit (low quality, less memory)
                                # ±16 - 16-bit (CD quality, standard)
                                # ±24 - 24-bit (professional quality)
                                # ±32 - 32-bit (studio quality)
                                # Negative values = signed integers
                                # Positive values = unsigned integers
                                # Higher bit depth = better dynamic range but more memory
            
            channels=2,         # Number of audio channels
                                # Available options:
                                # 1 - Mono (single channel)
                                # 2 - Stereo (left + right, standard)
                                # 4 - Quadraphonic
                                # 6 - 5.1 Surround sound
                                # 8 - 7.1 Surround sound
                                # More channels = better spatial audio but more memory
            
            buffer=2048         # Audio buffer size in bytes
                                # Common values:
                                # 256  - Minimal latency, highest CPU usage
                                # 512  - Low latency
                                # 1024 - Balanced latency/CPU usage
                                # 2048 - Standard buffer size
                                # 4096 - High latency, low CPU usage
                                # 8192 - Maximum latency, minimal CPU usage
                                # Smaller buffer = less delay but more CPU load
                                # Larger buffer = more delay but smoother playback
        )
        
        # Configure number of simultaneous sound channels
        pygame.mixer.set_num_channels(32)   # Increase for better polyphony
                                            # Default pygame gives only 8 channels
                                            # 32 channels allow playing more
                                            # simultaneous notes without interruption
        
        self._initialize_audio(conf)

    @lru_cache(maxsize=15)
    def _load_sound(self, sound_path: str) -> pygame.mixer.Sound:
        """Load and cache sound file"""
        if not os.path.exists(sound_path):
            raise FileNotFoundError(f"Sound file not found: {sound_path}")
        return pygame.mixer.Sound(sound_path)

    def _initialize_audio(self, conf):
        try:
            if not self._audio_initialized:
                self.num_channels = pygame.mixer.get_num_channels()
                self.channels = [pygame.mixer.Channel(i) for i in range(self.num_channels)]
                
                instruments_path = os.path.join(
                    os.getcwd(), 
                    f'resources/Instruments/{conf.player.instruments}'
                )
                
                # Initialize audio list with None values
                self.audio = [None] * 15
                
                # Load sounds on demand
                for i in range(15):
                    sound_file = os.path.join(instruments_path, f'{i}.wav')
                    sound = self._load_sound(sound_file)
                    sound.set_volume(self._base_volume)
                    self.audio[i] = sound
                    self._audio_cache[str(i)] = sound
                
                self._audio_initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize audio: {e}")
            raise

    def _find_available_channel(self) -> pygame.mixer.Channel:
        """Find first available channel or least recently used one"""
        # Try to find a free channel first
        for i in range(self.num_channels):
            channel_index = (self._channel_index + i) % self.num_channels
            if not self.channels[channel_index].get_busy():
                self._channel_index = channel_index
                return self.channels[channel_index]
        
        # If no free channels, use round-robin
        self._channel_index = (self._channel_index + 1) % self.num_channels
        return self.channels[self._channel_index]

    def press(self, key, conf):
        try:
            if not self._audio_initialized:
                self._initialize_audio(conf)
                
            note = self.key_mapping[key]
            sound = self._audio_cache.get(note)
            
            if sound is None:
                return
                
            channel = self._find_available_channel()
            channel.play(sound)
            
        except Exception as e:
            logger.error(f"Error playing audio sound: {e}")

    def set_volume(self, volume: float):
        """Set volume for all sounds"""
        try:
            self._base_volume = volume
            for sound in self._audio_cache.values():
                if sound:
                    sound.set_volume(volume)
        except Exception as e:
            logger.error(f"Error setting volume: {e}")

    def cleanup(self):
        """Proper cleanup of audio resources"""
        try:
            if self._audio_initialized and pygame.mixer.get_init():
                # Check if there are active channels
                active_channels = [ch for ch in self.channels if ch.get_busy()]
                
                if active_channels:
                    # Give time for the last notes to play
                    time.sleep(0.75)  # 750 milliseconds
                
                # Stop all channels
                pygame.mixer.stop()
                
                # Clear all channels
                for channel in self.channels:
                    channel.stop()
                
                # Clear sound cache
                self._load_sound.cache_clear()
                
                # Clear and delete sounds
                for sound in self._audio_cache.values():
                    if sound:
                        sound.stop()  # Stop sound
                        del sound
                self._audio_cache.clear()
                
                # Clear audio list
                for i in range(len(self.audio)):
                    if self.audio[i]:
                        self.audio[i].stop()
                        self.audio[i] = None
                
                # Clear channels list
                self.channels.clear()
                
                self._audio_initialized = False
                
        except Exception as e:
            logger.error(f"Error in audio cleanup: {e}")
            
    def __del__(self):
        """Destructor for guaranteed cleanup"""
        try:
            self.cleanup()
        except:
            pass
