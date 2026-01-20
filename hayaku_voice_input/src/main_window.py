import sys
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
    QComboBox,
    QSplitter,
    QFrame,
    QApplication,
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QTextCursor

from config import global_config
from audio_processor import AudioProcessor
from stt_processor import STTProcessor
from llm_processor import LLMProcessor
from floating_window import FloatingWindow
from config_dialog import ConfigDialog


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.init_processors()  # 先初始化处理器
        self.init_ui()
        self.load_presets()  # 加载预设助手（需要 llm_processor 存在）
        self.init_floating_window()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("Hayaku 语音输入法")
        self.setGeometry(100, 100, 900, 700)

        # 设置字体
        font = QFont("Microsoft YaHei", 10)

        # 主部件
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # 顶部工具栏
        toolbar = QFrame()
        toolbar.setFrameShape(QFrame.StyledPanel)
        toolbar_layout = QHBoxLayout()
        toolbar.setLayout(toolbar_layout)

        # 助手选择
        toolbar_layout.addWidget(QLabel("选择助手:"))
        self.assistant_combo = QComboBox()
        self.assistant_combo.setFont(font)
        toolbar_layout.addWidget(self.assistant_combo)

        # 配置按钮
        config_btn = QPushButton("⚙️ 配置")
        config_btn.setFont(font)
        config_btn.clicked.connect(self.show_config_dialog)
        toolbar_layout.addWidget(config_btn)

        toolbar_layout.addStretch()
        main_layout.addWidget(toolbar)

        # 电平显示
        self.level_label = QLabel("麦克风电平: 0%")
        self.level_label.setFont(font)
        self.level_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.level_label)

        # 分割器 - 左右分栏
        splitter = QSplitter(Qt.Horizontal)

        # 左侧 - 原文文本框
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)

        left_layout.addWidget(QLabel("听写结果 (可编辑):"))
        self.input_text = QTextEdit()
        self.input_text.setFont(QFont("Microsoft YaHei", 11))
        left_layout.addWidget(self.input_text)

        # 操作按钮
        button_layout = QHBoxLayout()

        self.record_btn = QPushButton("🎤 开始录音")
        self.record_btn.setFont(font)
        self.record_btn.setMinimumHeight(40)
        self.record_btn.clicked.connect(self.toggle_recording)
        button_layout.addWidget(self.record_btn)

        self.copy_input_btn = QPushButton("📋 复制原文")
        self.copy_input_btn.setFont(font)
        self.copy_input_btn.clicked.connect(self.copy_input_text)
        button_layout.addWidget(self.copy_input_btn)

        left_layout.addLayout(button_layout)
        splitter.addWidget(left_widget)

        # 右侧 - 润色结果文本框
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)

        right_layout.addWidget(QLabel("润色助手输出:"))
        self.output_text = QTextEdit()
        self.output_text.setFont(QFont("Microsoft YaHei", 11))
        self.output_text.setReadOnly(False)
        right_layout.addWidget(self.output_text)

        # 润色按钮
        polish_button_layout = QHBoxLayout()

        self.polish_btn = QPushButton("✨ 润色")
        self.polish_btn.setFont(font)
        self.polish_btn.setMinimumHeight(40)
        self.polish_btn.clicked.connect(self.polish_text)
        polish_button_layout.addWidget(self.polish_btn)

        self.copy_output_btn = QPushButton("📋 复制润色结果")
        self.copy_output_btn.setFont(font)
        self.copy_output_btn.clicked.connect(self.copy_output_text)
        polish_button_layout.addWidget(self.copy_output_btn)

        right_layout.addLayout(polish_button_layout)
        splitter.addWidget(right_widget)

        # 设置分割比例
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)

        # 状态栏
        self.status_label = QLabel("就绪")
        self.statusBar().addWidget(self.status_label)

        # 自动复制选项
        self.auto_copy = global_config.ui.get("auto_copy_to_clipboard", False)

    def init_processors(self):
        """初始化处理器"""
        # 音频处理器
        self.audio_processor = AudioProcessor(global_config.audio)
        self.audio_processor.start_stream()
        self.audio_processor.set_level_callback(self.update_level)
        self.audio_processor.start_level_monitoring()

        # STT处理器
        self.stt_processor = STTProcessor(global_config.stt)

        # LLM处理器
        self.llm_processor = LLMProcessor(global_config.llm)

        # 状态
        self.is_recording = False

    def init_floating_window(self):
        """初始化悬浮窗"""
        self.floating_window = FloatingWindow()
        self.floating_window.record_clicked.connect(self.toggle_recording)
        self.floating_window.copy_clicked.connect(self.copy_output_text)

        # 从配置加载位置
        pos = global_config.ui.get("floating_window_position", {})
        if pos:
            self.floating_window.move(pos.get("x", 100), pos.get("y", 100))

        self.floating_window.show()

    def load_presets(self):
        """加载预设助手"""
        presets = global_config.presets
        self.assistant_combo.clear()

        for preset in presets:
            self.assistant_combo.addItem(preset["name"], preset["system_prompt"])

        # 添加自定义选项
        self.assistant_combo.addItem("自定义系统提示", "")

        # 默认选择第一个
        if self.assistant_combo.count() > 0:
            self.assistant_combo.setCurrentIndex(0)
            self.llm_processor.set_system_prompt(self.assistant_combo.currentData())

        # 连接信号
        self.assistant_combo.currentIndexChanged.connect(self.on_assistant_changed)

    def on_assistant_changed(self, index):
        """助手改变时更新系统提示"""
        if index >= 0:
            system_prompt = self.assistant_combo.itemData(index)
            self.llm_processor.set_system_prompt(system_prompt)
            self.status_label.setText(
                f"已选择助手: {self.assistant_combo.itemText(index)}"
            )

    def update_level(self, level):
        """更新电平显示"""
        self.level_label.setText(f"麦克风电平: {level}%")
        self.floating_window.update_level(level)

    def toggle_recording(self):
        """切换录音状态"""
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        """开始录音"""
        self.is_recording = True
        self.record_btn.setText("⏹️ 停止录音")
        self.floating_window.set_recording_state(True)
        self.status_label.setText("正在录音...")
        self.input_text.clear()

        # 在后台线程中录音
        from threading import Thread

        thread = Thread(target=self._record_thread, daemon=True)
        thread.start()

    def _record_thread(self):
        """录音线程"""
        try:
            self.audio_processor.start_recording()
            audio_data = self.audio_processor.get_recorded_audio()

            if audio_data:
                # 转录
                self.status_label.setText("正在转录...")
                text = self.stt_processor.transcribe(audio_data)

                if text:
                    # 在主线程中更新UI
                    QTimer.singleShot(0, lambda: self.input_text.setText(text))

                    # 自动复制
                    if self.auto_copy:
                        QApplication.clipboard().setText(text)
                        QTimer.singleShot(
                            0,
                            lambda: self.status_label.setText(
                                "转录完成，已复制到剪贴板"
                            ),
                        )
                    else:
                        QTimer.singleShot(
                            0, lambda: self.status_label.setText("转录完成")
                        )

        except Exception as e:
            print(f"录音错误: {e}")
            QTimer.singleShot(
                0, lambda: self.status_label.setText(f"录音错误: {str(e)}")
            )

        finally:
            self.is_recording = False
            QTimer.singleShot(0, (lambda: self.record_btn.setText("🎤 开始录音")))
            QTimer.singleShot(
                0, (lambda: self.floating_window.set_recording_state(False))
            )

    def stop_recording(self):
        """停止录音"""
        if self.is_recording:
            self.audio_processor.stop_recording()
            self.status_label.setText("正在停止录音...")

    def polish_text(self):
        """润色文本"""
        text = self.input_text.toPlainText()

        if not text.strip():
            self.status_label.setText("请先输入或录音")
            return

        self.status_label.setText("正在润色...")

        # 异步处理
        self.llm_processor.process_async(text, callback=self.on_polish_complete)

    def on_polish_complete(self, result):
        """润色完成回调"""
        if result:
            self.output_text.setText(result)

            # 自动复制
            if self.auto_copy:
                QApplication.clipboard().setText(result)
                self.status_label.setText("润色完成，已复制到剪贴板")
            else:
                self.status_label.setText("润色完成")
        else:
            self.status_label.setText("润色失败")

    def copy_input_text(self):
        """复制原文"""
        text = self.input_text.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self.status_label.setText("原文已复制到剪贴板")

    def copy_output_text(self):
        """复制润色结果"""
        text = self.output_text.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self.status_label.setText("润色结果已复制到剪贴板")

    def show_config_dialog(self):
        """显示配置对话框"""
        dialog = ConfigDialog(self)
        if dialog.exec_() == ConfigDialog.Accepted:
            # 重新加载配置
            global_config._load_config()
            self.status_label.setText("配置已更新")

    def closeEvent(self, event):
        """关闭事件"""
        # 保存悬浮窗位置
        pos = self.floating_window.pos()
        global_config.set("ui.floating_window_position.x", pos.x())
        global_config.set("ui.floating_window_position.y", pos.y())
        global_config.save()

        # 停止处理器
        self.audio_processor.stop_level_monitoring()
        self.audio_processor.stop_stream()

        # 关闭悬浮窗
        self.floating_window.close()

        event.accept()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
