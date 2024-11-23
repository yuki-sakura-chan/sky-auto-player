import re
import threading
import time
from decimal import Decimal
from typing import Callable, Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLayout, QWidget
from pynput import keyboard
from qfluentwidgets import ListWidget, FluentIcon, SearchLineEdit
from qfluentwidgets.multimedia import StandardMediaPlayBar

from main import get_file_list, load_json, play_song, PlayCallback
from sakura import children_windows
from sakura.components.SakuraPlayBar import SakuraProgressBar
from sakura.components.SpeedControl import SpeedControl
from sakura.components.mapper.JsonMapper import JsonMapper
from sakura.components.ui import main_width
from sakura.components.ui.BottomRightButton import BottomRightButton
from sakura.config import conf
from sakura.config.sakura_logging import logger
from sakura.factory.PlayerFactory import get_player
from sakura.interface.Player import Player
from sakura.listener import register_listener
from sakura.registrar.listener_registers import listener_registers
from concurrent.futures import ThreadPoolExecutor
from sakura.components.TimeManager import TimeManager


class PlayerUi(QFrame):
    file_list_box: ListWidget
    file_list: list[str]
    search_input: SearchLineEdit

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Player")
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        # 创建主容器
        main_container = QFrame()
        main_container.setFixedWidth(main_width)
        # 添加主容器到主布局
        main_layout.addWidget(main_container)
        main_container.setFixedWidth(main_width)
        # 创建主容器布局
        container_layout = QVBoxLayout(main_container)
        # 创建文件信息布局
        file_info_layout = QHBoxLayout()
        file_info_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        search_input = SearchLineEdit()
        search_input.searchSignal.connect(self.search)
        search_input.clearSignal.connect(self.clear_search)
        search_input.textChanged.connect(self.update_search)
        search_input.returnPressed.connect(self.handle_search_complete)
        search_input.installEventFilter(self)
        self.search_input = search_input
        # 加载文件列表
        file_list_layout = QVBoxLayout()
        file_list_box = ListWidget()
        file_list_box.setFixedSize(400, 600)
        file_list_box.setSpacing(0.5)
        self.file_list = get_file_list(conf.file_path)
        for index, file in enumerate(self.file_list):
            file_list_box.addItem(file)
        # 添加文件列表到主容器布局
        file_list_layout.addWidget(search_input)
        file_list_layout.addWidget(file_list_box)
        file_info_layout.addLayout(file_list_layout)
        self.file_list_box = file_list_box
        # 创建信息框
        info_frame = QFrame(main_container)
        # 添加信息框到主容器布局
        file_info_layout.addWidget(info_frame)
        # 创建播放器布局
        player_layout = QVBoxLayout()
        player_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        # 创建播放器
        play = SakuraPlayBar(self, temp_layout=player_layout)
        player_layout.addWidget(play)
        player_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        # 添加播放器到主容器布局
        container_layout.addLayout(file_info_layout)
        container_layout.addLayout(player_layout)

    def clear_search(self) -> None:
        self.search('')

    def update_search(self, text: str) -> None:
        self.search(text)

    def search(self, text: str) -> None:
        self.file_list_box.clear()
        # 正则表达式匹配
        matching_files = [file for file in self.file_list if re.search(rf"{text}", file, re.IGNORECASE)]
        self.file_list_box.addItems(matching_files)

    def handle_search_complete(self) -> None:
        self.search(self.search_input.text())
        self.search_input.clearFocus()

    def eventFilter(self, watched, event) -> bool:
        if watched == self.search_input and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return:
                self.handle_search_complete()
                return True
        return super().eventFilter(watched, event)

    def mousePressEvent(self, event) -> None:
        if not self.search_input.geometry().contains(event.pos()):
            self.search_input.clearFocus()
        super().mousePressEvent(event)


class SakuraPlayer:
    def __init__(self, song_notes: list, time_manager: TimeManager, cb: Callable[[], None] = lambda: None):
        self.song_notes = song_notes
        self.time_manager = time_manager
        self.is_playing = False
        self.is_finished = False
        self.cb = cb
        self.last_time = 0
        self.current_executor = None
        self.current_thread = None
        self.key_mapping = None
        self.player = None
        
    def play(self, player: Player, key_mapping: dict, start_time: int = None):
        self.player = player
        self.key_mapping = key_mapping
        self.stop()
        time.sleep(0.1)
        
        self.is_finished = False
        self.is_playing = True
        
        if start_time is not None:
            self.time_manager.set_current_time(start_time * 1000)
        else:
            self.time_manager.set_current_time(0)
            
        self.time_manager.set_duration(self.last_time)
        self.time_manager.set_playing(True)
        
        filtered_notes = [
            note for note in self.song_notes 
            if note['time'] >= self.time_manager.get_current_time()
        ]
        
        play_cb = PlayCallback(
            lambda: self.is_finished,
            lambda: not self.is_playing,
            self.callback,
            self.termination_cb
        )
        
        self.current_executor = ThreadPoolExecutor(max_workers=4)
        self.current_thread = threading.Thread(
            target=play_song,
            args=(filtered_notes, player, key_mapping, play_cb, self.time_manager, self.current_executor)
        )
        self.current_thread.daemon = True
        self.current_thread.start()

    def pause(self):
        self.is_playing = False
        self.time_manager.set_playing(False)

    def stop(self):
        self.is_finished = True
        self.is_playing = False
        if self.current_executor:
            self.current_executor.shutdown(wait=False)
            self.current_executor = None
        if self.current_thread and self.current_thread.is_alive():
            self.current_thread.join(timeout=0.1)
        self.current_thread = None

    def continue_play(self):
        if not self.player or not self.key_mapping:
            logger.error("Player or key mapping not initialized")
            return
            
        self.stop()
        time.sleep(0.1)
            
        self.is_playing = True
        self.is_finished = False
        self.time_manager.set_playing(True)
        
        current_time = self.time_manager.get_current_time()
        filtered_notes = [
            note for note in self.song_notes 
            if note['time'] >= current_time
        ]
        
        play_cb = PlayCallback(
            lambda: self.is_finished,
            lambda: not self.is_playing,
            self.callback,
            self.termination_cb
        )
        
        self.current_executor = ThreadPoolExecutor(max_workers=4)
        self.current_thread = threading.Thread(
            target=play_song,
            args=(filtered_notes, self.player, self.key_mapping, 
                  play_cb, self.time_manager, self.current_executor)
        )
        self.current_thread.daemon = True
        self.current_thread.start()

    def callback(self):
        self.is_playing = False
        self.cb()

    def termination_cb(self):
        pass


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

    def __init__(self, parent: PlayerUi = None, temp_layout: QVBoxLayout = None):
        super().__init__()
        self.temp_layout = temp_layout
        self.setFixedWidth(main_width * 0.8)
        self.file_list_box = parent.file_list_box
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
        
        # Add mouse click handling for the progress sliderё
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
