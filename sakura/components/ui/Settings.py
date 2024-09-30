from PySide6.QtWidgets import QFrame, QVBoxLayout, QSizePolicy, QSpacerItem
from qfluentwidgets import GroupHeaderCardWidget, FluentIcon, PushButton


class BaseSettingsGroup(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBorderRadius(8)


class SystemSettingsGroup(BaseSettingsGroup):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle('系统设置')
        button = PushButton(parent)
        button.setText('按钮')
        self.addGroup(FluentIcon.TILES, '播放类型', '选择软件播放类型', button)


class SettingsUi(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('Settings')
        layout = QVBoxLayout(self)
        system = SystemSettingsGroup()
        spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(system)
        layout.addSpacerItem(spacer)

