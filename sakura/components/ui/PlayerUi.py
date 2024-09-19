from PySide6.QtWidgets import QFrame
from qfluentwidgets import FlowLayout, ListWidget


class PlayerUi(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Player")
        main_layout = FlowLayout(self)
        file_list_box = ListWidget()
        file_list_box.addItem("File 1")
        main_layout.addWidget(file_list_box)