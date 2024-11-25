import threading
import time
from decimal import Decimal
from typing import Callable, Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import Slider, CaptionLabel, ListWidget, FluentIcon
from qfluentwidgets.multimedia import StandardMediaPlayBar
from pynput import keyboard

from sakura import children_windows
from sakura.components.TimeManager import TimeManager
from sakura.components.mapper.JsonMapper import JsonMapper
from sakura.components.ui import main_width
from sakura.components.ui.BottomRightButton import BottomRightButton
from sakura.components.SpeedControl import SpeedControl
from sakura.config import conf
from sakura.config.sakura_logging import logger
from sakura.factory.PlayerFactory import get_player
from sakura.interface.PressListener import PressListener
from sakura.components.player.SakuraPlayer import SakuraPlayer
from sakura.listener import register_listener
from sakura.registrar.listener_registers import listener_registers
from main import load_json


class SakuraProgressBar(PressListener):
    thread_is_running = False
    progress_slider: Slider
    current_time_label: CaptionLabel
    remain_time_label: CaptionLabel

    def __init__(self, progress_slider: Slider, current_time_label: CaptionLabel, remain_time_label: CaptionLabel):
        self.progress_slider = progress_slider
        self.current_time_label = current_time_label
        self.remain_time_label = remain_time_label

    def listener(self, current_time: Callable[[], int], prev_time: Callable[[], int], 
                wait_time: Callable[[], int], last_time: Callable[[], int], 
                key, is_paused: Callable[[], bool]):
        if not self.thread_is_running:
            t = threading.Thread(
                target=manage_progress_thread,
                args=(current_time, last_time, is_paused, 
                      self.progress_slider, self.current_time_label,
                      self.remain_time_label, self.stop),
                daemon=True
            )
            t.start()
            self.thread_is_running = True

    def stop(self):
        self.thread_is_running = False


def manage_progress_thread(current_time, last_time, is_paused: Callable[[], bool], progress_slider: Slider,
                           current_time_label: CaptionLabel, remain_time_label: CaptionLabel, stop: Callable[[], None]):
    try:
        current_second = int(current_time() / 1000)
        last_second = int(last_time() / 1000)
        
        while current_second <= last_second:
            if is_paused():
                stop()
                return
                
            current_second = int(current_time() / 1000)
            
            minutes = current_second // 60
            seconds = current_second % 60
            current_time_label.setText(f'{minutes}:{seconds:02d}')
            
            remain_seconds = last_second - current_second
            remain_minutes = remain_seconds // 60
            remain_seconds = remain_seconds % 60
            remain_time_label.setText(f'{remain_minutes}:{remain_seconds:02d}')
            
            progress_slider.setValue(current_second)
            
            time.sleep(0.1)
    except Exception as e:
        logger.error(f"Error in progress thread: {e}")
    finally:
        stop()

class SakuraPlayBar(StandardMediaPlayBar):
    is_playing: bool = False
    file_list_box: ListWidget
    playing_name: str = ''
    sakura_player_dict: dict[str, SakuraPlayer] = {}
    temp_window: QWidget
    temp_layout: QVBoxLayout
    state: str = 'normal'
    _is_dragging: bool = False
    _start_position: Any
    temp_width: int
    wait_time: Decimal = 0
    progress_slider_clicked: bool = False
    user_is_seeking: bool = False

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
        
    def progress_slider_pressed(self):
        self.progress_slider_clicked = True
        self.user_is_seeking = True

    def progress_slider_released(self):
        if not self.progress_slider_clicked:
            return
            
        value = self.progressSlider.value()
        current_player = self.sakura_player_dict.get(self.playing_name)
        
        if current_player:
            was_playing = self.is_playing
            current_player.stop()
            time.sleep(0.1)
            
            self.time_manager.force_set_time(value * 1000)
            
            if was_playing:
                current_player.play(
                    get_player(conf.player.type, conf),
                    self.get_key_mapping(),
                    value
                )
                self.is_playing = True
                self.playButton.setPlay(True)
                self.time_manager.set_playing(True)
        
        self.progress_slider_clicked = False
        self.user_is_seeking = False

    def progress_slider_value_changed(self, value):
        if self.user_is_seeking:
            minutes = value // 60
            seconds = value % 60
            self.currentTimeLabel.setText(f'{minutes}:{seconds:02d}')
            
            if self.playing_name and self.playing_name in self.sakura_player_dict:
                total_seconds = self.sakura_player_dict[self.playing_name].last_time // 1000
                remain_seconds = total_seconds - value
                remain_minutes = remain_seconds // 60
                remain_seconds = remain_seconds % 60
                self.remainTimeLabel.setText(f'{remain_minutes}:{remain_seconds:02d}')

    # 增加 wait_time
    def add_wait_time(self):
        self.wait_time += Decimal(conf.control.speed)
        logger.info(f'wait_time: {self.wait_time}')

    # 减少 wait_time
    def reduce_wait_time(self):
        if self.wait_time > 0:
            self.wait_time -= Decimal(conf.control.speed)
        logger.info(f'wait_time: {self.wait_time}')

    def toggle_layout(self):
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

    # 鼠标按下事件，记录初始位置
    def mousePressEvent(self, event):
        if self.state == 'normal':
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self._start_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    # 鼠标移动事件，更新窗口位置
    def mouseMoveEvent(self, event):
        if self.state == 'normal':
            return
        if self._is_dragging:
            self.move(event.globalPosition().toPoint() - self._start_position)
            event.accept()

    # 鼠标释放事件，停止拖动
    def mouseReleaseEvent(self, event):
        if self.state == 'normal':
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = False
            event.accept()

    def togglePlayState(self):
        if self.is_playing:
            self.pause()
        else:
            self.play()

    def pause(self):
        self.playButton.setPlay(False)
        self.is_playing = False
        if self.playing_name in self.sakura_player_dict:
            self.sakura_player_dict[self.playing_name].pause()
            self.time_manager.set_playing(False)

    def play(self):
        current_item = self.file_list_box.currentItem()
        if current_item is None:
            return
        
        file_name = current_item.text()
        
        # Clearing resources from the previous song
        player = get_player(conf.player.type, conf)
        player.cleanup()
        
        if self.playing_name == file_name and not self.progress_slider_clicked:
            self.playButton.setPlay(True)
            self.is_playing = True
            if file_name in self.sakura_player_dict:
                self.sakura_player_dict[file_name].continue_play()
                self.time_manager.set_playing(True)
            return

        try:            
            json_data = load_json(f'{conf.file_path}/{file_name}')
            song_notes = json_data[0]['songNotes']
            
            if self.playing_name in self.sakura_player_dict:
                self.sakura_player_dict[self.playing_name].stop()
                del self.sakura_player_dict[self.playing_name]
            
            sakura_player = SakuraPlayer(song_notes, self.time_manager, self.callback)
            sakura_player.last_time = song_notes[-1]['time']
            self.sakura_player_dict[file_name] = sakura_player
            
            self.playButton.setPlay(True)
            self.is_playing = True
            self.playing_name = file_name
            
            total_seconds = sakura_player.last_time // 1000
            self.progressSlider.setRange(0, total_seconds)
            
            sakura_player.play(
                get_player(conf.player.type, conf),
                self.get_key_mapping()
            )
            
        except Exception as e:
            logger.error(f"Error playing file {file_name}: {e}")

    # 当播放完毕时，回调当前接口
    def callback(self):
        self.playButton.setPlay(False)
        self.is_playing = False
        self.playing_name = ''

    # 手动终止播放时，回调当前接口
    def termination_cb(self):
        pass

    def get_key_mapping(self):
        mapping_type = conf.mapping.type
        mapping_dict = {
            "json": JsonMapper()
        }
        return mapping_dict[mapping_type].get_key_mapping()

    def update_progress(self, current_time_ms: int):
        if not self.user_is_seeking:
            current_seconds = current_time_ms // 1000
            
            self.progressSlider.setValue(current_seconds)
            
            minutes = current_seconds // 60
            seconds = current_seconds % 60
            self.currentTimeLabel.setText(f'{minutes}:{seconds:02d}')
            
            if self.playing_name and self.playing_name in self.sakura_player_dict:
                total_seconds = self.sakura_player_dict[self.playing_name].last_time // 1000
                remain_seconds = total_seconds - current_seconds
                remain_minutes = remain_seconds // 60
                remain_seconds = remain_seconds % 60
                self.remainTimeLabel.setText(f'{remain_minutes}:{remain_seconds:02d}')

    def progress_slider_mouse_press(self, event):
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

    def __del__(self):
        if hasattr(self, 'time_manager'):
            self.time_manager.cleanup()
