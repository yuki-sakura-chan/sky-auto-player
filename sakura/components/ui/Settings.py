import os
import sys
from pathlib import Path

from PySide6.QtWidgets import QFrame, QVBoxLayout, QSizePolicy, QSpacerItem, QFileDialog
from qfluentwidgets import GroupHeaderCardWidget, FluentIcon, ComboBox, LineEdit, Dialog, ToolButton

from sakura.components.ui import languages
from sakura.config import conf, save_conf
from sakura.db.JsonPick import insert_locale_data
from sakura.locales.locale import load_locale_messages

locales = load_locale_messages('settings')


def update_config(attribute: str, value: str, attributes: LineEdit) -> None:
    try:
        if attribute == 'control.speed':
            conf.control.speed = str(float(value))
        # elif attribute == 'player.type':
        #     conf.player.type = value
        save_conf(conf)
        attributes.clearFocus()
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred while updating {attribute} - {value}: {e}")


class BaseSettingsGroup(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBorderRadius(8)


class SystemSettingsGroup(BaseSettingsGroup):
    items: list[str] = ['demo', 'win']
    languages: list[str] = ['简体中文', '繁體中文', 'English']

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(locales.messages('title'))
        self.create_combo_box(parent)
        self.create_language_change_box(parent)

    def create_combo_box(self, parent):
        combo = ComboBox(parent)
        combo.addItems(self.items)
        combo.setCurrentIndex(self.items.index(conf.player.type))
        combo.currentIndexChanged.connect(self.current_index_changed)
        self.addGroup(FluentIcon.TILES, locales.messages('play_type.title'),
                      locales.messages('play_type.content'), combo)

    def create_language_change_box(self, parent):
        combo = ComboBox(parent)
        combo.addItems(self.languages)
        current_items = next((k for k, v in languages.items() if v["key"] == conf.region), None)
        combo.setCurrentIndex(self.languages.index(current_items))
        combo.currentIndexChanged.connect(self.language_changed)
        self.addGroup(FluentIcon.LANGUAGE, locales.messages('region.title'),
                      locales.messages('region.content'), combo)

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
            os.execl(sys.executable, sys.executable, *sys.argv)


class SongsSettingsGroup(BaseSettingsGroup):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle('歌曲设置')
        self.create_speed_control(parent)
        self.create_songs_file_import(parent)

    def create_speed_control(self, parent):
        speed_control = LineEdit(parent)
        speed_control.setPlaceholderText(locales.messages('speed_control.PlaceholderText'))
        speed_control.setText(str(conf.control.speed))
        speed_control.editingFinished.connect(
            lambda: update_config('control.speed', speed_control.text(), speed_control))
        self.addGroup(FluentIcon.ADD, locales.messages('speed_control.title'),
                      locales.messages('speed_control.content'), speed_control)

    def create_songs_file_import(self, parent):
        button = ToolButton(parent)
        button.setIcon(FluentIcon.FOLDER)
        self.addGroup(FluentIcon.ADD, locales.messages('songs.file_import.title'),
                      locales.messages('songs.file_import.content'), button)
        button.clicked.connect(self.select_files)

    def select_files(self):
        paths, _ = QFileDialog.getOpenFileNames(self, locales.messages('songs.select_files.caption'), '',
                                                'JSON Files (*.json *.txt);;All Files (*)')
        if paths:
            path_dict = {}
            for p in paths:
                path = Path(p)
                if str(path.parent) not in path_dict:
                    path_dict[str(path.parent)] = [path.name]
                else:
                    path_dict[str(path.parent)].append(path.name)
            for k, v in path_dict.items():
                insert_locale_data(k, v)


class SettingsUi(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('Settings')
        layout = QVBoxLayout(self)
        system = SystemSettingsGroup()
        songs = SongsSettingsGroup()
        spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(system)
        layout.addWidget(songs)
        layout.addSpacerItem(spacer)

    def mousePressEvent(self, event) -> None:
        for widget in self.findChildren(LineEdit):
            widget.clearFocus()
        super().mousePressEvent(event)
