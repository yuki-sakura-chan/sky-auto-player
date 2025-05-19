import webbrowser

from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QFrame, QVBoxLayout, QSpacerItem, QSizePolicy
from qfluentwidgets import FlowLayout, LargeTitleLabel, ElevatedCardWidget, SubtitleLabel, CaptionLabel, IconWidget, \
    FluentIcon, ImageLabel, qconfig
from requests import request

from sakura.components.ui import background_images, main_width
from sakura.components.ui.BottomRightButton import BottomRightButton
from sakura.locales.locale import load_locale_messages


class Home(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("Home")
        background_layout = QVBoxLayout(self)
        background_layout.setContentsMargins(0, 0, 0, 0)
        background_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        background = ImageLabel(background_images[qconfig.theme.value]['path'], self)
        background.scaledToWidth(main_width)
        background.setBorderRadius(8, 8, 8, 8)
        layout = QVBoxLayout(background)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(30, 20, 30, 20)
        locales = load_locale_messages('home')
        layout.addWidget(LargeTitleLabel('Welcome to Sky Auto Player!', None))
        home_card = HomeCard('GitHub repo', locales.messages('home_card.text'), FluentIcon.GITHUB,
                             'https://github.com/yuki-sakura-chan/sky-auto-player', self)
        component_card = HomeCard('QFluentWidgets', locales.messages('component_card.text'),
                                  QIcon(':/qfluentwidgets/images/logo.png'),
                                  'https://qfluentwidgets.com/zh/')
        pixiv_card = HomeCard('Pixiv',
                              locales.messages('pixiv_card.text'),
                              'https://www.pixiv.net/favicon.ico', 'https://www.pixiv.net/')
        body_layout = FlowLayout()
        body_layout.addWidget(home_card)
        body_layout.addWidget(component_card)
        body_layout.addWidget(pixiv_card)
        layout.addLayout(body_layout)
        background_layout.addWidget(background)
        BottomRightButton(self, layout, FluentIcon.LINK, lambda: webbrowser.open(background_images[qconfig.theme.value]['url']))


class HomeCard(ElevatedCardWidget):

    def __init__(self, title: str, text: str, icon: FluentIcon | QIcon | str, url: str, parent=None):
        super().__init__(parent=parent)
        self.adjustSize()
        self.setFixedWidth(200)
        icon_label = IconWidget(icon, self)
        icon_label.setFixedSize(48, 48)
        if isinstance(icon, str) and icon.startswith('http'):
            loader_thread = IconLoaderThread(icon, icon_label)
            loader_thread.finished.connect(lambda: icon_label.setIcon(loader_thread.icon))
            icon_label.setIcon(FluentIcon.SYNC)
            loader_thread.start()
        title_label = SubtitleLabel(title, self)
        text_label = CaptionLabel(text, self)
        text_label.setWordWrap(True)

        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # 添加控件到布局
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(text_label)

        # 创建一个较小的占位的 QSpacerItem 用于占用空间，使 link 靠底部对齐
        spacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)
        BottomRightButton(self, layout, FluentIcon.LINK, lambda: webbrowser.open(url))


class IconLoaderThread(QThread):
    url: str
    icon: QIcon | FluentIcon

    def __init__(self, url: str, parent=None):
        super().__init__(parent=parent)
        self.url = url

    def run(self):
        try:
            resp = request('GET', self.url, timeout=5)
            if resp.status_code == 200:
                img_bytes = resp.content
                pixmap = QPixmap()
                pixmap.loadFromData(img_bytes)
                self.icon = QIcon(pixmap)
            else:
                self.icon = FluentIcon.CLOSE
        except Exception as e:
            print(e)
            self.icon = FluentIcon.CLOSE
