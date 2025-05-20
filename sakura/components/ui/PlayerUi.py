import re

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout
from qfluentwidgets import ListWidget, SearchLineEdit

from main import get_file_list
from sakura.components.SakuraPlayBar import SakuraPlayBar
from sakura.components.ui import main_width
from sakura.config import conf
from sakura.config.sakura_logging import logger


class PlayerUi(QFrame):
    file_list_box: ListWidget
    file_list: list[str]
    search_input: SearchLineEdit
    play: SakuraPlayBar

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
        play = SakuraPlayBar(file_list_box=self.file_list_box, temp_layout=player_layout)
        player_layout.addWidget(play)
        self.play = play
        player_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        # 添加双击播放音频事件
        file_list_box.doubleClicked.connect(self.double_clicked)
        # 添加播放器到主容器布局
        container_layout.addLayout(file_info_layout)
        container_layout.addLayout(player_layout)

        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._perform_search)
        self._search_cache = {}

    def clear_search(self) -> None:
        self.search('')

    def update_search(self, text: str) -> None:
        self.search(text)

    def search(self, text: str) -> None:
        self._search_timer.stop()
        self._search_timer.start(100)
        self._current_search = text

    def _perform_search(self) -> None:
        text = self._current_search
        if text in self._search_cache:
            results = self._search_cache[text]
        else:
            results = [
                file for file in self.file_list
                if re.search(rf"{text}", file, re.IGNORECASE)
            ]
            self._search_cache[text] = results

        self.file_list_box.clear()
        self.file_list_box.addItems(results)

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

    def get_file_list_box(self) -> ListWidget:
        return self.file_list_box

    def double_clicked(self) -> None:
        logger.info('正在播放：%s', self.file_list_box.currentItem().text())
        self.play.play()
