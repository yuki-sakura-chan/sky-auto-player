from typing import Union, Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QSpacerItem, QSizePolicy, QHBoxLayout
from qfluentwidgets import TransparentToolButton, FluentIconBase


class BottomRightButton(TransparentToolButton):
    def __init__(self, parent=None, layout=None, icon: Union[QIcon, str, FluentIconBase] = None,
                 clicked: Callable = None):
        super().__init__(parent)
        self.setFixedSize(16, 16)
        self.setIcon(icon)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(clicked)
        # 创建一个较小的占位的 QSpacerItem 用于占用空间，使 link 靠底部对齐
        spacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)

        # 添加 link 按钮并设置其靠右对齐
        link_layout = QHBoxLayout()
        link_layout.addStretch()
        link_layout.addWidget(self)

        layout.addLayout(link_layout)
