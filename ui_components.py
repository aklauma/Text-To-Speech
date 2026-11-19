from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QCheckBox, QComboBox, QSlider, QPlainTextEdit,
    QListWidget, QStackedWidget, QSizePolicy
)
from i18n import t


class AppTitleBar(QWidget):
    """
    Кастомный безрамочный заголовок:
    - Индикатор :: TWITCH TTS
    - Статус глиф ( ● ) LIVE / ( ○ ) OFFLINE
    - Пиксельные кнопки управления окном [ — ] и [ ✕ ]
    - Перетаскивание окна мышью (с поддержкой startSystemMove)
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName('titleBar')
        self._drag_pos = None
        self._is_live = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 8, 0)
        layout.setSpacing(10)

        # Логотип / Название
        self.title_label = QLabel(t('title'))
        self.title_label.setObjectName('titleLabel')
        layout.addWidget(self.title_label)

        layout.addStretch()

        # Статус-бейдж
        self.status_badge = QLabel(t('offline'))
        self.status_badge.setObjectName('statusBadgeIdle')
        layout.addWidget(self.status_badge)

        # Кнопки управления окном
        self.min_btn = QPushButton('—')
        self.min_btn.setObjectName('winBtnMin')
        self.min_btn.setCursor(Qt.PointingHandCursor)
        self.min_btn.clicked.connect(self._minimize_window)
        layout.addWidget(self.min_btn)

        self.close_btn = QPushButton('✕')
        self.close_btn.setObjectName('winBtnClose')
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self._close_window)
        layout.addWidget(self.close_btn)

    def set_status(self, is_live: bool, text: str = None):
        self._is_live = is_live
        if is_live:
            self.status_badge.setText(text or t('live'))
            self.status_badge.setObjectName('statusBadgeLive')
        else:
            self.status_badge.setText(text or t('offline'))
            self.status_badge.setObjectName('statusBadgeIdle')

        self.status_badge.style().unpolish(self.status_badge)
        self.status_badge.style().polish(self.status_badge)

    def update_texts(self):
        self.title_label.setText(t('title'))
        self.set_status(self._is_live)

    def _minimize_window(self):
        w = self.window()
        if w:
            w.showMinimized()

    def _close_window(self):
        w = self.window()
        if w:
            w.close()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            w = self.window()
            handle = w.windowHandle() if w else None
            if handle and hasattr(handle, 'startSystemMove'):
                handle.startSystemMove()
                event.accept()
                return
            self._drag_pos = event.globalPos() - self.window().pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos is not None:
            self.window().move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None


class SegmentedSwitch(QWidget):
    """
    Сегментированный переключатель:
    [ LOG ]  [ BLACKLIST ]  [ REWARDS ]
    """
    tab_changed = pyqtSignal(int)

    def __init__(self, tabs, parent=None):
        super().__init__(parent)
        self.buttons = []
        self.current_index = 0

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        for i, title in enumerate(tabs):
            btn = QPushButton(f'[ {title.upper()} ]')
            btn.setProperty('class', 'SegmentBtn')
            btn.setProperty('active', 'true' if i == 0 else 'false')
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, idx=i: self.set_current_index(idx))
            layout.addWidget(btn)
            self.buttons.append(btn)

        layout.addStretch()

    def update_texts(self, titles):
        for i, title in enumerate(titles):
            if i < len(self.buttons):
                self.buttons[i].setText(f'[ {title.upper()} ]')

    def set_current_index(self, index: int):
        if self.current_index == index and index != 0:
            return
        self.current_index = index
        for i, btn in enumerate(self.buttons):
            is_active = (i == index)
            btn.setProperty('active', 'true' if is_active else 'false')
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self.tab_changed.emit(index)


class ControlsPanel(QWidget):
    """
    Левая карточка управления:
    - Конфигурация языка, токена и канала
    - Выбор голоса и слайдер громкости
    - Кнопки TEST и START/STOP
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setProperty('class', 'PixelCard')

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        # Заголовок секции
        self.hdr = QLabel(t('config_controls'))
        self.hdr.setProperty('class', 'CardHeader')
        layout.addWidget(self.hdr)

        # Выбор языка
        self.lang_lbl = QLabel(t('language'))
        layout.addWidget(self.lang_lbl)

        self.lang_box = QComboBox()
        self.lang_box.addItem('SYSTEM', 'auto')
        self.lang_box.addItem('РУССКИЙ', 'ru')
        self.lang_box.addItem('ENGLISH', 'en')
        layout.addWidget(self.lang_box)

        layout.addSpacing(2)

        # Токен
        self.token_lbl = QLabel(t('oauth_token'))
        layout.addWidget(self.token_lbl)

        self.token_edit = QLineEdit()
        self.token_edit.setEchoMode(QLineEdit.Password)
        self.token_edit.setPlaceholderText(t('token_placeholder'))
        layout.addWidget(self.token_edit)

        self.remember_check = QCheckBox(t('remember_token'))
        layout.addWidget(self.remember_check)

        layout.addSpacing(2)

        # Канал
        self.channel_lbl = QLabel(t('twitch_channel'))
        layout.addWidget(self.channel_lbl)

        self.channel_edit = QLineEdit()
        self.channel_edit.setPlaceholderText(t('channel_placeholder'))
        layout.addWidget(self.channel_edit)

        layout.addSpacing(2)

        # Голос
        self.voice_lbl = QLabel(t('voice_engine'))
        layout.addWidget(self.voice_lbl)

        self.voice_box = QComboBox()
        layout.addWidget(self.voice_box)

        layout.addSpacing(2)

        # Громкость
        vol_header = QHBoxLayout()
        self.vol_lbl = QLabel(t('volume'))
        self.vol_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.vol_val_lbl = QLabel('25%')
        self.vol_val_lbl.setObjectName('volValLabel')
        vol_header.addWidget(self.vol_lbl)
        vol_header.addWidget(self.vol_val_lbl)
        layout.addLayout(vol_header)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(25)
        self.volume_slider.valueChanged.connect(
            lambda v: self.vol_val_lbl.setText(f'{v}%')
        )
        layout.addWidget(self.volume_slider)

        layout.addSpacing(8)

        # Кнопка тестирования звука
        self.test_btn = QPushButton(t('test_voice'))
        self.test_btn.setObjectName('testBtn')
        self.test_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.test_btn)

        layout.addStretch()

        # Кнопка запуска/остановки бота
        self.start_btn = QPushButton(t('start_bot'))
        self.start_btn.setObjectName('startBtn')
        self.start_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.start_btn)

    def update_texts(self, is_running=False):
        self.hdr.setText(t('config_controls'))
        self.lang_lbl.setText(t('language'))
        self.lang_box.setItemText(0, 'SYSTEM')
        self.token_lbl.setText(t('oauth_token'))
        self.token_edit.setPlaceholderText(t('token_placeholder'))
        self.remember_check.setText(t('remember_token'))
        self.channel_lbl.setText(t('twitch_channel'))
        self.channel_edit.setPlaceholderText(t('channel_placeholder'))
        self.voice_lbl.setText(t('voice_engine'))
        self.vol_lbl.setText(t('volume'))
        self.test_btn.setText(t('test_voice'))
        self.start_btn.setText(t('stop_bot') if is_running else t('start_bot'))


class LogPanel(QWidget):
    """
    Правая панель чат-лога
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setProperty('class', 'PixelCard')

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        self.hdr = QLabel(t('live_chat_log'))
        self.hdr.setProperty('class', 'CardHeader')
        layout.addWidget(self.hdr)

        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMaximumBlockCount(1000)
        layout.addWidget(self.log_view)

        # Нижняя строка управления
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 4, 0, 0)

        self.auto_scroll_check = QCheckBox(t('auto_scroll'))
        self.auto_scroll_check.setChecked(True)
        self.auto_scroll_check.setMinimumWidth(160)
        bottom_layout.addWidget(self.auto_scroll_check)

        bottom_layout.addStretch()

        self.clear_btn = QPushButton(t('clear_log'))
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.clicked.connect(self.log_view.clear)
        bottom_layout.addWidget(self.clear_btn)

        layout.addLayout(bottom_layout)

    def update_texts(self):
        self.hdr.setText(t('live_chat_log'))
        self.auto_scroll_check.setText(t('auto_scroll'))
        self.clear_btn.setText(t('clear_log'))


class BlacklistListWidget(QListWidget):
    """
    QListWidget с поддержкой удаления по клавише Delete.
    """
    delete_pressed = pyqtSignal()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.delete_pressed.emit()
            event.accept()
        else:
            super().keyPressEvent(event)


class BlacklistPanel(QWidget):
    """
    Панель чёрного списка с возможностью удаления по кнопке и клавише Delete.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setProperty('class', 'PixelCard')

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        self.hdr = QLabel(t('blacklist_title'))
        self.hdr.setProperty('class', 'CardHeader')
        layout.addWidget(self.hdr)

        # Строка добавления
        add_layout = QHBoxLayout()
        add_layout.setSpacing(6)

        self.user_edit = QLineEdit()
        self.user_edit.setPlaceholderText(t('username_placeholder'))
        add_layout.addWidget(self.user_edit)

        self.add_btn = QPushButton(t('add_user'))
        self.add_btn.setCursor(Qt.PointingHandCursor)
        add_layout.addWidget(self.add_btn)

        layout.addLayout(add_layout)

        # Список пользователей с обработкой клавиши Delete
        self.users_list = BlacklistListWidget()
        layout.addWidget(self.users_list)

        # Кнопка удаления
        self.remove_btn = QPushButton(t('remove_selected'))
        self.remove_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.remove_btn)

    def update_texts(self):
        self.hdr.setText(t('blacklist_title'))
        self.user_edit.setPlaceholderText(t('username_placeholder'))
        self.add_btn.setText(t('add_user'))
        self.remove_btn.setText(t('remove_selected'))


class RewardsPlaceholder(QWidget):
    """
    Стильная минималистичная карточка-заглушка
    для будущей интеграции наград за баллы канала (Twitch Channel Points).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setProperty('class', 'PixelCard')

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 30, 20, 30)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)

        glyph = QLabel(
            "   [ · · · · · ]\n"
            " [ · ·       · · ]\n"
            " [ ·   REWARD  · ]\n"
            " [ · ·       · · ]\n"
            "   [ · · · · · ]"
        )
        glyph.setObjectName('rewardsGlyph')
        glyph.setAlignment(Qt.AlignCenter)
        layout.addWidget(glyph)

        self.title = QLabel(t('rewards_title'))
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet('font-size: 13px; font-weight: bold; color: #FFFFFF; letter-spacing: 2px;')
        layout.addWidget(self.title)

        self.desc = QLabel(t('rewards_desc'))
        self.desc.setAlignment(Qt.AlignCenter)
        self.desc.setStyleSheet('color: #666666; font-size: 10px; line-height: 1.6;')
        layout.addWidget(self.desc)

    def update_texts(self):
        self.title.setText(t('rewards_title'))
        self.desc.setText(t('rewards_desc'))
