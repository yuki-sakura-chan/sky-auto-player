from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout
from qfluentwidgets import ListWidget
from qfluentwidgets.multimedia import StandardMediaPlayBar

from main import get_file_list
from sakura.components.ui import main_width
from sakura.config.Config import conf


class PlayerUi(QFrame):
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
        # 加载文件列表
        file_list_box = ListWidget()
        file_list_box.setFixedSize(400, 600)
        file_list = get_file_list(conf.get('file_path'))
        for index, file in enumerate(file_list):
            file_list_box.addItem(file)
        # 添加文件列表到主容器布局
        file_info_layout.addWidget(file_list_box)
        # 创建信息框
        info_frame = QFrame(main_container)
        # 添加信息框到主容器布局
        file_info_layout.addWidget(info_frame)
        # 创建播放器布局
        player_layout = QVBoxLayout()
        player_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        # 创建播放器
        play = SakuraPlayBar()
        player_layout.addWidget(play)
        player_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        # 添加播放器到主容器布局
        container_layout.addLayout(file_info_layout)
        container_layout.addLayout(player_layout)


class SakuraPlayBar(StandardMediaPlayBar):
    isPlaying: bool = False

    def __init__(self):
        super().__init__()
        self.setFixedWidth(main_width * 0.8)
        self.progressSlider.setRange(0, 100)
        self.progressSlider.setValue(50)
        self.currentTimeLabel.setText('00:00')
        self.remainTimeLabel.setText('00:20')

    def togglePlayState(self):
        if self.isPlaying:
            self.pause()
        else:
            self.play()

    def pause(self):
        self.playButton.setPlay(False)
        self.isPlaying = False

    def play(self):
        self.playButton.setPlay(True)
        self.isPlaying = True
