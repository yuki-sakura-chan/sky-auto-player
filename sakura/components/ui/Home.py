from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFrame, QVBoxLayout, QSpacerItem, QSizePolicy
from qfluentwidgets import FlowLayout, LargeTitleLabel, ElevatedCardWidget, SubtitleLabel, CaptionLabel, IconWidget, \
    FluentIcon, ImageLabel, qconfig

from sakura.components.ui import background_images
from sakura.components.ui.BottomLeftLinkButton import BottomLeftLinkButton


class Home(QFrame):
    background_image: str = ':/sakura/images/background-1.jpg'

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("Home")
        background_layout = QVBoxLayout(self)
        background_layout.setContentsMargins(0, 0, 0, 0)
        background_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        background = ImageLabel(background_images[qconfig.theme.value]['path'], self)
        background.scaledToWidth(1240)
        background.setBorderRadius(8, 8, 8, 8)
        layout = QVBoxLayout(background)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.addWidget(LargeTitleLabel('Welcome to Sky Auto Player!', None))
        home_card = HomeCard('GitHub repo', '本程序免费开源，欢迎大家贡献', FluentIcon.GITHUB,
                             'https://github.com/yuki-sakura-chan/sky-auto-player', self)
        component_card = HomeCard('QFluentWidgets', '本程序UI使用了QFluentWidgets UI 组件库，详情请点击跳转',
                                  QIcon(':/qfluentwidgets/images/logo.png'),
                                  'https://qfluentwidgets.com/zh/')
        body_layout = FlowLayout()
        body_layout.addWidget(home_card)
        body_layout.addWidget(component_card)
        layout.addLayout(body_layout)
        background_layout.addWidget(background)
        BottomLeftLinkButton(self, layout, FluentIcon.LINK, background_images[qconfig.theme.value]['url'])


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
        BottomLeftLinkButton(self, layout, FluentIcon.LINK, url)
