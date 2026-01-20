import requests
from threading import Thread
from queue import Queue


class STTProcessor:
    """语音转文字处理器"""

    def __init__(self, config):
        self.config = config
        self.url = config.get("url", "")
        self.model = config.get("model", "")
        self.api_key = config.get("api_key", "")

        self.text_queue = Queue()
        self.processing = False

    def transcribe(self, audio_data, callback=None):
        """转录音频为文字"""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        files = {"file": ("audio.mp3", audio_data)}
        payload = {"model": self.model}

        try:
            response = requests.post(
                self.url, data=payload, files=files, headers=headers, timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                text = result.get("text", "")
                print(f"[STT] 转录结果: {text}")

                if callback:
                    callback(text)

                return text
            else:
                print(f"[STT] 错误: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            print(f"[STT] 异常: {e}")
            return None

    def transcribe_async(self, audio_data, callback=None):
        """异步转录音频"""

        def _transcribe():
            self.processing = True
            try:
                text = self.transcribe(audio_data)
                if callback and text:
                    callback(text)
            finally:
                self.processing = False

        thread = Thread(target=_transcribe, daemon=True)
        thread.start()
