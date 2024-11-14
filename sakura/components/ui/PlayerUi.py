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


class PlayerUi(QFrame):
    file_list_box: ListWidget
    file_list: list
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
        search_input.clearSignal.connect(lambda: self.search(''))
        search_input.installEventFilter(self)
        self.search_input = search_input
        # 加载文件列表
        file_list_layout = QVBoxLayout()
        file_list_box = ListWidget()
        file_list_box.setFixedSize(400, 600)
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

    def search(self, text):
        self.file_list_box.clear()
        # 正则表达式匹配
        for index, file in enumerate(self.file_list):
            if re.search(rf"{text}", file, re.IGNORECASE):
                self.file_list_box.addItem(file)

    def eventFilter(self, watched, event):
        if watched == self.search_input and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return:
                self.search(self.search_input.text())
                return True
        return super().eventFilter(watched, event)


class SakuraPlayer:
    song_notes: list
    is_finished: bool = False
    cb: Callable[[], None]
    tcb: Callable[[], None]
    is_playing: bool
    main_parent: QLayout
    last_time: int

    def __init__(self, song_notes: list, cb: Callable[[], None] = lambda: None, tcb: Callable[[], None] = lambda: None):
        self.song_notes = song_notes
        self.is_playing = False
        self.cb = cb
        self.tcb = tcb

    def play(self, player: Player, key_mapping: dict, slider_value=None):
        time.sleep(0.1)
        self.is_finished = False
        self.is_playing = True
        play_cb = PlayCallback(lambda: self.is_finished, lambda: not self.is_playing, self.callback,
                               self.termination_cb)
        player_thread = threading.Thread(target=play_song,
                                         args=(self.song_notes, player, key_mapping, play_cb, slider_value * 1000,))
        player_thread.daemon = True
        player_thread.start()

    def pause(self):
        self.is_playing = False

    def stop(self):
        # 继续播放，以保证可以执行回调
        self.is_playing = True
        # 终止线程
        self.is_finished = True

    def continue_play(self):
        self.is_playing = True

    def callback(self):
        self.is_playing = False
        self.cb()

    def termination_cb(self):
        self.tcb()


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

    def __init__(self, parent: PlayerUi = None, temp_layout: QVBoxLayout = None):
        super().__init__()
        self.temp_layout = temp_layout
        self.setFixedWidth(main_width * 0.8)
        self.file_list_box = parent.file_list_box
        self.progressSlider.setRange(0, 100)
        self.currentTimeLabel.setText('0:00')
        self.remainTimeLabel.setText('0:00')
        self.rightButtonLayout.setContentsMargins(0, 0, 8, 0)
        self.progressSlider.clicked.connect(self.progress_slider_clicked_event)
        self.progressSlider.valueChanged.connect(self.progress_slider_changed_event)
        BottomRightButton(self, self.rightButtonLayout, FluentIcon.MINIMIZE, self.toggle_layout)
        # 注册全局键盘监听
        register_listener(keyboard.Key.f4, self.togglePlayState, '暂停/继续')
        register_listener(keyboard.Key.up, self.add_wait_time, '增加等待时间')
        register_listener(keyboard.Key.down, self.reduce_wait_time, '减少等待时间')
        # 注册 PressListener 监听
        listener_registers.append(SakuraProgressBar(self.progressSlider, self.currentTimeLabel, self.remainTimeLabel))
        # 注册 SpeedControl 监听
        listener_registers.append(SpeedControl(lambda: float(self.wait_time)))


    def progress_slider_clicked_event(self):
        self.progress_slider_clicked = True

    def progress_slider_changed_event(self, value):
        self.currentTimeLabel.setText(f'{value // 60}:{value % 60:02d}')

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
        self.sakura_player_dict[self.playing_name].pause()

    def play(self):
        current_item = self.file_list_box.currentItem()
        if current_item is None:
            return
        player = get_player(conf.player.type, conf)
        mapping_type = conf.mapping.type
        mapping_dict = {
            "json": JsonMapper()
        }
        key_mapping = mapping_dict[mapping_type].get_key_mapping()
        file_name = current_item.text()
        if self.playing_name == file_name and not self.progress_slider_clicked:
            self.playButton.setPlay(True)
            self.is_playing = True
            self.sakura_player_dict[file_name].continue_play()
            return
        self.playing_name = file_name
        # 播放新的歌曲时，终止之前的播放器
        if self.sakura_player_dict:
            for p in self.sakura_player_dict.values():
                p.stop()
        # 如果 sakura_player_dict 中已经有了这个播放器，直接播放
        if file_name in self.sakura_player_dict:
            self.playButton.setPlay(True)
            self.is_playing = True
            sakura_player = self.sakura_player_dict[file_name]
            self.progressSlider.setRange(0, int(sakura_player.last_time / 1000))
            sakura_player.play(player, key_mapping, self.progressSlider.value() )
            self.progressSlider.setValue(0)
            self.progress_slider_clicked = False
            return
        json_data = load_json(f'{conf.file_path}/{file_name}')
        song_notes = json_data[0]['songNotes']
        last_time = song_notes[-1]['time']
        self.progressSlider.setRange(0, int(last_time / 1000))
        self.progressSlider.setValue(0)
        sakura_player = SakuraPlayer(song_notes, self.callback, self.termination_cb)
        sakura_player.play(player, key_mapping, self.progressSlider.value())
        sakura_player.last_time = last_time
        self.sakura_player_dict[file_name] = sakura_player
        self.playButton.setPlay(True)
        self.is_playing = True

    # 当播放完毕时，回调当前接口
    def callback(self):
        self.playButton.setPlay(False)
        self.is_playing = False
        self.playing_name = ''

    # 手动终止播放时，回调当前接口
    def termination_cb(self):
        pass
