import queue
import sys
import threading
import time
from xml.sax.saxutils import escape

RATE = 0                  # от -10 до 10
PAUSE_MS = 300            # тишина перед фразой в мс
TAIL_SEC = 0.3            # ожидание после фразы


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
    """
    Основной движок озвучки Windows через SAPI5 (COM-объект SAPI.SpVoice).
    Работает через библиотеку pywin32 (pythoncom).
    """
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
    """
    Заглушка для сред разработки и анализаторов сборки,
    где COM-библиотека win32com недоступна.
    """
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
            text = self.q.get()
            # Заглушка: обработка в фоновом потоке
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

    # Заглушка при сборке или запуске вне Windows
    _tts_instance = MockTTS()
    return _tts_instance


def list_voices():
    return get_tts_engine().list_voices()
