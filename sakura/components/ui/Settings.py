from PySide6.QtWidgets import QFrame, QVBoxLayout, QSizePolicy, QSpacerItem
from qfluentwidgets import GroupHeaderCardWidget, FluentIcon, ComboBox, LineEdit
from sakura.config import conf, save_conf


class BaseSettingsGroup(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBorderRadius(8)


class SystemSettingsGroup(BaseSettingsGroup):
    items: list[str] = ['demo', 'win']

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle('系统设置')
        self.create_combo_box(parent)
        self.create_speed_control(parent)

    def create_combo_box(self, parent):
        combo = ComboBox(parent)
        combo.addItems(self.items)
        combo.currentIndexChanged.connect(self.current_index_changed)
        combo.setCurrentIndex(self.items.index(conf.player.type))
        self.addGroup(FluentIcon.TILES, '播放类型', '选择软件播放类型', combo)

    def create_speed_control(self, parent):
        speed_control = LineEdit(parent)
        speed_control.setPlaceholderText('请输入每拍增加的速度')
        speed_control.setText(str(conf.control.speed))
        speed_control.editingFinished.connect(lambda: self.update_config('control.speed', speed_control.text(), speed_control))
        self.addGroup(FluentIcon.ADD, '速度控制', '设置每拍增加的速度', speed_control)


    def current_index_changed(self, index: int) -> None:
        conf.player.type = self.items[index]
        save_conf(conf)

    def update_config(self, attribute: str, value: str, attributes: LineEdit) -> None:
        try:
            if attribute == 'control.speed':
                conf.control.speed = str(float(value))
            # elif attribute == 'player.type':
            #     conf.player.type = value
            save_conf(conf)
            attributes.clearFocus()
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred while updating {attribute} - {value}: {e}")


class SettingsUi(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('Settings')
        layout = QVBoxLayout(self)
        system = SystemSettingsGroup()
        spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(system)
        layout.addSpacerItem(spacer)

    def mousePressEvent(self, event) -> None:
        for widget in self.findChildren(LineEdit):
            widget.clearFocus()
        super().mousePressEvent(event)
