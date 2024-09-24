import sys

from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import QApplication, QHBoxLayout, QFrame
from qfluentwidgets import FluentIcon as FIF, setTheme, Theme
from qfluentwidgets import NavigationItemPosition, FluentWindow, SubtitleLabel, setFont

import resources.resources_rc  # noqa
from sakura.components.ui.Home import Home
from sakura.components.ui.PlayerUi import PlayerUi


class Widget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)

        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignmentFlag.AlignCenter)

        # 必须给子界面设置全局唯一的对象名
        self.setObjectName(text.replace(' ', '-'))


class Window(FluentWindow):
    """ 主界面 """

    def __init__(self):
        super().__init__()

        # 初始化主页面
        self.init_window()
        # 创建子界面，实际使用时将 Widget 换成自己的子界面
        self.homeInterface = Home(self)
        self.playerInterface = PlayerUi(self)
        self.settingInterface = Widget('Setting Interface', self)
        self.init_navigation()

    def init_navigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, 'Home')
        self.navigationInterface.addSeparator()
        self.addSubInterface(self.playerInterface, FIF.PLAY, 'Player')
        self.addSubInterface(self.settingInterface, FIF.SETTING, 'Settings', NavigationItemPosition.BOTTOM)

    def init_window(self):
        self.setMinimumHeight(800)
        self.setMinimumWidth(1286)
        self.navigationInterface.setExpandWidth(180)
        self.setWindowIcon(QIcon(':/sakura/icon/logo-128x128.ico'))
        self.setWindowTitle('Sky Auto Player')


if __name__ == '__main__':
    setTheme(Theme.AUTO)
    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    screen_rect = screen.availableGeometry()
    w = Window()
    x = (screen_rect.width() - w.width()) // 2
    y = (screen_rect.height() - w.height()) // 2
    w.move(x, y)
    w.show()
    app.exec()
