from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QVBoxLayout, QSizePolicy, QSpacerItem, QDialog
from qfluentwidgets import (GroupHeaderCardWidget, FluentIcon, ComboBox, LineEdit, PushButton, ProgressBar, 
                           InfoBar, InfoBarPosition)

from sakura.config import conf, save_conf
from sakura.components.ui.DownloadDialog import DownloadDialog
from sakura.components.InstrumentsManager import InstrumentsManager


class BaseSettingsGroup(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBorderRadius(8)


class SystemSettingsGroup(BaseSettingsGroup):
    player_types: list[str] = ['demo', 'win']
    
    def __init__(self, parent=None, instruments_manager=None):
        super().__init__(parent)
        self.setTitle('系统设置')
        
        self.instruments_manager = instruments_manager or InstrumentsManager()
        
        self._init_ui(parent)
    
    def _init_ui(self, parent):
        """Initialization of all UI components"""
        self.create_player_type_combo(parent)
        self.create_speed_control(parent)
        self.create_instruments_combo(parent)
        self.create_instruments_section()

    def create_instruments_section(self):
        self.download_button = PushButton('Download Instruments')
        self.download_button.clicked.connect(self._download_instruments)
        
        self.addGroup(
            FluentIcon.DOWNLOAD,
            'Instruments',
            'Download and manage instruments',
            self.download_button
        )
        
    def _download_instruments(self):
        dialog = DownloadDialog(self.instruments_manager, self)
        
        try:
            self.download_button.setEnabled(False)
            dialog.show()
            dialog.start_download()
            
            result = dialog.exec()
            
            if result == QDialog.Accepted:
                self.instruments_manager.update_instruments_combo(self.instruments_combo)
                
                InfoBar.success(
                    title='Download Complete',
                    content='Musical instruments have been successfully downloaded and installed',
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
            else:
                if hasattr(dialog.download_thread, '_is_cancelled') and dialog.download_thread._is_cancelled:
                    InfoBar.warning(
                        title='Download Cancelled',
                        content='The download was cancelled by user',
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=3000,
                        parent=self
                    )
                else:
                    InfoBar.error(
                        title='Download Failed',
                        content='Failed to download instruments. Please check your internet connection and try again',
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=5000,
                        parent=self
                    )
                    
        finally:
            self.download_button.setEnabled(True)
            
    def create_player_type_combo(self, parent):
        combo = ComboBox(parent)
        combo.addItems(self.player_types)
        combo.currentIndexChanged.connect(lambda idx: self.current_index_changed('type', idx))
        combo.setCurrentIndex(self.player_types.index(conf.player.type))
        self.addGroup(FluentIcon.TILES, '播放类型', '选择软件播放类型', combo)

    def create_instruments_combo(self, parent):
        self.instruments_combo = ComboBox(parent)
        
        self.instruments_manager.update_instruments_combo(self.instruments_combo)
        
        self.instruments_combo.currentIndexChanged.connect(
            lambda index: self.instruments_manager.handle_combo_index_change(
                self.instruments_combo, 
                index
            )
        )
            
        self.addGroup(
            FluentIcon.MUSIC,
            'Instrument Selection',
            'Select the instrument you want to use',
            self.instruments_combo
        )

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
