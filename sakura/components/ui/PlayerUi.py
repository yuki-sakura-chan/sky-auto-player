import time

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QListWidgetItem
from qfluentwidgets import ListWidget, SearchLineEdit, PipsPager, PipsScrollButtonDisplayMode, ToolButton, FluentIcon, \
    TitleLabel, MessageBox

from sakura.components.SakuraPlayBar import SakuraPlayBar
from sakura.components.ui import main_width
from sakura.config import conf
from sakura.db.DBManager import song_client
from sakura.db.JsonPick import get_file_list, load_locale_data
from sakura.db.model.PageData import PageData
from sakura.db.model.SongModel import SongModel
from sakura.locales.locale import load_locale_messages


class PlayerUi(QFrame):
    file_list_box: ListWidget
    search_input: SearchLineEdit
    play: SakuraPlayBar
    pager: PipsPager
    _search_last = 0
    _selected_info_song_id: int = 0

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_search = ''
        self._search_cache = {}
        self.setObjectName("Player")
        self.locales = load_locale_messages('player-ui')
        locales = self.locales
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        # 创建主容器
        main_container = QFrame()
        # 添加主容器到主布局
        main_layout.addWidget(main_container)
        main_container.setFixedWidth(main_width)
        # 创建主容器布局
        container_layout = QVBoxLayout(main_container)
        # 创建文件信息布局
        file_info_layout = QHBoxLayout()
        file_info_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        search_input = SearchLineEdit()
        search_input.searchSignal.connect(self.search)
        search_input.clearSignal.connect(self.clear_search)
        search_input.textChanged.connect(self.update_search)
        search_input.returnPressed.connect(self.handle_search_complete)
        search_input.installEventFilter(self)
        search_input.setFixedWidth(400)
        self.search_input = search_input
        # 加载文件列表
        file_list_layout = QVBoxLayout()
        file_list_box = ListWidget()
        self.file_list_box = file_list_box
        file_list_box.setFixedSize(search_input.width(), 600)
        file_list_box.setSpacing(0.5)
        if song_client.db_is_null():
            file_list = get_file_list(conf.file_path)
            load_locale_data(conf.file_path, file_list)
        # 创建分页器
        pager = PipsPager(orientation=Qt.Orientation.Horizontal)
        self.pager = pager
        pager.setVisibleNumber(8)
        pager.setNextButtonDisplayMode(PipsScrollButtonDisplayMode.ALWAYS)
        pager.setPreviousButtonDisplayMode(PipsScrollButtonDisplayMode.ALWAYS)
        self._perform_search()
        pager.currentIndexChanged.connect(lambda i: self._perform_search(i + 1))
        # 添加文件列表到主容器布局
        file_list_layout.addWidget(search_input)
        file_list_layout.addWidget(file_list_box)
        file_list_layout.addWidget(pager)
        file_info_layout.addLayout(file_list_layout)
        # 创建信息框
        info_frame = QFrame(main_container)
        info_frame.setFixedHeight(file_list_box.height())
        info_frame.setFixedWidth(int(main_container.width() - search_input.width() * 1.1))
        info_header_layout = QHBoxLayout(info_frame)
        # 创建删除按钮
        delete_button = ToolButton()
        delete_button.setIcon(FluentIcon.DELETE)
        # 创建标题标签
        info_title = TitleLabel()
        info_title.setText(locales.messages('info.title'))
        self.delete_button = delete_button
        self.info_title = info_title
        info_header_layout.addWidget(info_title)
        info_header_layout.addStretch()
        info_header_layout.addWidget(delete_button)
        info_header_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        file_list_box.clicked.connect(self.song_info)
        delete_button.clicked.connect(self.delete_song)
        # 添加信息框到主容器布局
        file_info_layout.addWidget(info_frame)
        # 创建播放器布局
        player_layout = QVBoxLayout()
        player_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        # 创建播放器
        play = SakuraPlayBar(file_list_box=self.file_list_box, temp_layout=player_layout)
        player_layout.addWidget(play)
        self.play = play
        player_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        # 添加双击播放音频事件
        file_list_box.doubleClicked.connect(self.double_clicked)
        # 添加播放器到主容器布局
        container_layout.addLayout(file_info_layout)
        container_layout.addLayout(player_layout)

        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._perform_search)

    def clear_search(self) -> None:
        self.search('')

    def update_search(self, text: str) -> None:
        self.search(text)

    def search(self, text: str) -> None:
        self._search_timer.stop()
        self._search_timer.start(100)
        self._current_search = text

    def _perform_search(self, current: int = 1) -> None:
        # 防抖
        now = time.time()
        if now - self._search_last < 0.1:
            return
        self._current = current
        self._search_last = now
        text = self._current_search
        cache = {}
        if text != '' and f'{text}:{current}' in self._search_cache:
            cache = self._search_cache[f'{text}:{current}']
        else:
            results = self.page(current, keyword=text)
            cache['data'] = results.data
            cache['pageNumber'] = results.get_page_number()
            self._search_cache[f'{text}:{current}'] = cache
        # 防止频繁改变 pagerNumber 的值
        if self.pager.getPageNumber() != cache['pageNumber']:
            self.pager.setPageNumber(cache['pageNumber'])
        self.load_songs(cache['data'])
        file_list = self.file_list_box
        for i in range(file_list.count()):
            item = file_list.item(i)
            if item.data(1) == self._selected_info_song_id:
                file_list.setCurrentItem(item)
                return
        file_list.setCurrentItem(None)

    def handle_search_complete(self) -> None:
        self.search(self.search_input.text())
        self.search_input.clearFocus()

    def eventFilter(self, watched, event) -> bool:
        if watched == self.search_input and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return:
                self.handle_search_complete()
                return True
        return super().eventFilter(watched, event)

    def mousePressEvent(self, event) -> None:
        if not self.search_input.geometry().contains(event.pos()):
            self.search_input.clearFocus()
        super().mousePressEvent(event)

    def get_file_list_box(self) -> ListWidget:
        return self.file_list_box

    def double_clicked(self) -> None:
        self.play.play()

    def load_songs(self, songs: list[SongModel]) -> None:
        self.file_list_box.clear()
        for index, v in enumerate(songs):
            item = QListWidgetItem(v.name)
            item.setData(1, v.id)
            self.file_list_box.addItem(item)

    def page(self, current: int = 1, keyword: str = '') -> PageData:
        """
        Get songs by pagination

        Args:
            current: Current page
            keyword: Keyword
        Return:
            Page number
        """
        page_data = PageData(size=15)
        total = song_client.select_count(keyword)
        if total == 0:
            return PageData()
        songs = song_client.page(current, keyword, page_data.size)
        page_data.data = songs
        page_data.total = total
        return page_data

    def song_info(self) -> None:
        info_title = self.info_title
        file_list_box = self.file_list_box
        current_item = file_list_box.currentItem()
        song_id = current_item.data(1)
        self._selected_info_song_id = song_id
        song = song_client.select_by_id(song_id)
        info_title.setText(song.name if song else self.locales.messages('info.title'))

    def delete_song(self) -> None:
        song_id = self._selected_info_song_id
        if song_id == 0:
            return
        song = song_client.select_by_id(song_id)
        if song is None:
            return
        locales = self.locales
        title = locales.messages('delete.dialog.title')
        content = locales.messages('delete.dialog.content').format(song.name)
        m = MessageBox(title, content, self)
        m.setClosableOnMaskClicked(True)
        if m.exec():
            flag = song_client.delete_by_id(song_id)
            if flag:
                self._perform_search(self._current)
                self._search_cache.clear()
                self.play.pause()
                self.info_title.setText(locales.messages('info.title'))
