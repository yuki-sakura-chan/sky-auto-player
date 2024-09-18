import webbrowser

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFrame, QVBoxLayout, QSpacerItem, QHBoxLayout, QSizePolicy
from qfluentwidgets import FlowLayout, LargeTitleLabel, ElevatedCardWidget, SubtitleLabel, CaptionLabel, IconWidget, \
    FluentIcon, ToolButton


class Home(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("Home")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.addWidget(LargeTitleLabel('Welcome to Sky Auto Player!', None))
        home_card = HomeCard('GitHub repo', '本程序是免费开源的，点击可以跳转到GitHub仓库', FluentIcon.GITHUB,
                             'https://github.com/yuki-sakura-chan/sky-auto-player', self)
        component_card = HomeCard('QFluentWidgets', '本程序使用了QFluentWidgets UI 组件库，请勿商用', QIcon(':/qfluentwidgets/images/logo.png'),
                                  'https://qfluentwidgets.com/zh/')
        body_layout = FlowLayout()
        body_layout.addWidget(home_card)
        body_layout.addWidget(component_card)
        layout.addLayout(body_layout)


class HomeCard(ElevatedCardWidget):

    def __init__(self, title: str, text: str, icon: FluentIcon | QIcon, url: str, parent=None):
        super().__init__(parent=parent)
        self.adjustSize()
        self.setFixedWidth(200)
        icon = IconWidget(icon, self)
        icon.setFixedSize(48, 48)
        title_label = SubtitleLabel(title, self)
        text_label = CaptionLabel(text, self)
        text_label.setWordWrap(True)

        link = ToolButton(FluentIcon.LINK, self)
        link.setFixedSize(16, 16)
        link.setCursor(Qt.CursorShape.PointingHandCursor)
        link.clicked.connect(lambda: webbrowser.open(url))

        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # 添加控件到布局
        layout.addWidget(icon)
        layout.addWidget(title_label)
        layout.addWidget(text_label)

        # 创建一个较小的占位的 QSpacerItem 用于占用空间，使 link 靠底部对齐
        spacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)

        # 添加 link 按钮并设置其靠右对齐
        link_layout = QHBoxLayout()
        link_layout.addStretch()
        link_layout.addWidget(link)

        layout.addLayout(link_layout)
