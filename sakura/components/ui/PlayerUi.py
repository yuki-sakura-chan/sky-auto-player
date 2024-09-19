from PySide6.QtWidgets import QFrame
from qfluentwidgets import FlowLayout, ListWidget

from main import get_file_list
from sakura.config.Config import conf


class PlayerUi(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Player")
        main_layout = FlowLayout(self)
        file_list_box = ListWidget()
        file_list = get_file_list(conf.get('file_path'))
        for index, file in enumerate(file_list):
            file_list_box.addItem(file)
        main_layout.addWidget(file_list_box)
