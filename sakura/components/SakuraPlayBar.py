import threading
import time
from decimal import Decimal
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout
from pynput import keyboard
from qfluentwidgets import ListWidget, FluentIcon
from qfluentwidgets.multimedia import StandardMediaPlayBar

from sakura import children_windows
from sakura.components.SpeedControl import SpeedControl
from sakura.components.TimeManager import TimeManager
from sakura.components.mapper.JsonMapper import JsonMapper
from sakura.components.player.SakuraPlayer import SakuraPlayer
from sakura.components.ui import main_width
from sakura.components.ui.BottomRightButton import BottomRightButton
from sakura.config import conf, save_conf
from sakura.config.sakura_logging import logger
from sakura.db.DBManager import song_client
from sakura.factory.PlayerFactory import get_player
from sakura.listener import register_listener
from sakura.registrar.listener_registers import listener_registers


class SakuraPlayBar(StandardMediaPlayBar):
    is_playing: bool = False
    file_list_box: ListWidget
    playing_id: int = 0
    '''
        此变量本意是为了减少重复解析json文件，因为只需要 song_notes 字段 (因为除了 song_notes 字段外，其他字段全是无效字段），
        所以将 SakuraPlayer 对象放到数组中，等用户播放重复性的 song 时，可以跳过 json 解析。
        因为没写注解的原因，可能被他人误解了？反正这件事告诉了我写注释的重要性...
        懒得改了，等哪天心情好改一下
    '''
    sakura_player_dict: dict[int, SakuraPlayer] = {}
    temp_window: QWidget
    temp_layout: QVBoxLayout
    state: str = 'normal'
    _is_dragging: bool = False
    _start_position: Any
    temp_width: int
    wait_time: Decimal = 0
    progress_slider_clicked: bool = False
    user_is_seeking: bool = False
    
    _user_volume: float = 0
    _is_muted: bool = False
    _last_volume_change = None
    _volume_timer = None
    _volume_lock = threading.Lock()

    def __init__(self, file_list_box: ListWidget = None, temp_layout: QVBoxLayout = None):
        super().__init__()
        self.temp_layout = temp_layout
        self.setFixedWidth(main_width * 0.8)
        self.file_list_box = file_list_box
        self.progressSlider.setRange(0, 100)
        self.currentTimeLabel.setText('0:00')
        self.remainTimeLabel.setText('0:00')
        self.rightButtonLayout.setContentsMargins(0, 0, 8, 0)
        self.progressSlider.sliderPressed.connect(self.progress_slider_pressed)
        self.progressSlider.sliderReleased.connect(self.progress_slider_released)
        self.progressSlider.valueChanged.connect(self.progress_slider_value_changed)
        BottomRightButton(self, self.rightButtonLayout, FluentIcon.MINIMIZE, self.toggle_layout)
        # 注册全局键盘监听
        register_listener(keyboard.Key.f4, self.togglePlayState, '暂停/继续')
        register_listener(keyboard.Key.up, self.add_wait_time, '增加等待时间')
        register_listener(keyboard.Key.down, self.reduce_wait_time, '减少等待时间')
        # 注 SpeedControl 监听
        listener_registers.append(SpeedControl(lambda: float(self.wait_time)))
        self.time_manager = TimeManager()
        self.time_manager.timeChanged.connect(self.update_progress)
        
        # Add mouse click handling for the progress slider
        self.progressSlider.mousePressEvent = self.progress_slider_mouse_press
        
        try:
            # Load initial volume from config
            self._user_volume = float(conf.player.volume)
            self._is_muted = False
            
            self.volumeButton.setVolume(int(self._user_volume * 100))
            # Connect volume signals
            self.volumeButton.volumeChanged.connect(self._handle_volume_change)
            self.volumeButton.mutedChanged.connect(self._handle_mute_change)
            logger.info(f"Volume controls initialized with volume: {self._user_volume}")
        except Exception as e:
            logger.error(f"Failed to initialize volume controls: {e}")

    # Layout Control Methods
    def toggle_layout(self):
        """Toggle between normal and mini player layouts"""
        if self.state == 'normal':
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.setParent(None)
            self.show()
            self.state = 'mini'
            self.temp_width = self.width()
            self.setFixedWidth(200)
            children_windows.append(self)
        else:
            self.state = 'normal'
            self.setFixedWidth(self.temp_width)
            self.temp_layout.addWidget(self)
            children_windows.remove(self)

    def mousePressEvent(self, event):
        """
        Handle mouse press events for dragging mini player
        
        Args:
            event: Mouse press event
        """
        if self.state == 'normal':
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self._start_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """
        Handle mouse move events for dragging mini player
        
        Args:
            event: Mouse move event
        """
        if self.state == 'normal':
            return
        if self._is_dragging:
            self.move(event.globalPosition().toPoint() - self._start_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """
        Handle mouse release events for dragging mini player
        
        Args:
            event: Mouse release event
        """
        if self.state == 'normal':
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = False
            event.accept()

    def togglePlayState(self):
        """Toggle between play and pause states"""
        if self.is_playing:
            self.pause()
        else:
            self.play()

    def pause(self):
        """Pause the current playback"""
        self.playButton.setPlay(False)
        self.is_playing = False
        if self.playing_id in self.sakura_player_dict:
            self.sakura_player_dict[self.playing_id].pause()
            self.time_manager.set_playing(False)

    def play(self):
        """
        Start or resume playback of the currently selected song
        Handles loading new songs and managing player instances
        """
        current_item = self.file_list_box.currentItem()
        if current_item is None:
            return
        
        song_id = current_item.data(1)
        
        # If the same song and not seeking - just continue
        if self.playing_id == song_id and not self.progress_slider_clicked:
            self.playButton.setPlay(True)
            self.is_playing = True
            if song_id in self.sakura_player_dict:
                self.sakura_player_dict[song_id].continue_play()
                self.time_manager.set_playing(True)
            return
        song_model = song_client.select_by_id(song_id)
        try:
            # Clear the previous player before loading a new song
            if self.playing_id in self.sakura_player_dict:
                old_player = self.sakura_player_dict[self.playing_id]
                old_player.cleanup(force=True)  # Force cleanup when changing songs
                del self.sakura_player_dict[self.playing_id]
            
            # 从数据库查询 song_notes
            song_notes = song_model.songNotes

            # Create new player
            player = get_player(conf.player.type, conf)  # Create player beforehand
            sakura_player = SakuraPlayer(song_notes, self.time_manager, self.callback)
            sakura_player.last_time = song_notes[-1]['time']
            
            # Update UI before playback starts
            self.playButton.setPlay(True)
            total_seconds = sakura_player.last_time // 1000
            self.progressSlider.setRange(0, total_seconds)
            
            # Save player and start playback
            self.sakura_player_dict[song_id] = sakura_player
            self.playing_id = song_id
            self.is_playing = True
            
            # Start playback
            sakura_player.play(player, self.get_key_mapping())
            logger.info('正在播放：%s', self.file_list_box.currentItem().text())

            
        except Exception as e:
            logger.error(f"Error playing song {song_model.name}: {e}")
            self.is_playing = False
            self.playButton.setPlay(False)

    def callback(self):
        """
        Callback executed when playback is finished
        Handles cleanup and UI updates
        """
        try:
            if self.playing_id in self.sakura_player_dict:
                current_player = self.sakura_player_dict[self.playing_id]
                current_player.cleanup(force=False)  # Soft cleanup when song ends
            
            self.playButton.setPlay(False)
            self.is_playing = False
            
        except Exception as e:
            logger.error(f"Error in playback callback: {e}")
        finally:
            self.is_playing = False
            self.playButton.setPlay(False)

    def termination_cb(self):
        pass

    def get_key_mapping(self):
        """Get the current key mapping configuration"""
        mapping_type = conf.mapping.type
        mapping_dict = {
            "json": JsonMapper()
        }
        return mapping_dict[mapping_type].get_key_mapping()

    def progress_slider_pressed(self):
        """Handle when user starts dragging the progress slider"""
        self.progress_slider_clicked = True
        self.user_is_seeking = True
        if self.is_playing:
            self.time_manager.set_playing(False)

    def progress_slider_released(self):
        """
        Handle when user releases the progress slider
        Performs seeking to the new position
        """
        if not self.progress_slider_clicked:
            return
            
        try:
            value = self.progressSlider.value()
            current_player = self.sakura_player_dict.get(self.playing_id)
            
            if current_player:
                was_playing = self.is_playing
                
                # Pause playback
                if was_playing:
                    self.time_manager.set_playing(False)
                
                # Perform seeking
                current_player.seek(value * 1000)
                
                # Resume playback
                if was_playing:
                    self.time_manager.set_playing(True)
                    
        finally:
            self.progress_slider_clicked = False
            self.user_is_seeking = False

    def progress_slider_value_changed(self, value):
        """
        Update time labels when progress slider value changes
        
        Args:
            value: New slider position in seconds
        """
        if not self.user_is_seeking:
            return
        
        minutes = value // 60
        seconds = value % 60
        self.currentTimeLabel.setText(f'{minutes}:{seconds:02d}')
        
        if self.playing_id and self.playing_id in self.sakura_player_dict:
            total_seconds = self.sakura_player_dict[self.playing_id].last_time // 1000
            remain_seconds = total_seconds - value
            remain_minutes = remain_seconds // 60
            remain_seconds = remain_seconds % 60
            self.remainTimeLabel.setText(f'{remain_minutes}:{remain_seconds:02d}')

    def progress_slider_mouse_press(self, event):
        """
        Handle direct clicks on the progress bar
        
        Args:
            event: Mouse event containing click position
        """
        if event.button() == Qt.MouseButton.LeftButton:
            # Calculate the clicked position as a percentage
            value = event.position().x() / self.progressSlider.width()
            new_value = int(value * self.progressSlider.maximum())
            
            # Update the slider value
            self.progressSlider.setValue(new_value)
            
            # Handle the position change similar to slider release
            self.progress_slider_clicked = True
            self.user_is_seeking = True
            self.progress_slider_released()

    def update_progress(self, current_time_ms: int):
        """
        Update progress bar and time labels based on current playback position
        
        Args:
            current_time_ms: Current playback time in milliseconds
        """
        if not self.user_is_seeking:
            current_seconds = current_time_ms // 1000
            
            self.progressSlider.setValue(current_seconds)
            
            minutes = current_seconds // 60
            seconds = current_seconds % 60
            self.currentTimeLabel.setText(f'{minutes}:{seconds:02d}')
            
            if self.playing_id and self.playing_id in self.sakura_player_dict:
                total_seconds = self.sakura_player_dict[self.playing_id].last_time // 1000
                remain_seconds = total_seconds - current_seconds
                remain_minutes = remain_seconds // 60
                remain_seconds = remain_seconds % 60
                self.remainTimeLabel.setText(f'{remain_minutes}:{remain_seconds:02d}')

    def add_wait_time(self):
        """Increase playback wait time"""
        self.wait_time += Decimal(conf.control.speed)
        logger.info(f'wait_time: {self.wait_time}')

    def reduce_wait_time(self):
        """Decrease playback wait time"""
        if self.wait_time > 0:
            self.wait_time -= Decimal(conf.control.speed)
        logger.info(f'wait_time: {self.wait_time}')

    # Volume Control Methods
    def _handle_volume_change(self, value: int):
        """
        Handle volume slider changes
        
        Args:
            value: New volume value (0-100)
        """
        try:
            volume = float(value) / 100.0
            
            # Only save to config if not muted
            if not self._is_muted:
                self._user_volume = volume
                conf.player.volume = volume
                save_conf(conf)
                
                # Start delayed logging
                self._start_volume_timer(volume)
            self._update_player_volume(volume)
        except Exception as e:
            logger.error(f"Failed to handle volume change: {e}")

    def _handle_mute_change(self, is_muted: bool):
        """
        Handle mute button toggles
        
        Args:
            is_muted: True if audio should be muted
        """
        try:
            self._is_muted = is_muted
            volume = 0.0 if is_muted else self._user_volume
            self.volumeButton.setVolume(0 if is_muted else int(self._user_volume * 100))
            self._update_player_volume(volume)
            self._start_volume_timer(volume)
            # Start delayed logging
            self._start_volume_timer(0.0 if is_muted else self._user_volume)
        except Exception as e:
            logger.error(f"Failed to handle mute change: {e}")

    def _update_player_volume(self, volume: float):
        """
        Update volume for current player
        
        Args:
            volume: New volume value (0.0-1.0)
        """
        try:
            if self.playing_id in self.sakura_player_dict:
                current_player = self.sakura_player_dict[self.playing_id]
                if hasattr(current_player, 'player') and hasattr(current_player.player, 'audio'):
                    for sound in current_player.player.audio:
                        sound.set_volume(volume)
        except Exception as e:
            logger.error(f"Failed to update player volume: {e}")

    def _delayed_volume_logging(self):
        """Background thread for delayed (1 second) volume change logging"""
        while True:
            with self._volume_lock:
                if self._last_volume_change is None:
                    return
                
                current_volume = self._last_volume_change
                self._last_volume_change = None
            
            time.sleep(1)
            
            with self._volume_lock:
                if self._last_volume_change is not None:
                    continue
                if self._is_muted:
                    logger.info(f"Final volume state: Muted (saved volume: {self._user_volume})")
                else:
                    logger.info(f"Final volume state: {current_volume}")
                return

    def _start_volume_timer(self, volume: float):
        """
        Start or restart the volume logging timer
        
        Args:
            volume: Current volume value to log
        """
        with self._volume_lock:
            self._last_volume_change = volume
            
            if self._volume_timer and self._volume_timer.is_alive():
                return
                
            self._volume_timer = threading.Thread(
                target=self._delayed_volume_logging,
                daemon=True
            )
            self._volume_timer.start()

    def __del__(self):
        """Cleanup resources when object is destroyed"""
        if hasattr(self, 'time_manager'):
            self.time_manager.cleanup()
