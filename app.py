import asyncio
import json
import os
import sys
from datetime import datetime

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QFontDatabase, QKeySequence, QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QStackedWidget, QShortcut
)
from twitchio.ext import commands

from i18n import t, set_language, get_current_language, get_configured_mode
from theme import load_stylesheet_with_accent
from tts_engine import get_tts_engine, list_voices
from ui_components import (
    AppTitleBar, SegmentedSwitch, ControlsPanel,
    LogPanel, BlacklistPanel, RewardsPlaceholder
)


def resource_path(name):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

SETTINGS_PATH = os.path.join(APP_DIR, 'settings.json')
STYLE_PATH = resource_path('style.qss')


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


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        # Безрамочное окно
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint | Qt.WindowMinMaxButtonsHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.resize(900, 570)
        self.setMinimumSize(850, 530)

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

    def _setup_ui(self):
        self.central_widget = QWidget(self)
        self.central_widget.setObjectName('centralWidget')
        self.setCentralWidget(self.central_widget)

        root_layout = QVBoxLayout(self.central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Кастомный заголовок
        self.title_bar = AppTitleBar(self)
        root_layout.addWidget(self.title_bar)

        # Главная рабочая область (Split View)
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(12, 12, 12, 12)
        content_layout.setSpacing(12)

        # Левая колонка: панель управления
        self.controls_panel = ControlsPanel(self)
        self.controls_panel.setFixedWidth(330)
        content_layout.addWidget(self.controls_panel)

        # Правая колонка: переключатель + область контента
        right_container = QWidget(self)
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        # Сегментированный переключатель с локализованными вкладками
        self.tabs_switch = SegmentedSwitch([t('tab_log'), t('tab_blacklist'), t('tab_rewards')], self)
        right_layout.addWidget(self.tabs_switch)

        # QStackedWidget для вкладок
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
        # Навигация по вкладкам
        self.tabs_switch.tab_changed.connect(self.stacked_widget.setCurrentIndex)

        # Выбор языка интерфейса на левой панели
        self.controls_panel.lang_box.currentIndexChanged.connect(self.on_language_changed)

        # Аудио контролы
        self.controls_panel.voice_box.currentTextChanged.connect(self.apply_audio)
        self.controls_panel.volume_slider.valueChanged.connect(self.apply_audio)

        # Действия
        self.controls_panel.test_btn.clicked.connect(self.test_speech)
        self.controls_panel.start_btn.clicked.connect(self.toggle_bot)

        # Чёрный список (кнопка, Enter, клавиша Delete)
        self.blacklist_panel.add_btn.clicked.connect(self.add_blacklist)
        self.blacklist_panel.user_edit.returnPressed.connect(self.add_blacklist)
        self.blacklist_panel.remove_btn.clicked.connect(self.remove_blacklist)
        self.blacklist_panel.users_list.delete_pressed.connect(self.remove_blacklist)

        self.del_shortcut = QShortcut(QKeySequence(Qt.Key_Delete), self.blacklist_panel.users_list)
        self.del_shortcut.activated.connect(self.remove_blacklist)

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
        ts = datetime.now().strftime('%H:%M:%S')
        self.log_panel.log_view.appendPlainText(f'[{ts}] {text}')
        if self.log_panel.auto_scroll_check.isChecked():
            sb = self.log_panel.log_view.verticalScrollBar()
            sb.setValue(sb.maximum())

    def add_blacklist(self):
        name = self.blacklist_panel.user_edit.text().strip().lstrip('@').lower()
        self.blacklist_panel.user_edit.clear()
        if not name or name in self.blacklist:
            return
        self.blacklist.add(name)
        self.refresh_blacklist()
        self.append_log(t('added_blacklist', name=name))

    def remove_blacklist(self):
        items = self.blacklist_panel.users_list.selectedItems()
        if not items:
            cur = self.blacklist_panel.users_list.currentItem()
            if cur:
                items = [cur]
        if not items:
            return

        for item in items:
            name = item.text()
            self.blacklist.discard(name)
            self.append_log(t('removed_blacklist', name=name))
        self.refresh_blacklist()

    def refresh_blacklist(self):
        self.blacklist_panel.users_list.clear()
        self.blacklist_panel.users_list.addItems(sorted(self.blacklist))

    def toggle_bot(self):
        if self.thread and self.thread.isRunning():
            self.controls_panel.start_btn.setEnabled(False)
            self.thread.stop()
            return

        token = self.controls_panel.token_edit.text().strip()
        channel = self.controls_panel.channel_edit.text().strip()
        if not token or not channel:
            self.append_log(t('error_credentials'))
            self.tabs_switch.set_current_index(0)
            return

        self.thread = BotThread(token, channel, self.tts, self.blacklist)
        self.thread.log.connect(self.append_log)
        self.thread.stopped.connect(self.on_stopped)
        self.thread.start()

        self._set_ui_running_state(True)
        self.append_log(t('connecting'))

    def _set_ui_running_state(self, running: bool):
        btn = self.controls_panel.start_btn
        if running:
            self.title_bar.set_status(True, t('live'))
            btn.setText(t('stop_bot'))
            btn.setObjectName('stopBtn')
        else:
            self.title_bar.set_status(False, t('offline'))
            btn.setText(t('start_bot'))
            btn.setObjectName('startBtn')
            btn.setEnabled(True)

        btn.style().unpolish(btn)
        btn.style().polish(btn)

    def on_stopped(self):
        self._set_ui_running_state(False)
        self.append_log(t('bot_stopped'))

    def load_settings(self):
        if not os.path.exists(SETTINGS_PATH):
            return
        try:
            with open(SETTINGS_PATH, encoding='utf-8') as f:
                s = json.load(f)
        except Exception:
            return

        # Язык
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
            self.thread.wait(3000)
        event.accept()


def setup_application_fonts():
    font_paths = [
        resource_path(os.path.join('assets', 'fonts', 'Monocraft.ttf')),
        resource_path(os.path.join('assets', 'fonts', 'Silkscreen-Regular.ttf')),
    ]
    loaded = []
    for p in font_paths:
        if os.path.exists(p):
            fid = QFontDatabase.addApplicationFont(p)
            fams = QFontDatabase.applicationFontFamilies(fid)
            if fams:
                loaded.extend(fams)

    font_family = 'Monocraft' if 'Monocraft' in loaded else ('Silkscreen' if 'Silkscreen' in loaded else 'monospace')
    font = QFont(font_family, 10)
    font.setStyleHint(QFont.Monospace)
    QApplication.setFont(font)


def main():
    app = QApplication(sys.argv)

    # Инициализация языка: берем сохраненный или системный авто
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

    # Загрузка QSS с адаптацией под системный акцентный цвет
    qss = load_stylesheet_with_accent(STYLE_PATH)
    if qss:
        app.setStyleSheet(qss)

    w = Window()
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
