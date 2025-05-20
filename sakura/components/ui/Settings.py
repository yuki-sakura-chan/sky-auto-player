import sys

from PySide6.QtCore import QProcess
from PySide6.QtWidgets import QFrame, QVBoxLayout, QSizePolicy, QSpacerItem, QApplication
from qfluentwidgets import GroupHeaderCardWidget, FluentIcon, ComboBox, LineEdit, Dialog

from sakura.components.ui import languages
from sakura.config import conf, save_conf
from sakura.locales.locale import load_locale_messages, Locale


class BaseSettingsGroup(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBorderRadius(8)


class SystemSettingsGroup(BaseSettingsGroup):
    items: list[str] = ['demo', 'win']
    languages: list[str] = ['简体中文', '繁體中文', 'English']
    locales: Locale

    def __init__(self, parent=None):
        super().__init__(parent)
        self.locales = load_locale_messages('settings')
        self.setTitle(self.locales.messages('title'))
        self.create_combo_box(parent)
        self.create_speed_control(parent)
        self.create_language_change_box(parent)

    def create_combo_box(self, parent):
        combo = ComboBox(parent)
        combo.addItems(self.items)
        combo.setCurrentIndex(self.items.index(conf.player.type))
        combo.currentIndexChanged.connect(self.current_index_changed)
        self.addGroup(FluentIcon.TILES, self.locales.messages('play_type.title'),
                      self.locales.messages('play_type.content'), combo)

    def create_speed_control(self, parent):
        speed_control = LineEdit(parent)
        speed_control.setPlaceholderText(self.locales.messages('speed_control.PlaceholderText'))
        speed_control.setText(str(conf.control.speed))
        speed_control.editingFinished.connect(
            lambda: self.update_config('control.speed', speed_control.text(), speed_control))
        self.addGroup(FluentIcon.ADD, self.locales.messages('speed_control.title'),
                      self.locales.messages('speed_control.content'), speed_control)

    def create_language_change_box(self, parent):
        combo = ComboBox(parent)
        combo.addItems(self.languages)
        current_items = next((k for k, v in languages.items() if v["key"] == conf.region), None)
        combo.setCurrentIndex(self.languages.index(current_items))
        combo.currentIndexChanged.connect(self.language_changed)
        self.addGroup(FluentIcon.LANGUAGE, self.locales.messages('region.title'),
                      self.locales.messages('region.content'), combo)

    def current_index_changed(self, index: int) -> None:
        conf.player.type = self.items[index]
        save_conf(conf)

    def language_changed(self, index: int) -> None:
        w = Dialog(languages[self.languages[index]]['title'], languages[self.languages[index]]['content'], self)
        if conf.region == languages[self.languages[index]]["key"]:
            return
        if w.exec():
            conf.region = languages[self.languages[index]]["key"]
            save_conf(conf)
            QApplication.quit()
            process = QProcess()
            process.startDetached(sys.executable, sys.argv)

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
