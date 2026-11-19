import asyncio
import json
import os
import queue
import sys
import threading
import time
from datetime import datetime
from xml.sax.saxutils import escape

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QRect, QEvent, QLocale
from PyQt5.QtGui import QFont, QFontDatabase, QKeySequence, QIcon, QColor, QPalette
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QShortcut, QSizeGrip, QLabel, QPushButton,
    QLineEdit, QCheckBox, QComboBox, QSlider, QPlainTextEdit,
    QListWidget, QSizePolicy
)
from twitchio.ext import commands


def resource_path(name):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

SETTINGS_PATH = os.path.join(APP_DIR, 'settings.json')


# ===================================================================
# 1. ТЕМАТИЗАЦИЯ И СИСТЕМНЫЙ АКЦЕНТ WINDOWS (DWM)
# ===================================================================
DEFAULT_ACCENT = "#D71920"

STYLE_QSS = """
/* Global Settings */
QWidget {
    background-color: #080808;
    color: #FFFFFF;
    font-family: "Monocraft", "Silkscreen", "Consolas", monospace;
    font-size: 11px;
    selection-background-color: @ACCENT@;
    selection-color: #FFFFFF;
}

QLabel {
    background-color: transparent;
}

/* Frameless Window Border */
#centralWidget {
    background-color: #080808;
    border: 1px solid #2B2B2B;
}

#volValLabel {
    color: @ACCENT@;
    font-weight: bold;
}

#rewardsGlyph {
    color: @ACCENT@;
    font-weight: bold;
}

/* Title Bar */
#titleBar {
    background-color: #0C0C0C;
    border-bottom: 1px solid #242424;
    min-height: 38px;
    max-height: 38px;
}

#titleLabel {
    font-size: 11px;
    font-weight: bold;
    color: #FFFFFF;
    letter-spacing: 1px;
    padding-left: 8px;
}

#statusBadgeLive {
    background-color: @ACCENT@;
    color: #FFFFFF;
    border: 1px solid @ACCENT@;
    border-radius: 2px;
    padding: 3px 8px;
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 1px;
}

#statusBadgeIdle {
    background-color: #161616;
    color: #888888;
    border: 1px solid #333333;
    border-radius: 2px;
    padding: 3px 8px;
    font-size: 10px;
    letter-spacing: 1px;
}

#winBtnMin, #winBtnMax, #winBtnClose {
    background-color: transparent;
    border: none;
    color: #AAAAAA;
    font-size: 13px;
    font-weight: bold;
    min-width: 38px;
    min-height: 38px;
    padding: 0px;
}

#winBtnMin:hover, #winBtnMax:hover {
    background-color: #222222;
    color: #FFFFFF;
}

#winBtnClose:hover {
    background-color: @ACCENT@;
    color: #FFFFFF;
}

/* Panels */
QWidget[class="PixelCard"] {
    background-color: #101010;
    border: 1px solid #242424;
    border-radius: 0px;
}

QLabel[class="CardHeader"], .CardHeader {
    font-size: 11px;
    font-weight: bold;
    color: #888888;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 6px;
}

/* Buttons */
QPushButton {
    background-color: #181818;
    border: 1px solid #333333;
    border-radius: 0px;
    color: #FFFFFF;
    padding: 6px 12px;
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 0.5px;
}

QPushButton:hover {
    background-color: #262626;
    border: 1px solid #777777;
    color: #FFFFFF;
}

QPushButton:pressed {
    background-color: #FFFFFF;
    border: 1px solid #FFFFFF;
    color: #000000;
}

QPushButton:disabled {
    background-color: #101010;
    border: 1px solid #202020;
    color: #444444;
}

#startBtn {
    background-color: @ACCENT@;
    border: 1px solid @ACCENT@;
    color: #FFFFFF;
    font-weight: bold;
    font-size: 11px;
    padding: 8px 14px;
}

#startBtn:hover {
    background-color: @ACCENT_HOVER@;
    border: 1px solid #FFFFFF;
}

#startBtn:pressed {
    background-color: #FFFFFF;
    color: #000000;
}

#stopBtn {
    background-color: #181818;
    border: 1px solid @ACCENT@;
    color: @ACCENT@;
    font-weight: bold;
    font-size: 11px;
    padding: 8px 14px;
}

#stopBtn:hover {
    background-color: @ACCENT@;
    color: #FFFFFF;
}

#testBtn {
    background-color: #161616;
    border: 1px solid #3A3A3A;
    color: #CCCCCC;
}

#testBtn:hover {
    border: 1px solid @ACCENT@;
    color: #FFFFFF;
}

/* Segmented Buttons */
QPushButton.SegmentBtn {
    background-color: #101010;
    border: 1px solid #242424;
    color: #777777;
    padding: 6px 14px;
    font-size: 10px;
}

QPushButton.SegmentBtn:hover {
    color: #FFFFFF;
    border: 1px solid #444444;
}

QPushButton.SegmentBtn[active="true"] {
    background-color: #FFFFFF;
    border: 1px solid #FFFFFF;
    color: #000000;
    font-weight: bold;
}

/* Inputs & ComboBox */
QLineEdit {
    background-color: #0A0A0A;
    border: 1px solid #262626;
    border-radius: 0px;
    color: #FFFFFF;
    padding: 5px 8px;
    font-size: 11px;
}

QLineEdit:focus {
    border: 1px solid @ACCENT@;
}

QLineEdit:disabled {
    background-color: #060606;
    border: 1px solid #1A1A1A;
    color: #555555;
}

QComboBox {
    background-color: #0A0A0A;
    border: 1px solid #262626;
    border-radius: 0px;
    color: #FFFFFF;
    padding: 5px 8px;
    font-size: 11px;
}

QComboBox:focus, QComboBox:hover {
    border: 1px solid @ACCENT@;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #FFFFFF;
    margin-right: 6px;
}

QComboBox QAbstractItemView {
    background-color: #121212;
    border: 1px solid #333333;
    color: #FFFFFF;
    selection-background-color: @ACCENT@;
    selection-color: #FFFFFF;
    outline: none;
    padding: 4px;
}

/* Checkbox */
QCheckBox {
    background-color: transparent;
    spacing: 8px;
    color: #888888;
    font-size: 10px;
}

QCheckBox:hover {
    color: #FFFFFF;
}

QCheckBox::indicator {
    width: 14px;
    height: 14px;
    background-color: #0A0A0A;
    border: 1px solid #333333;
    border-radius: 0px;
}

QCheckBox::indicator:hover {
    border: 1px solid #FFFFFF;
}

QCheckBox::indicator:checked {
    background-color: #FFFFFF;
    border: 3px solid @ACCENT@;
}

/* Slider */
QSlider::groove:horizontal {
    height: 4px;
    background: #202020;
    border-radius: 0px;
}

QSlider::sub-page:horizontal {
    background: @ACCENT@;
}

QSlider::handle:horizontal {
    background: #FFFFFF;
    border: 1px solid #000000;
    width: 10px;
    margin-top: -6px;
    margin-bottom: -6px;
    border-radius: 0px;
}

QSlider::handle:horizontal:hover {
    background: @ACCENT_HOVER@;
}

/* Lists and Text */
QPlainTextEdit {
    background-color: #0A0A0A;
    border: 1px solid #202020;
    color: #E6E6E6;
    font-size: 11px;
    line-height: 1.4;
    padding: 8px;
}

QListWidget {
    background-color: #0A0A0A;
    border: 1px solid #202020;
    color: #FFFFFF;
    padding: 6px;
}

QListWidget::item {
    padding: 4px 6px;
    border-bottom: 1px solid #161616;
}

QListWidget::item:hover {
    background-color: #1A1A1A;
}

QListWidget::item:selected {
    background-color: @ACCENT@;
    color: #FFFFFF;
}

/* Scrollbar */
QScrollBar:vertical {
    background-color: #080808;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #242424;
    min-height: 20px;
    border-radius: 0px;
}

QScrollBar::handle:vertical:hover {
    background-color: @ACCENT@;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

QSizeGrip {
    background: transparent;
    width: 14px;
    height: 14px;
}
"""


def get_system_accent_color(default: str = DEFAULT_ACCENT) -> str:
    """Определяет акцентный цвет Windows из реестра DWM (AccentColor или ColorizationColor)."""
    if sys.platform == 'win32':
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\DWM")
            try:
                val, _ = winreg.QueryValueEx(key, "AccentColor")
                r = val & 0xFF
                g = (val >> 8) & 0xFF
                b = (val >> 16) & 0xFF
                return f"#{r:02x}{g:02x}{b:02x}"
            except FileNotFoundError:
                val, _ = winreg.QueryValueEx(key, "ColorizationColor")
                r = (val >> 16) & 0xFF
                g = (val >> 8) & 0xFF
                b = val & 0xFF
                return f"#{r:02x}{g:02x}{b:02x}"
            finally:
                winreg.CloseKey(key)
        except Exception:
            pass

    try:
        app = QApplication.instance()
        if app:
            col = app.palette().color(QPalette.Highlight)
            if col.isValid() and col.name().lower() not in ('#000000', '#ffffff'):
                return col.name()
    except Exception:
        pass

    return default


def get_accent_hover(hex_color: str) -> str:
    c = QColor(hex_color)
    if c.isValid():
        return c.lighter(120).name()
    return hex_color


def load_stylesheet_with_accent(accent_color: str = None) -> str:
    if not accent_color:
        accent_color = get_system_accent_color()
    hover_color = get_accent_hover(accent_color)

    qss = STYLE_QSS.replace('@ACCENT@', accent_color)
    qss = qss.replace('@ACCENT_HOVER@', hover_color)
    return qss


# ===================================================================
# 2. МУЛЬТИЯЗЫЧНОСТЬ (SYSTEM / RU / EN)
# ===================================================================
TRANSLATIONS = {
    'ru': {
        'title': ':: TWITCH TTS',
        'offline': '( ○ ) ОФФЛАЙН',
        'live': '( ● ) В ЭФИРЕ',
        'tab_log': 'ЛОГ',
        'tab_blacklist': 'ЧЁРНЫЙ СПИСОК',
        'tab_rewards': 'НАГРАДЫ',
        'config_controls': '// НАСТРОЙКИ И УПРАВЛЕНИЕ',
        'language': 'ЯЗЫК ИНТЕРФЕЙСА:',
        'lang_system': 'SYSTEM',
        'lang_ru': 'РУССКИЙ',
        'lang_en': 'ENGLISH',
        'oauth_token': 'OAUTH ТОКЕН:',
        'token_placeholder': 'oauth:xxxxxxxxxxxx',
        'remember_token': 'ЗАПОМНИТЬ ТОКЕН',
        'twitch_channel': 'КАНАЛ TWITCH:',
        'channel_placeholder': 'имя_канала',
        'voice_engine': 'ГОЛОС ОЗВУЧКИ:',
        'volume': 'ГРОМКОСТЬ:',
        'test_voice': '[ ▶ ТЕСТ ЗВУКА ]',
        'start_bot': '[ ▶ ЗАПУСТИТЬ ]',
        'stop_bot': '[ ■ ОСТАНОВИТЬ ]',
        'live_chat_log': '// ЖИВОЙ ЧАТ ТРАНСЛЯЦИИ',
        'auto_scroll': 'АВТОПРОКРУТКА',
        'clear_log': '[ ОЧИСТИТЬ ЛОГ ]',
        'blacklist_title': '// ИГНОРИРУЕМЫЕ (ЧЁРНЫЙ СПИСОК)',
        'username_placeholder': 'никнейм',
        'add_user': '[ + ДОБАВИТЬ ]',
        'remove_selected': '[ - УДАЛИТЬ (DEL) ]',
        'rewards_title': '// БАЛЛЫ КАНАЛА TWITCH',
        'rewards_desc': 'ИНТЕГРАЦИЯ ЧЕРЕЗ TWITCH EVENTSUB / PUBSUB\nАВТО-ЧТЕНИЕ НАГРАД ПО НАЗВАНИЮ И ID\n\nСТАТУС: [ В РАЗРАБОТКЕ ]',
        'test_speech_log': 'Проверка TTS [{voice}, Громкость {vol}%]: "{text}"',
        'test_phrase': 'Проверка звука. Тестовое сообщение.',
        'connected_as': 'Подключено как {nick}',
        'bot_stopped': 'Бот остановлен',
        'connecting': 'Подключение к Twitch...',
        'error_credentials': 'Ошибка: введите OAuth токен и имя канала',
        'added_blacklist': 'Добавлен в чёрный список: {name}',
        'removed_blacklist': 'Удалён из чёрного списка: {name}',
    },
    'en': {
        'title': ':: TWITCH TTS',
        'offline': '( ○ ) OFFLINE',
        'live': '( ● ) LIVE',
        'tab_log': 'LOG',
        'tab_blacklist': 'BLACKLIST',
        'tab_rewards': 'REWARDS',
        'config_controls': '// CONFIG & CONTROLS',
        'language': 'INTERFACE LANGUAGE:',
        'lang_system': 'SYSTEM',
        'lang_ru': 'РУССКИЙ',
        'lang_en': 'ENGLISH',
        'oauth_token': 'OAUTH TOKEN:',
        'token_placeholder': 'oauth:xxxxxxxxxxxx',
        'remember_token': 'REMEMBER TOKEN',
        'twitch_channel': 'TWITCH CHANNEL:',
        'channel_placeholder': 'channel_name',
        'voice_engine': 'VOICE ENGINE:',
        'volume': 'VOLUME:',
        'test_voice': '[ ▶ TEST VOICE ]',
        'start_bot': '[ ▶ START BOT ]',
        'stop_bot': '[ ■ STOP BOT ]',
        'live_chat_log': '// LIVE CHAT LOG',
        'auto_scroll': 'AUTO-SCROLL',
        'clear_log': '[ CLEAR LOG ]',
        'blacklist_title': '// IGNORED USERS (BLACKLIST)',
        'username_placeholder': 'username',
        'add_user': '[ + ADD ]',
        'remove_selected': '[ - REMOVE SELECTED (DEL) ]',
        'rewards_title': '// TWITCH CHANNEL POINTS',
        'rewards_desc': 'INTEGRATION VIA TWITCH EVENTSUB / PUBSUB\nAUTO-READ CUSTOM REWARDS BY TITLE & ID\n\nSTATUS: [ COMING SOON ]',
        'test_speech_log': 'Testing TTS [{voice}, Vol {vol}%]: "{text}"',
        'test_phrase': 'Audio check. Speech synthesis system active.',
        'connected_as': 'Connected as {nick}',
        'bot_stopped': 'Bot stopped',
        'connecting': 'Connecting to Twitch...',
        'error_credentials': 'Error: Enter OAuth token and Channel name',
        'added_blacklist': 'Added to blacklist: {name}',
        'removed_blacklist': 'Removed from blacklist: {name}',
    }
}

_current_lang = 'en'
_configured_mode = 'auto'


def detect_system_language() -> str:
    try:
        sys_loc = QLocale.system().name().lower()
        if sys_loc.startswith('ru'):
            return 'ru'
    except Exception:
        pass

    if sys.platform == 'win32':
        try:
            import ctypes
            lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
            if (lang_id & 0x3FF) == 0x19:
                return 'ru'
        except Exception:
            pass

    return 'en'


def set_language(mode: str):
    global _current_lang, _configured_mode
    _configured_mode = mode if mode in ('auto', 'ru', 'en') else 'auto'
    if _configured_mode == 'auto':
        _current_lang = detect_system_language()
    else:
        _current_lang = _configured_mode


def get_current_language() -> str:
    return _current_lang


def t(key: str, **kwargs) -> str:
    lang_dict = TRANSLATIONS.get(_current_lang, TRANSLATIONS['en'])
    text = lang_dict.get(key, TRANSLATIONS['en'].get(key, key))
    if kwargs:
        return text.format(**kwargs)
    return text


# ===================================================================
# 3. ДВИЖОК ОЗВУЧКИ WINDOWS SAPI5
# ===================================================================
RATE = 0
PAUSE_MS = 300
TAIL_SEC = 0.3


class BaseTTS:
    def __init__(self):
        self.q = queue.Queue()
        self.voice_name = ''
        self.volume = 25
        self.is_mock = False
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def speak(self, text: str):
        text = text.replace('<', ' меньше чем ').strip()
        if not text:
            return
        if text[-1] not in '.!?…':
            text += '.'
        self.q.put(text)

    def test_voice(self):
        self.speak('Проверка звука. Тестовое сообщение.')

    def list_voices(self):
        raise NotImplementedError

    def _worker(self):
        raise NotImplementedError


class WindowsSapiTTS(BaseTTS):
    def __init__(self):
        super().__init__()
        self.is_mock = False

    def list_voices(self):
        try:
            import pythoncom
            import win32com.client
            pythoncom.CoInitialize()
            sapi = win32com.client.Dispatch('SAPI.SpVoice')
            return [v.GetDescription() for v in sapi.GetVoices()]
        except Exception as e:
            print(f'Error listing Windows SAPI5 voices: {e}')
            return ['Default SAPI5 Voice']

    def _worker(self):
        try:
            import pythoncom
            import win32com.client
            pythoncom.CoInitialize()
            sapi = win32com.client.Dispatch('SAPI.SpVoice')
        except Exception as e:
            print(f'SAPI Init Error: {e}')
            return

        current = None
        while True:
            text = self.q.get()
            try:
                if self.voice_name and self.voice_name != current:
                    for v in sapi.GetVoices():
                        if v.GetDescription() == self.voice_name:
                            sapi.Voice = v
                            current = self.voice_name
                            break
                sapi.Volume = int(self.volume)
                sapi.Rate = RATE
                sapi.Speak(f'<silence msec="{PAUSE_MS}"/>{escape(text)}', 8)
                time.sleep(TAIL_SEC)
            except Exception as e:
                print(f'SAPI TTS speak error: {e}')


class MockTTS(BaseTTS):
    def __init__(self):
        super().__init__()
        self.is_mock = True

    def list_voices(self):
        return [
            'Microsoft Irina Desktop - Russian',
            'Microsoft David Desktop - English (United States)',
            'Microsoft Zira Desktop - English (United States)'
        ]

    def _worker(self):
        while True:
            _ = self.q.get()
            time.sleep(0.05)


_tts_instance = None


def get_tts_engine() -> BaseTTS:
    global _tts_instance
    if _tts_instance is not None:
        return _tts_instance

    if sys.platform == 'win32':
        try:
            import pythoncom
            import win32com.client
            _tts_instance = WindowsSapiTTS()
            return _tts_instance
        except ImportError:
            pass

    _tts_instance = MockTTS()
    return _tts_instance


def list_voices():
    return get_tts_engine().list_voices()


# ===================================================================
# 4. ПОЛЬЗОВАТЕЛЬСКИЙ ИНТЕРФЕЙС (ПИКСЕЛЬНЫЙ ДИЗАЙН)
# ===================================================================
class AppTitleBar(QWidget):
    """Безрамочный заголовок с кнопками управления окном и статусом."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName('titleBar')
        self._drag_pos = None
        self._is_live = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 8, 0)
        layout.setSpacing(10)

        self.title_label = QLabel(t('title'))
        self.title_label.setObjectName('titleLabel')
        layout.addWidget(self.title_label)

        layout.addStretch()

        self.status_badge = QLabel(t('offline'))
        self.status_badge.setObjectName('statusBadgeIdle')
        layout.addWidget(self.status_badge)

        self.min_btn = QPushButton('—')
        self.min_btn.setObjectName('winBtnMin')
        self.min_btn.setCursor(Qt.PointingHandCursor)
        self.min_btn.clicked.connect(self._minimize_window)
        layout.addWidget(self.min_btn)

        self.max_btn = QPushButton('□')
        self.max_btn.setObjectName('winBtnMax')
        self.max_btn.setCursor(Qt.PointingHandCursor)
        self.max_btn.clicked.connect(self._toggle_maximize)
        layout.addWidget(self.max_btn)

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

    def _toggle_maximize(self):
        w = self.window()
        if w:
            if w.isMaximized():
                w.showNormal()
                self.max_btn.setText('□')
            else:
                w.showMaximized()
                self.max_btn.setText('❐')

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._toggle_maximize()
            event.accept()

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
    tab_changed = pyqtSignal(int)

    def __init__(self, tabs, parent=None):
        super().__init__(parent)
        self.buttons = []
        self.current_index = 0

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        for i, text in enumerate(tabs):
            btn = QPushButton(text)
            btn.setProperty('class', 'SegmentBtn')
            btn.setCursor(Qt.PointingHandCursor)
            btn.setProperty('active', 'true' if i == 0 else 'false')
            btn.clicked.connect(lambda _, idx=i: self.set_index(idx))
            layout.addWidget(btn)
            self.buttons.append(btn)

    def set_index(self, index: int):
        if index == self.current_index:
            return
        self.current_index = index
        for i, btn in enumerate(self.buttons):
            is_active = (i == index)
            btn.setProperty('active', 'true' if is_active else 'false')
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self.tab_changed.emit(index)

    def update_texts(self, tabs):
        for i, text in enumerate(tabs):
            if i < len(self.buttons):
                self.buttons[i].setText(text)


class ControlsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setProperty('class', 'PixelCard')

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        self.hdr = QLabel(t('config_controls'))
        self.hdr.setProperty('class', 'CardHeader')
        layout.addWidget(self.hdr)

        self.lang_lbl = QLabel(t('language'))
        layout.addWidget(self.lang_lbl)

        self.lang_box = QComboBox()
        self.lang_box.addItem(f"[ · ] {t('lang_system')}", 'auto')
        self.lang_box.addItem(f"[ RU ] {t('lang_ru')}", 'ru')
        self.lang_box.addItem(f"[ EN ] {t('lang_en')}", 'en')
        layout.addWidget(self.lang_box)

        layout.addSpacing(4)

        self.token_lbl = QLabel(t('oauth_token'))
        layout.addWidget(self.token_lbl)

        self.token_edit = QLineEdit()
        self.token_edit.setEchoMode(QLineEdit.Password)
        self.token_edit.setPlaceholderText(t('token_placeholder'))
        layout.addWidget(self.token_edit)

        self.remember_check = QCheckBox(t('remember_token'))
        layout.addWidget(self.remember_check)

        layout.addSpacing(4)

        self.channel_lbl = QLabel(t('twitch_channel'))
        layout.addWidget(self.channel_lbl)

        self.channel_edit = QLineEdit()
        self.channel_edit.setPlaceholderText(t('channel_placeholder'))
        layout.addWidget(self.channel_edit)

        layout.addSpacing(4)

        self.voice_lbl = QLabel(t('voice_engine'))
        layout.addWidget(self.voice_lbl)

        self.voice_box = QComboBox()
        layout.addWidget(self.voice_box)

        layout.addSpacing(4)

        vol_header = QHBoxLayout()
        self.vol_lbl = QLabel(t('volume'))
        vol_header.addWidget(self.vol_lbl)
        vol_header.addStretch()

        self.vol_val_lbl = QLabel('25%')
        self.vol_val_lbl.setObjectName('volValLabel')
        vol_header.addWidget(self.vol_val_lbl)
        layout.addLayout(vol_header)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(25)
        self.volume_slider.valueChanged.connect(lambda v: self.vol_val_lbl.setText(f'{v}%'))
        layout.addWidget(self.volume_slider)

        self.test_btn = QPushButton(t('test_voice'))
        self.test_btn.setObjectName('testBtn')
        self.test_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.test_btn)

        layout.addStretch()

        self.start_btn = QPushButton(t('start_bot'))
        self.start_btn.setObjectName('startBtn')
        self.start_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.start_btn)

    def update_texts(self, is_running=False):
        self.hdr.setText(t('config_controls'))
        self.lang_lbl.setText(t('language'))

        curr_data = self.lang_box.currentData()
        self.lang_box.blockSignals(True)
        self.lang_box.setItemText(0, f"[ · ] {t('lang_system')}")
        self.lang_box.setItemText(1, f"[ RU ] {t('lang_ru')}")
        self.lang_box.setItemText(2, f"[ EN ] {t('lang_en')}")
        idx = self.lang_box.findData(curr_data)
        if idx >= 0:
            self.lang_box.setCurrentIndex(idx)
        self.lang_box.blockSignals(False)

        self.token_lbl.setText(t('oauth_token'))
        self.token_edit.setPlaceholderText(t('token_placeholder'))
        self.remember_check.setText(t('remember_token'))
        self.channel_lbl.setText(t('twitch_channel'))
        self.channel_edit.setPlaceholderText(t('channel_placeholder'))
        self.voice_lbl.setText(t('voice_engine'))
        self.vol_lbl.setText(t('volume'))
        self.test_btn.setText(t('test_voice'))

        if is_running:
            self.start_btn.setText(t('stop_bot'))
            self.start_btn.setObjectName('stopBtn')
        else:
            self.start_btn.setText(t('start_bot'))
            self.start_btn.setObjectName('startBtn')

        self.start_btn.style().unpolish(self.start_btn)
        self.start_btn.style().polish(self.start_btn)


class LogPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setProperty('class', 'PixelCard')

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        top_layout = QHBoxLayout()
        self.hdr = QLabel(t('live_chat_log'))
        self.hdr.setProperty('class', 'CardHeader')
        top_layout.addWidget(self.hdr)
        top_layout.addStretch()

        self.auto_scroll_check = QCheckBox(t('auto_scroll'))
        self.auto_scroll_check.setChecked(True)
        top_layout.addWidget(self.auto_scroll_check)

        self.clear_btn = QPushButton(t('clear_log'))
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.clicked.connect(self.clear_log)
        top_layout.addWidget(self.clear_btn)

        layout.addLayout(top_layout)

        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

    def append_message(self, message: str):
        now = datetime.now().strftime('%H:%M:%S')
        self.log_text.appendPlainText(f'[{now}] {message}')
        if self.auto_scroll_check.isChecked():
            sb = self.log_text.verticalScrollBar()
            sb.setValue(sb.maximum())

    def clear_log(self):
        self.log_text.clear()

    def update_texts(self):
        self.hdr.setText(t('live_chat_log'))
        self.auto_scroll_check.setText(t('auto_scroll'))
        self.clear_btn.setText(t('clear_log'))


class BlacklistListWidget(QListWidget):
    delete_pressed = pyqtSignal()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.delete_pressed.emit()
            event.accept()
        else:
            super().keyPressEvent(event)


class BlacklistPanel(QWidget):
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

        add_layout = QHBoxLayout()
        add_layout.setSpacing(6)

        self.user_edit = QLineEdit()
        self.user_edit.setPlaceholderText(t('username_placeholder'))
        add_layout.addWidget(self.user_edit)

        self.add_btn = QPushButton(t('add_user'))
        self.add_btn.setCursor(Qt.PointingHandCursor)
        add_layout.addWidget(self.add_btn)

        layout.addLayout(add_layout)

        self.users_list = BlacklistListWidget()
        layout.addWidget(self.users_list)

        self.remove_btn = QPushButton(t('remove_selected'))
        self.remove_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.remove_btn)

    def update_texts(self):
        self.hdr.setText(t('blacklist_title'))
        self.user_edit.setPlaceholderText(t('username_placeholder'))
        self.add_btn.setText(t('add_user'))
        self.remove_btn.setText(t('remove_selected'))


class RewardsPlaceholder(QWidget):
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


# ===================================================================
# 5. TWITCH BOT И ФОНОВЫЙ ПОТОК
# ===================================================================
class TwitchBot(commands.Bot):
    def __init__(self, token, channel, loop, on_log, on_text, blacklist):
        super().__init__(token=token, prefix='!!!',
                         initial_channels=[channel], loop=loop)
        self.on_log = on_log
        self.on_text = on_text
        self.blacklist = blacklist

    async def event_ready(self):
        self.on_log(t('connected_as', nick=self.nick))

    async def event_message(self, message):
        if message.echo or not message.content:
            return
        if message.author.name.lower() in self.blacklist:
            return

        content = message.content
        text = None
        if content.startswith(('!tts ', '!ттс ')):
            text = content[5:]
        elif content.startswith('!'):
            text = content[1:]

        if text and text.strip():
            self.on_log(f'{message.author.name}: {text}')
            self.on_text(text)


class BotThread(QThread):
    log = pyqtSignal(str)
    stopped = pyqtSignal()

    def __init__(self, token, channel, tts, blacklist):
        super().__init__()
        self.token = token.replace('oauth:', '').strip()
        self.channel = channel.strip().lstrip('#')
        self.tts = tts
        self.blacklist = blacklist
        self.loop = None
        self.bot = None

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.bot = TwitchBot(self.token, self.channel, self.loop,
                                 self.log.emit, self.tts.speak, self.blacklist)
            self.loop.run_until_complete(self.bot.start())
        except Exception as e:
            self.log.emit(f'Error: {e}')
        finally:
            self.loop.close()
            self.stopped.emit()

    def stop(self):
        if self.bot and self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self.bot.close(), self.loop)


# ===================================================================
# 6. ГЛАВНОЕ ОКНО ПРИЛОЖЕНИЯ
# ===================================================================
class Window(QMainWindow):
    BORDER_MARGIN = 6

    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint | Qt.WindowMinMaxButtonsHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.resize(900, 570)
        self.setMinimumSize(850, 530)

        self._resize_edge = None
        self._resize_start_pos = None
        self._resize_start_geo = None

        icon_path = resource_path(os.path.join('assets', 'icon.png'))
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.tts = get_tts_engine()
        self.thread = None
        self.blacklist = set()

        self._setup_ui()
        self._populate_voices()
        self.load_settings()
        self.apply_audio()
        self._connect_signals()

        self.setMouseTracking(True)
        self.central_widget.setMouseTracking(True)
        self.central_widget.installEventFilter(self)

        self.size_grip = QSizeGrip(self)
        self.size_grip.setFixedSize(14, 14)

    def _setup_ui(self):
        self.central_widget = QWidget(self)
        self.central_widget.setObjectName('centralWidget')
        self.setCentralWidget(self.central_widget)

        root_layout = QVBoxLayout(self.central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.title_bar = AppTitleBar(self)
        root_layout.addWidget(self.title_bar)

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(12, 12, 12, 12)
        content_layout.setSpacing(12)

        self.controls_panel = ControlsPanel(self)
        self.controls_panel.setFixedWidth(330)
        content_layout.addWidget(self.controls_panel)

        right_container = QWidget(self)
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        self.tabs_switch = SegmentedSwitch([t('tab_log'), t('tab_blacklist'), t('tab_rewards')], self)
        right_layout.addWidget(self.tabs_switch)

        self.stacked_widget = QStackedWidget(self)
        self.log_panel = LogPanel(self)
        self.blacklist_panel = BlacklistPanel(self)
        self.rewards_panel = RewardsPlaceholder(self)

        self.stacked_widget.addWidget(self.log_panel)
        self.stacked_widget.addWidget(self.blacklist_panel)
        self.stacked_widget.addWidget(self.rewards_panel)

        right_layout.addWidget(self.stacked_widget)
        content_layout.addWidget(right_container, stretch=1)

        root_layout.addLayout(content_layout)

    def _populate_voices(self):
        voices = list_voices()
        self.controls_panel.voice_box.clear()
        self.controls_panel.voice_box.addItems(voices)

    def _connect_signals(self):
        self.tabs_switch.tab_changed.connect(self.stacked_widget.setCurrentIndex)
        self.controls_panel.lang_box.currentIndexChanged.connect(self.on_language_changed)
        self.controls_panel.voice_box.currentTextChanged.connect(self.apply_audio)
        self.controls_panel.volume_slider.valueChanged.connect(self.apply_audio)
        self.controls_panel.test_btn.clicked.connect(self.test_speech)
        self.controls_panel.start_btn.clicked.connect(self.toggle_bot)

        self.blacklist_panel.add_btn.clicked.connect(self.add_blacklist)
        self.blacklist_panel.user_edit.returnPressed.connect(self.add_blacklist)
        self.blacklist_panel.remove_btn.clicked.connect(self.remove_blacklist)
        self.blacklist_panel.users_list.delete_pressed.connect(self.remove_blacklist)

        self.del_shortcut = QShortcut(QKeySequence(Qt.Key_Delete), self.blacklist_panel.users_list)
        self.del_shortcut.activated.connect(self.remove_blacklist)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'size_grip'):
            self.size_grip.move(self.width() - self.size_grip.width() - 2,
                                self.height() - self.size_grip.height() - 2)

    def _get_edge_flags(self, pos):
        if self.isMaximized():
            return None, None
        w, h = self.width(), self.height()
        x, y = pos.x(), pos.y()
        m = self.BORDER_MARGIN

        left = x <= m
        right = x >= w - m
        top = y <= m
        bottom = y >= h - m

        if top and left:
            return (Qt.TopEdge | Qt.LeftEdge), Qt.SizeFDiagCursor
        if top and right:
            return (Qt.TopEdge | Qt.RightEdge), Qt.SizeBDiagCursor
        if bottom and left:
            return (Qt.BottomEdge | Qt.LeftEdge), Qt.SizeBDiagCursor
        if bottom and right:
            return (Qt.BottomEdge | Qt.RightEdge), Qt.SizeFDiagCursor
        if left:
            return Qt.LeftEdge, Qt.SizeHorCursor
        if right:
            return Qt.RightEdge, Qt.SizeHorCursor
        if top:
            return Qt.TopEdge, Qt.SizeVerCursor
        if bottom:
            return Qt.BottomEdge, Qt.SizeVerCursor
        return None, None

    def eventFilter(self, obj, event):
        if obj == self.central_widget and not self.isMaximized():
            if event.type() == QEvent.MouseMove:
                pos = self.mapFromGlobal(event.globalPos())
                edge, cursor = self._get_edge_flags(pos)
                if cursor:
                    self.setCursor(cursor)
                else:
                    self.unsetCursor()
            elif event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                pos = self.mapFromGlobal(event.globalPos())
                edge, _ = self._get_edge_flags(pos)
                if edge:
                    handle = self.windowHandle()
                    if handle and hasattr(handle, 'startSystemResize'):
                        handle.startSystemResize(edge)
                        return True
                    self._resize_edge = edge
                    self._resize_start_pos = event.globalPos()
                    self._resize_start_geo = self.geometry()
                    return True
        return super().eventFilter(obj, event)

    def mouseMoveEvent(self, event):
        if self._resize_edge and self._resize_start_geo:
            diff = event.globalPos() - self._resize_start_pos
            geo = QRect(self._resize_start_geo)
            min_w = self.minimumWidth()
            min_h = self.minimumHeight()

            if self._resize_edge & Qt.LeftEdge:
                new_w = max(min_w, geo.width() - diff.x())
                geo.setLeft(geo.right() - new_w)
            if self._resize_edge & Qt.RightEdge:
                new_w = max(min_w, geo.width() + diff.x())
                geo.setWidth(new_w)
            if self._resize_edge & Qt.TopEdge:
                new_h = max(min_h, geo.height() - diff.y())
                geo.setTop(geo.bottom() - new_h)
            if self._resize_edge & Qt.BottomEdge:
                new_h = max(min_h, geo.height() + diff.y())
                geo.setHeight(new_h)

            self.setGeometry(geo)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._resize_edge = None
        self._resize_start_pos = None
        self._resize_start_geo = None
        self.unsetCursor()
        super().mouseReleaseEvent(event)

    def on_language_changed(self, idx):
        mode = self.controls_panel.lang_box.itemData(idx) or 'auto'
        set_language(mode)
        self.update_ui_texts()

    def update_ui_texts(self):
        is_running = bool(self.thread and self.thread.isRunning())
        self.title_bar.update_texts()
        self.controls_panel.update_texts(is_running=is_running)
        self.tabs_switch.update_texts([t('tab_log'), t('tab_blacklist'), t('tab_rewards')])
        self.log_panel.update_texts()
        self.blacklist_panel.update_texts()
        self.rewards_panel.update_texts()

    def apply_audio(self, *_):
        self.tts.voice_name = self.controls_panel.voice_box.currentText()
        self.tts.volume = self.controls_panel.volume_slider.value()

    def test_speech(self):
        self.apply_audio()
        phrase = t('test_phrase')
        self.append_log(t('test_speech_log', voice=self.tts.voice_name, vol=self.tts.volume, text=phrase))
        self.tts.speak(phrase)

    def append_log(self, text):
        self.log_panel.append_message(text)

    def add_blacklist(self):
        name = self.blacklist_panel.user_edit.text().strip().lower()
        if not name:
            return
        self.blacklist.add(name)
        self.blacklist_panel.user_edit.clear()
        self.refresh_blacklist()
        self.append_log(t('added_blacklist', name=name))

    def remove_blacklist(self):
        for item in self.blacklist_panel.users_list.selectedItems():
            name = item.text().lower()
            self.blacklist.discard(name)
            self.append_log(t('removed_blacklist', name=name))
        self.refresh_blacklist()

    def refresh_blacklist(self):
        self.blacklist_panel.users_list.clear()
        for name in sorted(self.blacklist):
            self.blacklist_panel.users_list.addItem(name)

    def toggle_bot(self):
        if self.thread and self.thread.isRunning():
            self.controls_panel.start_btn.setEnabled(False)
            self.thread.stop()
        else:
            token = self.controls_panel.token_edit.text().strip()
            channel = self.controls_panel.channel_edit.text().strip()
            if not token or not channel:
                self.append_log(t('error_credentials'))
                return

            self._set_ui_running_state(True)
            self.append_log(t('connecting'))
            self.thread = BotThread(token, channel, self.tts, self.blacklist)
            self.thread.log.connect(self.append_log)
            self.thread.stopped.connect(self.on_bot_stopped)
            self.thread.start()

    def _set_ui_running_state(self, is_running):
        self.title_bar.set_status(is_running)
        self.controls_panel.token_edit.setEnabled(not is_running)
        self.controls_panel.channel_edit.setEnabled(not is_running)
        self.controls_panel.remember_check.setEnabled(not is_running)
        self.controls_panel.start_btn.setEnabled(True)

        if is_running:
            self.controls_panel.start_btn.setText(t('stop_bot'))
            self.controls_panel.start_btn.setObjectName('stopBtn')
        else:
            self.controls_panel.start_btn.setText(t('start_bot'))
            self.controls_panel.start_btn.setObjectName('startBtn')

        self.controls_panel.start_btn.style().unpolish(self.controls_panel.start_btn)
        self.controls_panel.start_btn.style().polish(self.controls_panel.start_btn)

    def on_bot_stopped(self):
        self.thread = None
        self._set_ui_running_state(False)
        self.append_log(t('bot_stopped'))

    def load_settings(self):
        if not os.path.exists(SETTINGS_PATH):
            return
        try:
            with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
                s = json.load(f)
        except Exception:
            return

        lang_mode = s.get('language', 'auto')
        idx = self.controls_panel.lang_box.findData(lang_mode)
        if idx < 0:
            idx = 0
        self.controls_panel.lang_box.blockSignals(True)
        self.controls_panel.lang_box.setCurrentIndex(idx)
        self.controls_panel.lang_box.blockSignals(False)
        set_language(lang_mode)
        self.update_ui_texts()

        self.controls_panel.channel_edit.setText(s.get('channel', ''))
        token = s.get('token', '')
        self.controls_panel.token_edit.setText(token)
        self.controls_panel.remember_check.setChecked(bool(token))

        vol = s.get('volume', 25)
        self.controls_panel.volume_slider.setValue(vol)
        self.controls_panel.vol_val_lbl.setText(f'{vol}%')

        i = self.controls_panel.voice_box.findText(s.get('voice', ''))
        if i >= 0:
            self.controls_panel.voice_box.setCurrentIndex(i)

        self.blacklist.update(str(n).lower() for n in s.get('blacklist', []))
        self.refresh_blacklist()

    def closeEvent(self, event):
        s = {
            'channel': self.controls_panel.channel_edit.text(),
            'voice': self.controls_panel.voice_box.currentText(),
            'volume': self.controls_panel.volume_slider.value(),
            'token': (self.controls_panel.token_edit.text()
                      if self.controls_panel.remember_check.isChecked() else ''),
            'blacklist': sorted(self.blacklist),
            'language': self.controls_panel.lang_box.currentData() or 'auto',
        }
        try:
            with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
                json.dump(s, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f'Error saving settings: {e}')

        if self.thread and self.thread.isRunning():
            self.thread.stop()
            self.thread.wait()
        event.accept()


def setup_application_fonts():
    font_paths = [
        resource_path(os.path.join('assets', 'fonts', 'Monocraft.ttf')),
    ]
    loaded = []
    for p in font_paths:
        if os.path.exists(p):
            fid = QFontDatabase.addApplicationFont(p)
            fams = QFontDatabase.applicationFontFamilies(fid)
            if fams:
                loaded.extend(fams)

    font_family = 'Monocraft' if 'Monocraft' in loaded else 'monospace'
    font = QFont(font_family, 10)
    font.setStyleHint(QFont.Monospace)
    QApplication.setFont(font)


def main():
    app = QApplication(sys.argv)

    lang_pref = 'auto'
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
                saved = json.load(f)
                lang_pref = saved.get('language', 'auto')
        except Exception:
            pass
    set_language(lang_pref)

    setup_application_fonts()

    qss = load_stylesheet_with_accent()
    if qss:
        app.setStyleSheet(qss)

    w = Window()
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
