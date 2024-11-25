import os

import pygame

from sakura.interface.Player import Player
from sakura.config.sakura_logging import logger

class DemoPlayer(Player):
    key_mapping = {
        "C": "0", "D": "1", "E": "2", "F": "3", "G": "4",
        "A": "5", "B": "6", "C1": "7", "D1": "8", "E1": "9",
        "F1": "10", "G1": "11", "A1": "12", "B1": "13", "C2": "14"
    }

    def __init__(self, conf):
        super().__init__(conf)
        self._audio_initialized = False
        self.audio = []
        self.channels = []
        self.num_channels = 0
        self._channel_index = 0
        
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

    def _initialize_audio(self, conf):
        try:
            if not self._audio_initialized:
                self.num_channels = pygame.mixer.get_num_channels()
                self.channels = [pygame.mixer.Channel(i) for i in range(self.num_channels)]
                
                instruments_path = os.path.join(
                    os.getcwd(), 
                    f'resources/Instruments/{conf.player.instruments}'
                )
                
                for i in range(15):
                    sound_file = os.path.join(instruments_path, f'{i}.wav')
                    if not os.path.exists(sound_file):
                        raise FileNotFoundError(f"Sound file not found: {sound_file}")
                    
                    sound = pygame.mixer.Sound(sound_file)
                    sound.set_volume(conf.player.volume)  # Unified volume for all notes
                    self.audio.append(sound)
                
                self._audio_initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize audio: {e}")
            raise

    def press(self, key, conf):
        try:
            if not self._audio_initialized:
                self._initialize_audio(conf)
                
            note = self.key_mapping[key]
            channel = self.channels[self._channel_index]
            
            channel.play(self.audio[int(note)])
            
            self._channel_index = (self._channel_index + 1) % self.num_channels
            
        except Exception as e:
            logger.error(f"Error playing audio sound: {e}")

    def cleanup(self):
        """Proper cleanup of audio resources"""
        try:
            if self._audio_initialized and pygame.mixer.get_init():
                pygame.mixer.stop()
                
                for sound in self.audio:
                    del sound
                self.audio.clear()
                self.channels.clear()
                
                self._audio_initialized = False
        except Exception as e:
            logger.error(f"Error in audio cleanup: {e}")

    def __del__(self):
        self.cleanup()
