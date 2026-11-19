import os
import sys
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QApplication

DEFAULT_ACCENT = "#D71920"  # Фирменный пиксельный красный по умолчанию


def get_system_accent_color(default: str = DEFAULT_ACCENT) -> str:
    """
    Получает системный акцентный цвет Windows из реестра Desktop Window Manager (DWM):
    HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\DWM
      - AccentColor: ABGR DWORD (Windows 10/11)
      - ColorizationColor: ARGB DWORD (Fallback для Windows 8/10)
    Если значение недоступно или запуск вне Windows, возвращается default.
    """
    if sys.platform == 'win32':
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\DWM")
            try:
                # В Windows 10/11 AccentColor хранится в формате ABGR
                val, _ = winreg.QueryValueEx(key, "AccentColor")
                r = val & 0xFF
                g = (val >> 8) & 0xFF
                b = (val >> 16) & 0xFF
                return f"#{r:02x}{g:02x}{b:02x}"
            except FileNotFoundError:
                # ColorizationColor хранится в формате ARGB
                val, _ = winreg.QueryValueEx(key, "ColorizationColor")
                r = (val >> 16) & 0xFF
                g = (val >> 8) & 0xFF
                b = val & 0xFF
                return f"#{r:02x}{g:02x}{b:02x}"
            finally:
                winreg.CloseKey(key)
        except Exception:
            pass

    # Fallback из палитры Qt (если доступно)
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
    """Генерирует более светлый оттенок акцентного цвета для hover-состояний."""
    c = QColor(hex_color)
    if c.isValid():
        return c.lighter(120).name()
    return hex_color


def load_stylesheet_with_accent(style_path: str, accent_color: str = None) -> str:
    """
    Загружает QSS и подставляет в него актуальный акцентный цвет.
    Заменяет как плейсхолдер @ACCENT@, так и дефолтные упоминания красного (#D71920).
    """
    if not os.path.exists(style_path):
        return ""

    if not accent_color:
        accent_color = get_system_accent_color()

    hover_color = get_accent_hover(accent_color)

    with open(style_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Подставляем акцентные цвета в шаблон QSS
    content = content.replace('@ACCENT@', accent_color)
    content = content.replace('@ACCENT_HOVER@', hover_color)
    content = content.replace('#D71920', accent_color)
    content = content.replace('#FF2A30', hover_color)
    content = content.replace('#FF2830', hover_color)

    return content
