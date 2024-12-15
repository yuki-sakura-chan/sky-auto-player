import os
from functools import lru_cache
from typing import Dict, List, Optional
import time
import soundfile as sf

import pygame

from sakura.interface.Player import Player
from sakura.config.sakura_logging import logger


class DemoPlayer(Player):
    key_mapping = {
        "C": "0", "D": "1", "E": "2", "F": "3", "G": "4",
        "A": "5", "B": "6", "C1": "7", "D1": "8", "E1": "9",
        "F1": "10", "G1": "11", "A1": "12", "B1": "13", "C2": "14"
    }

    SUPPORTED_AUDIO_FORMATS = ['.mp3', '.wav', '.ogg', '.flac']

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
            
            buffer=1024         # Audio buffer size in bytes
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
        """Initialize audio system, load sound files and set up audio channels"""
        try:
            if not self._audio_initialized:
                self.num_channels = pygame.mixer.get_num_channels()
                self.channels = [pygame.mixer.Channel(i) for i in range(self.num_channels)]
                
                instruments_path = os.path.normpath(os.path.join(
                    os.getcwd(), 
                    'resources',
                    'Instruments',
                    conf.player.source,
                    conf.player.instruments
                ))
                
                logger.info(f"Loading instrument from: {instruments_path}")
                
                if not os.path.exists(instruments_path):
                    raise FileNotFoundError(f"Instrument directory not found: {instruments_path}")
                
                # Initialize audio list with None values
                self.audio = [None] * 15
                
                # Load sounds on demand
                for i in range(15):
                    try:
                        sound_file = self._find_audio_file(instruments_path, i)
                        sound = self._load_sound(sound_file)
                        sound.set_volume(self._base_volume)
                        self.audio[i] = sound
                        self._audio_cache[str(i)] = sound
                    except FileNotFoundError as e:
                        logger.error(f"Failed to load audio file: {e}")
                        raise
                
                self._audio_initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize audio: {e}")
            raise

    @lru_cache(maxsize=15)
    def _load_sound(self, sound_path: str) -> pygame.mixer.Sound:
        """Load and cache sound file"""
        if not os.path.exists(sound_path):
            raise FileNotFoundError(f"Sound file not found: {sound_path}")
        return pygame.mixer.Sound(sound_path)

    def _convert_to_wav(self, input_path: str) -> str:
        """
        Convert audio file to WAV format for compatibility.
        Only converts if file isn't already WAV format.
        
        Args:
            input_path: Path to input audio file
        Returns:
            Path to WAV file (either converted or original)
        """
        try:
            # Skip if already WAV
            if input_path.lower().endswith('.wav'):
                return input_path
                
            directory = os.path.dirname(input_path)
            filename = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(directory, f"{filename}.wav")
            
            # Convert only if output doesn't exist
            if not os.path.exists(output_path):
                # Read audio file
                data, sample_rate = sf.read(input_path)
                # Write WAV file with original settings
                sf.write(
                    output_path,
                    data,
                    sample_rate,
                    format='WAV'
                )
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error converting audio to WAV: {e}")
            return input_path

    def _find_audio_file(self, base_path: str, index: int) -> str:
        """
        Find first available audio file with supported format.
        Converts found file to WAV format if needed.
        
        Args:
            base_path: Directory to search in
            index: Note index to find
        Returns:
            Path to found audio file
        """
        for format in self.SUPPORTED_AUDIO_FORMATS:
            file_path = os.path.join(base_path, f'{index}{format}')
            if os.path.exists(file_path):
                # Convert to WAV before returning
                return self._convert_to_wav(file_path)
                
        raise FileNotFoundError(
            f"No supported audio file found for note {index} in {base_path}. "
            f"Supported formats: {', '.join(self.SUPPORTED_AUDIO_FORMATS)}"
        )

    def _find_available_channel(self) -> pygame.mixer.Channel:
        """
        Find first available channel or least recently used one.
        Uses round-robin selection if all channels are busy.
        
        Returns:
            pygame.mixer.Channel object for sound playback
        """
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
        """
        Play sound corresponding to pressed key.
        Initializes audio if not already initialized.
        
        Args:
            key: Key identifier
            conf: Configuration object
        """
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
        """
        Set volume level for all sounds.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
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
        """Destructor to ensure cleanup is called when object is destroyed"""
        try:
            self.cleanup()
        except:
            pass
