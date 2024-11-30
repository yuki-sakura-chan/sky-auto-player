from queue import Queue, Empty
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from itertools import groupby
from typing import Callable, List

from sakura.components.TimeManager import TimeManager
from sakura.config import conf
from sakura.config.sakura_logging import logger
from sakura.interface.Player import Player


class NoteEvent:
    """
    Represents a musical note event with timing and key information
    """
    def __init__(self, time: int, keys: List[str]):
        self.time = time  # Time in milliseconds
        self.keys = keys  # List of keys to be played

class EventQueue:
    """
    Thread-safe queue for managing note events
    """
    def __init__(self):
        self.queue = Queue()
        self._lock = threading.Lock()

    def put(self, event: NoteEvent):
        """Add a new event to the queue thread-safely"""
        with self._lock:
            self.queue.put(event)
 
    def get(self, block=True, timeout=None):
        """Get an event from the queue with optional blocking"""
        return self.queue.get(block=block, timeout=timeout)

    def get_nowait(self):
        """Get an event without blocking, may raise Empty exception"""
        return self.queue.get_nowait()

    def empty(self):
        """Check if the queue is empty"""
        return self.queue.empty()

    def clear(self):
        """Clear all events from the queue"""
        with self._lock:
            while not self.queue.empty():
                try:
                    self.queue.get_nowait()
                except Empty:
                    break

    def load_all(self, events: List[NoteEvent]):
        """Load all notes at once"""
        with self._lock:
            for event in events:
                self.queue.put(event)


class SakuraPlayer:
    """
    Main player class for handling music playback and note events
    """
    def __init__(self, song_notes: list, time_manager: TimeManager, cb: Callable[[], None] = lambda: None):
        """
        Initialize the player with song notes and time management
        
        Args:
            song_notes: List of note events for the song
            time_manager: TimeManager instance for handling playback timing
            cb: Optional callback function called when playback finishes
        """
        self.event_queue = EventQueue()
        self.time_manager = time_manager
        self.cb = cb
        self.is_playing = False
        self.is_finished = False
        self.player = None
        self.key_mapping = None
        self.last_time = 0
        
        self._song_notes = song_notes
        self._playback_thread = None
        self._seek_event = threading.Event()
        self._seeking = False
        self._seek_lock = threading.Lock()
        self._shutdown = threading.Event()

    @contextmanager
    def _thread_pool(self, max_workers: int = 15):
        """
        Context manager for thread pool execution
        
        Args:
            max_workers: Maximum number of concurrent worker threads
        """
        try:
            self._executor = ThreadPoolExecutor(max_workers=max_workers)
            yield self._executor
        finally:
            if self._executor:
                self._executor.shutdown(wait=False)
                self._executor = None

    def _prepare_notes(self, start_time: int = 0) -> List[NoteEvent]:
        """
        Prepare note events starting from specified time
        
        Args:
            start_time: Starting time in milliseconds
        Returns:
            List of NoteEvent objects
        """
        filtered_notes = [
            note for note in self._song_notes
            if note['time'] >= start_time
        ]
        
        return [
            NoteEvent(t, [note['key'] for note in group])
            for t, group in groupby(filtered_notes, key=lambda x: x['time'])
        ]

    def _safe_stop_thread(self, thread: threading.Thread, timeout: float = 0.5):
        """
        Safely stop a thread with timeout
        
        Args:
            thread: Thread to stop
            timeout: Maximum time to wait for thread termination
        """
        if thread and thread.is_alive():
            self._shutdown.set()
            thread.join(timeout=timeout)
            self._shutdown.clear()

    def _playback_worker(self):
        """
        Main worker thread for handling playback events
        Processes events from queue and triggers note playback
        """
        with self._thread_pool() as executor:
            while not self.is_finished and not self._shutdown.is_set():
                try:
                    # Skip processing if seeking is in progress
                    if self._seeking or self._seek_event.is_set():
                        time.sleep(0.1)
                        continue
                    
                    try:
                        # Try to get next event from queue with timeout
                        event = self.event_queue.get(block=True, timeout=0.1)
                    except Empty:
                        # Check if song has ended when queue is empty
                        current_time = self.time_manager.get_current_time()
                        if current_time >= self.last_time - 100:  # Allow 100ms error margin
                            # Song finished - reset player state
                            self.is_finished = True
                            self.is_playing = False
                            self.time_manager.set_playing(False)
                            self.time_manager.force_set_time(0)  # Reset to beginning
                            self.callback()  # Update UI via callback
                        continue
                    
                    # Get current playback time
                    current_time = self.time_manager.get_current_time()
                    
                    # Skip events that are in the past
                    if event.time < current_time:
                        continue
                    
                    # Calculate wait time until next event
                    wait_time = (event.time - current_time) / 1000
                    elapsed_time = 0
                    
                    # Wait loop with periodic checks for seek/stop requests
                    while elapsed_time < wait_time:
                        if self._seek_event.is_set() or self._shutdown.is_set():
                            break
                        if not self.is_playing:
                            time.sleep(0.1)
                            continue
                        sleep_time = min(0.1, wait_time - elapsed_time)
                        time.sleep(sleep_time)
                        elapsed_time += sleep_time

                    # Skip event processing if seeking or shutdown requested
                    if self._seek_event.is_set() or self._shutdown.is_set():
                        continue
                    
                    # Update current time to event time
                    self.time_manager.set_current_time(event.time)
                    
                    # Process each key in the event and submit to thread pool
                    for key in event.keys:
                        if mapped_key := self.key_mapping.get(key):
                            if not self._seek_event.is_set():
                                executor.submit(self.player.press, mapped_key, conf)
                    
                except Exception as e:
                    logger.error(f"Error in playback worker: {e}")
                    if not self._seek_event.is_set():
                        break

    def play(self, player: Player, key_mapping: dict, start_time: int = None):
        """
        Start playback from specified position
        
        Args:
            player: Player instance for actual note playback
            key_mapping: Dictionary mapping note keys to player keys
            start_time: Optional starting position in seconds
        """
        self.stop()
        
        self.player = player
        self.key_mapping = key_mapping
        self.is_finished = False
        self.is_playing = True
        
        start_ms = (start_time or 0) * 1000
        self.time_manager.set_current_time(start_ms)
        self.time_manager.set_duration(self.last_time)
        self.time_manager.set_playing(True)
        
        # Load all notes at once
        notes = self._prepare_notes(start_ms)
        self.event_queue.load_all(notes)
        
        # Start only the playback thread
        self._playback_thread = threading.Thread(
            target=self._playback_worker,
            daemon=True
        )
        self._playback_thread.start()

    def pause(self):
        """Pause the current playback"""
        self.is_playing = False
        self.time_manager.set_playing(False)

    def continue_play(self):
        """Resume playback from current position"""
        if not self.player or not self.key_mapping:
            logger.error("Player or key mapping not initialized")
            return
            
        # If the song has ended, start from the beginning
        if self.is_finished:
            self.is_finished = False
            self.seek(0)  # Rewind to the beginning
        
        self.is_playing = True
        self.time_manager.set_playing(True)

    def stop(self):
        """
        Stop playback and clean up resources
        Thread-safe operation
        """
        try:
            self.is_finished = True
            self.is_playing = False
            self._seek_event.set()
            self._shutdown.set()
            
            if self.time_manager:
                self.time_manager.set_playing(False)
            
            # Clear the queue
            if hasattr(self, 'event_queue') and self.event_queue:
                self.event_queue.clear()
                
            # Stop the playback thread
            if self._playback_thread and self._playback_thread.is_alive():
                self._safe_stop_thread(self._playback_thread)
                self._playback_thread = None
                
            self._seek_event.clear()
            self._shutdown.clear()
            
        except Exception as e:
            logger.error(f"Error stopping playback: {e}")

    def seek(self, position_ms: int):
        """
        Change playback position
        
        Args:
            position_ms: New position in milliseconds
        """
        with self._seek_lock:
            try:
                was_playing = self.is_playing
                self._seek_event.set()
                self._seeking = True
                
                # Fast cleanup of the queue
                self.event_queue.clear()
                
                # Update time immediately
                self.time_manager.force_set_time(position_ms)
                
                # Prepare all notes from the new position
                notes = self._prepare_notes(position_ms)
                
                # Load all notes at once
                self.event_queue.load_all(notes)
                
                # Start only the playback thread
                if self._playback_thread and self._playback_thread.is_alive():
                    self._safe_stop_thread(self._playback_thread)
                    
                self._playback_thread = threading.Thread(
                    target=self._playback_worker,
                    daemon=True
                )
                self._playback_thread.start()
                
                # Immediately restore playback
                if was_playing:
                    self.is_playing = True
                    self.time_manager.set_playing(True)
                    
            finally:
                self._seeking = False
                self._seek_event.clear()

    def callback(self):
        """Called when playback is finished"""
        try:
            self.cleanup()
            if self.cb:
                self.cb()
        except Exception as e:
            logger.error(f"Error in player callback: {e}")

    def cleanup(self, force=False):
        """
        Clean up all resources and stop playback
        
        Args:
            force: If True, forces immediate cleanup regardless of playback state
        """
        try:
            # Stop playback
            self.is_playing = False
            
            if force:
                self.is_finished = True
                self._seek_event.set()
                self._shutdown.set()
                
                # Clear the event queue
                if hasattr(self, 'event_queue') and self.event_queue:
                    self.event_queue.clear()
                    
                # Stop the playback thread
                if self._playback_thread and self._playback_thread.is_alive():
                    self._safe_stop_thread(self._playback_thread)
                    self._playback_thread = None
                    
                # Clean up the player and release resources
                if self.player:
                    self.player.cleanup()
                    self.player = None
                    
                # Clear all references to data
                self._song_notes = None
                self.key_mapping = None
                self.event_queue = None
                
                # Reset flags
                self._seek_event.clear()
                self._shutdown.clear()
                self._seeking = False
                
        except Exception as e:
            logger.error(f"Error in cleanup: {e}")

    def __del__(self):
        """Destructor ensuring cleanup is called"""
        try:
            self.cleanup()
        except:
            pass
