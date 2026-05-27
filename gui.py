import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from qfluentwidgets import FluentIcon as FIF, setTheme, Theme, NavigationDisplayMode
from qfluentwidgets import NavigationItemPosition, FluentWindow

import resources.resources_rc  # noqa
from sakura import children_windows
from sakura.components.SingleApplication import SingleApplication
from sakura.components.ui.Home import Home
from sakura.components.ui.PlayerUi import PlayerUi
from sakura.components.ui.Settings import SettingsUi


class Window(FluentWindow):
    """ 主界面 """

    def __init__(self):
        super().__init__()

        # 初始化主页面
        self.init_window()
        # 创建子界面，实际使用时将 Widget 换成自己的子界面
        self.homeInterface = Home(self)
        self.playerInterface = PlayerUi(self)
        self.settingInterface = SettingsUi(self)
        self.init_navigation()

    def init_navigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, 'Home')
        self.navigationInterface.addSeparator()
        self.addSubInterface(self.playerInterface, FIF.PLAY, 'Player')
        self.addSubInterface(self.settingInterface, FIF.SETTING, 'Settings', NavigationItemPosition.BOTTOM)

    def init_window(self):
        self.setMinimumHeight(800)
        self.setMinimumWidth(1286)
        self.navigationInterface.setMinimumExpandWidth(10000)
        self.setWindowIcon(QIcon(':/sakura/icon/logo-128x128.ico'))
        self.setWindowTitle('Sky Auto Player')

    def closeEvent(self, event):
        super().closeEvent(event)
        for item in children_windows:
            item.close()

    # 显示窗口
    def show_window(self):

        # 如果窗口最小化
        if self.isMinimized():

            # 恢复正常状态
            self.showNormal()

        # 显示窗口
        self.show()

        # 提升窗口层级
        # 类似置顶到最前面
        self.raise_()

        # 激活窗口
        # 获取焦点
        self.activateWindow()


if __name__ == '__main__':
    setTheme(Theme.AUTO)
    app = QApplication(sys.argv)
    # 创建单实例对象
    single_app = SingleApplication("sakura_auto_player")
    if single_app.already_running():
        # 直接退出当前进程
        sys.exit(0)
    screen = app.primaryScreen()
    screen_rect = screen.availableGeometry()
    w = Window()
    # 收到 show 消息时
    # 调用窗口显示函数
    single_app.on_show = w.show_window
    x = (screen_rect.width() - w.width()) // 2
    y = (screen_rect.height() - w.height()) // 2
    w.move(x, y)
    w.show()
    app.exec()
