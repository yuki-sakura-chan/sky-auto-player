from PySide6.QtWidgets import QFrame, QVBoxLayout, QSizePolicy, QSpacerItem
from qfluentwidgets import GroupHeaderCardWidget, FluentIcon, ComboBox

from sakura.config import conf


class BaseSettingsGroup(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBorderRadius(8)


class SystemSettingsGroup(BaseSettingsGroup):
    items: str = ['demo', 'win']

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle('系统设置')
        combo = ComboBox(parent)
        combo.addItems(self.items)
        combo.currentIndexChanged.connect(self.current_index_changed)
        combo.setCurrentIndex(self.items.index(conf.player.type))
        self.addGroup(FluentIcon.TILES, '播放类型', '选择软件播放类型', combo)

    def current_index_changed(self, index):
        conf.player.type = self.items[index]


class SettingsUi(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('Settings')
        layout = QVBoxLayout(self)
        system = SystemSettingsGroup()
        spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(system)
        layout.addSpacerItem(spacer)
