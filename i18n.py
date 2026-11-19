import sys
from PyQt5.QtCore import QLocale

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
    """
    Определяет язык системы:
    1. Системная локаль Qt QLocale.system().name()
    2. Windows API GetUserDefaultUILanguage через ctypes
    """
    # 1. Проверяем системную локаль Qt
    try:
        sys_loc = QLocale.system().name().lower()
        if sys_loc.startswith('ru'):
            return 'ru'
    except Exception:
        pass

    # 2. Проверяем нативный Windows API
    if sys.platform == 'win32':
        try:
            import ctypes
            lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
            # 0x0419 = Russian (1049)
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


def get_configured_mode() -> str:
    return _configured_mode


def t(key: str, **kwargs) -> str:
    lang_dict = TRANSLATIONS.get(_current_lang, TRANSLATIONS['en'])
    text = lang_dict.get(key, TRANSLATIONS['en'].get(key, key))
    if kwargs:
        return text.format(**kwargs)
    return text
