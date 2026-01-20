import io
import numpy as np
import pyaudio
import webrtcvad
from pydub import AudioSegment
from threading import Thread, Event
from queue import Queue
import time


class AudioProcessor:
    """音频处理类 - 实现VAD和电平检测"""

    def __init__(self, config):
        self.config = config

        # 音频参数
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = config.get("channels", 1)
        self.RATE = config.get("rate", 16000)
        self.CHUNK = config.get("chunk", 1280)
        self.VAD_FRAME_MS = config.get("vad_frame_ms", 30)
        self.VAD_FRAME_SAMPLES = int(self.RATE * self.VAD_FRAME_MS / 1000)

        # VAD阈值
        self.SILENCE_LIMIT_SECONDS = config.get("silence_limit_seconds", 1.5)
        self.MIN_RECORD_SECONDS = config.get("min_record_seconds", 0.5)

        # 初始化VAD
        self.vad = webrtcvad.Vad()
        self.vad.set_mode(3)  # 0-3, 3最激进(强降噪但可能切断语音)

        # PyAudio
        self.pa = pyaudio.PyAudio()
        self.stream = None

        # 事件和队列
        self.recording_event = Event()
        self.audio_queue = Queue()
        self.level_callback = None  # 电平回调函数

        # 电平监测线程
        self.level_thread = None
        self.level_running = False

    def start_stream(self):
        """启动音频流"""
        self.stream = self.pa.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
        )

    def stop_stream(self):
        """停止音频流"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

    def calculate_level(self, audio_data):
        """计算音频电平 (0-100)"""
        audio_np = np.frombuffer(audio_data, dtype=np.int16)
        rms = np.sqrt(np.mean(audio_np**2))
        max_level = 32767.0
        level = min(100, int((rms / max_level) * 100 * 10))  # 放大10倍以便显示
        return level

    def start_level_monitoring(self):
        """启动电平监测线程"""
        self.level_running = True
        self.level_thread = Thread(target=self._monitor_level, daemon=True)
        self.level_thread.start()

    def stop_level_monitoring(self):
        """停止电平监测"""
        self.level_running = False
        if self.level_thread:
            self.level_thread.join(timeout=1)
            self.level_thread = None

    def _monitor_level(self):
        """电平监测线程"""
        if not self.stream:
            return

        try:
            while self.level_running:
                data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                level = self.calculate_level(data)

                # 通过回调发送电平信号
                if self.level_callback:
                    self.level_callback(level)

        except Exception as e:
            print(f"电平监测错误: {e}")

    def start_recording(self):
        """开始录音"""
        if not self.stream:
            self.start_stream()

        print(">>> 开始录音...")
        frames = []
        silence_chunks = 0
        max_silence_chunks = int(self.SILENCE_LIMIT_SECONDS * 1000 / self.VAD_FRAME_MS)

        recording = True

        while recording and not self.recording_event.is_set():
            # 读取VAD帧
            data = self.stream.read(self.VAD_FRAME_SAMPLES, exception_on_overflow=False)
            frames.append(data)

            # VAD检测
            is_speech = self.vad.is_speech(data, self.RATE)

            if is_speech:
                silence_chunks = 0  # 重置静音计数
            else:
                silence_chunks += 1

            # 检查是否应该结束录音
            current_duration = (len(frames) * self.VAD_FRAME_MS) / 1000
            if (
                silence_chunks > max_silence_chunks
                and current_duration > self.MIN_RECORD_SECONDS
            ):
                print(">>> 检测到语音结束")
                recording = False

        # 合并音频数据
        audio_data = b"".join(frames)

        # 转换为MP3格式
        mp3_data = self.pcm_to_mp3(audio_data)

        # 放入队列
        self.audio_queue.put(mp3_data)

        print(">>> 录音完成")

    def stop_recording(self):
        """停止录音"""
        self.recording_event.set()
        time.sleep(0.1)  # 等待录音线程结束
        self.recording_event.clear()

    def pcm_to_mp3(self, audio_data):
        """将PCM数据转换为MP3"""
        audio_segment = AudioSegment(
            data=audio_data,
            sample_width=self.pa.get_sample_size(self.FORMAT),
            frame_rate=self.RATE,
            channels=self.CHANNELS,
        )
        mp3_buffer = io.BytesIO()
        audio_segment.export(mp3_buffer, format="mp3")
        return mp3_buffer.getvalue()

    def get_recorded_audio(self, timeout=5.0):
        """获取录制的音频（带超时）"""
        try:
            return self.audio_queue.get(timeout=timeout)
        except:
            return None

    def set_level_callback(self, callback):
        """设置电平回调函数"""
        self.level_callback = callback

    def __del__(self):
        """析构函数"""
        self.stop_level_monitoring()
        self.stop_stream()
        if hasattr(self, "pa"):
            self.pa.terminate()
