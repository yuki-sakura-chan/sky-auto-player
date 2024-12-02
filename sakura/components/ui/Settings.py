from PySide6.QtWidgets import QFrame, QVBoxLayout, QSizePolicy, QSpacerItem
from qfluentwidgets import GroupHeaderCardWidget, FluentIcon, ComboBox, LineEdit
from sakura.config import conf, save_conf


class BaseSettingsGroup(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBorderRadius(8)


class SystemSettingsGroup(BaseSettingsGroup):
    player_types: list[str] = ['demo', 'win']
    instruments: list[str] = [
        'Aurora', 'Contrabass', 'Flute', 'Guitar', 'Harp', 'Horn', 'Kalimba', 'LightGuitar', 
        'MantaOcarina', 'Ocarina', 'Panflute', 'Piano', 'Piano V2', 'Piano Old', 'Pipa', 
        'SFX_BirdCall', 'SFX_CrabCall', 'SFX_FishCall', 'SFX_JellyCall', 'SFX_MantaCall', 
        'SFX_MothCall', 'SFX_SpiritMantaCall', 'ToyUkulele', 'Trumpet', 'WinterPiano', 'Xylophone'
        ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle('系统设置')
        self.create_player_type_combo(parent)
        self.create_instruments_combo(parent)
        self.create_speed_control(parent)

    def create_player_type_combo(self, parent):
        combo = ComboBox(parent)
        combo.addItems(self.player_types)
        combo.currentIndexChanged.connect(lambda idx: self.current_index_changed('type', idx))
        combo.setCurrentIndex(self.player_types.index(conf.player.type))
        self.addGroup(FluentIcon.TILES, '播放类型', '选择软件播放类型', combo)

    def create_instruments_combo(self, parent):
        combo = ComboBox(parent)
        combo.addItems(self.instruments)
        combo.currentIndexChanged.connect(lambda idx: self.current_index_changed('instruments', idx))
        combo.setCurrentIndex(self.instruments.index(conf.player.instruments))
        self.addGroup(FluentIcon.MUSIC, 'Instrument Selection', 'Select the instrument you want to use', combo)

    def create_speed_control(self, parent):
        speed_control = LineEdit(parent)
        speed_control.setPlaceholderText('请输入每拍增加的速度')
        speed_control.setText(str(conf.control.speed))
        speed_control.editingFinished.connect(lambda: self.update_config('control.speed', speed_control.text(), speed_control))
        self.addGroup(FluentIcon.ADD, '速度控制', '设置每拍增加的速度', speed_control)

    def current_index_changed(self, setting: str, index: int) -> None:
        if setting == 'type':
            conf.player.type = self.player_types[index]
        elif setting == 'instruments':
            conf.player.instruments = self.instruments[index]
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
