from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QDoubleSpinBox,
    QCheckBox,
    QTextEdit,
    QTabWidget,
    QWidget,
    QPushButton,
    QSpinBox,
    QGroupBox,
    QFormLayout,
    QMessageBox,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from config import global_config


class ConfigDialog(QDialog):
    """配置对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_config()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("配置")
        self.setMinimumSize(600, 500)
        self.setModal(True)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # 创建标签页
        tab_widget = QTabWidget()

        # STT配置页面
        stt_widget = self.create_stt_config_widget()
        tab_widget.addTab(stt_widget, "STT (语音转文字)")

        # LLM配置页面
        llm_widget = self.create_llm_config_widget()
        tab_widget.addTab(llm_widget, "LLM (大模型)")

        # 音频配置页面
        audio_widget = self.create_audio_config_widget()
        tab_widget.addTab(audio_widget, "音频设置")

        # 界面配置页面
        ui_widget = self.create_ui_config_widget()
        tab_widget.addTab(ui_widget, "界面设置")

        # 预设助手页面
        presets_widget = self.create_presets_widget()
        tab_widget.addTab(presets_widget, "预设助手")

        layout.addWidget(tab_widget)

        # 按钮
        button_layout = QHBoxLayout()

        save_btn = QPushButton("保存")
        save_btn.setMinimumWidth(100)
        save_btn.clicked.connect(self.save_config)
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        # 设置字体
        font = QFont("Microsoft YaHei", 10)
        self.setFont(font)

    def create_stt_config_widget(self):
        """创建STT配置页面"""
        widget = QWidget()
        layout = QFormLayout()
        widget.setLayout(layout)

        self.stt_url_edit = QLineEdit()
        layout.addRow("STT API URL:", self.stt_url_edit)

        self.stt_model_edit = QLineEdit()
        layout.addRow("STT 模型:", self.stt_model_edit)

        self.stt_api_key_edit = QLineEdit()
        self.stt_api_key_edit.setEchoMode(QLineEdit.Password)
        layout.addRow("STT API Key:", self.stt_api_key_edit)

        return widget

    def create_llm_config_widget(self):
        """创建LLM配置页面"""
        widget = QWidget()
        layout = QFormLayout()
        widget.setLayout(layout)

        self.llm_api_key_edit = QLineEdit()
        self.llm_api_key_edit.setEchoMode(QLineEdit.Password)
        layout.addRow("LLM API Key:", self.llm_api_key_edit)

        self.llm_base_url_edit = QLineEdit()
        layout.addRow("LLM Base URL:", self.llm_base_url_edit)

        self.llm_model_edit = QLineEdit()
        layout.addRow("LLM 模型:", self.llm_model_edit)

        self.llm_temperature_spin = QDoubleSpinBox()
        self.llm_temperature_spin.setRange(0.0, 2.0)
        self.llm_temperature_spin.setSingleStep(0.1)
        layout.addRow("Temperature:", self.llm_temperature_spin)

        return widget

    def create_audio_config_widget(self):
        """创建音频配置页面"""
        widget = QWidget()
        layout = QFormLayout()
        widget.setLayout(layout)

        self.audio_channels_spin = QSpinBox()
        self.audio_channels_spin.setRange(1, 2)
        layout.addRow("声道数:", self.audio_channels_spin)

        self.audio_rate_spin = QSpinBox()
        self.audio_rate_spin.setRange(8000, 48000)
        self.audio_rate_spin.setSingleStep(1000)
        layout.addRow("采样率 (Hz):", self.audio_rate_spin)

        self.audio_chunk_spin = QSpinBox()
        self.audio_chunk_spin.setRange(512, 4096)
        self.audio_chunk_spin.setSingleStep(128)
        layout.addRow("Chunk 大小:", self.audio_chunk_spin)

        self.audio_vad_frame_spin = QSpinBox()
        self.audio_vad_frame_spin.setRange(10, 100)
        layout.addRow("VAD 帧长 (ms):", self.audio_vad_frame_spin)

        self.audio_silence_spin = QDoubleSpinBox()
        self.audio_silence_spin.setRange(0.5, 5.0)
        self.audio_silence_spin.setSingleStep(0.5)
        layout.addRow("静音限制 (秒):", self.audio_silence_spin)

        self.audio_min_record_spin = QDoubleSpinBox()
        self.audio_min_record_spin.setRange(0.1, 2.0)
        self.audio_min_record_spin.setSingleStep(0.1)
        layout.addRow("最小录音 (秒):", self.audio_min_record_spin)

        return widget

    def create_ui_config_widget(self):
        """创建UI配置页面"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        group = QGroupBox("通用设置")
        group_layout = QVBoxLayout()

        self.auto_copy_check = QCheckBox("自动复制到剪贴板")
        group_layout.addWidget(self.auto_copy_check)

        group.setLayout(group_layout)
        layout.addWidget(group)

        layout.addStretch()

        return widget

    def create_presets_widget(self):
        """创建预设助手页面"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        self.presets_text = QTextEdit()
        self.presets_text.setMaximumHeight(400)
        layout.addWidget(QLabel("预设助手配置 (YAML格式):"))
        layout.addWidget(self.presets_text)

        return widget

    def load_config(self):
        """加载配置"""
        # STT
        stt = global_config.stt
        self.stt_url_edit.setText(stt.get("url", ""))
        self.stt_model_edit.setText(stt.get("model", ""))
        self.stt_api_key_edit.setText(stt.get("api_key", ""))

        # LLM
        llm = global_config.llm
        self.llm_api_key_edit.setText(llm.get("api_key", ""))
        self.llm_base_url_edit.setText(llm.get("base_url", ""))
        self.llm_model_edit.setText(llm.get("model", ""))
        self.llm_temperature_spin.setValue(llm.get("temperature", 0.7))

        # 音频
        audio = global_config.audio
        self.audio_channels_spin.setValue(audio.get("channels", 1))
        self.audio_rate_spin.setValue(audio.get("rate", 16000))
        self.audio_chunk_spin.setValue(audio.get("chunk", 1280))
        self.audio_vad_frame_spin.setValue(audio.get("vad_frame_ms", 30))
        self.audio_silence_spin.setValue(audio.get("silence_limit_seconds", 1.5))
        self.audio_min_record_spin.setValue(audio.get("min_record_seconds", 0.5))

        # UI
        ui = global_config.ui
        self.auto_copy_check.setChecked(ui.get("auto_copy_to_clipboard", False))

        # Presets
        import yaml

        presets = global_config.presets
        presets_yaml = yaml.dump(
            {"presets": presets}, allow_unicode=True, sort_keys=False
        )
        self.presets_text.setPlainText(presets_yaml)

    def save_config(self):
        """保存配置"""
        try:
            import yaml

            # STT
            global_config.set("stt.url", self.stt_url_edit.text())
            global_config.set("stt.model.model", self.stt_model_edit.text())
            global_config.set("stt.api_key", self.stt_api_key_edit.text())

            # LLM
            global_config.set("llm.api_key", self.llm_api_key_edit.text())
            global_config.set("llm.base_url", self.llm_base_url_edit.text())
            global_config.set("llm.model.model", self.llm_model_edit.text())
            global_config.set("llm.temperature", self.llm_temperature_spin.value())

            # Audio
            global_config.set("audio.channels", self.audio_channels_spin.value())
            global_config.set("audio.rate", self.audio_rate_spin.value())
            global_config.set("audio.chunk", self.audio_chunk_spin.value())
            global_config.set("audio.vad_frame_ms", self.audio_vad_frame_spin.value())
            global_config.set(
                "audio.silence_limit_seconds", self.audio_silence_spin.value()
            )
            global_config.set(
                "audio.min_record_seconds", self.audio_min_record_spin.value()
            )

            # UI
            global_config.set(
                "ui.auto_copy_to_clipboard", self.auto_copy_check.isChecked()
            )

            # Presets
            presets_data = yaml.safe_load(self.presets_text.toPlainText())
            if presets_data and "presets" in presets_data:
                global_config.config["presets"] = presets_data["presets"]

            # 保存到文件
            global_config.save()

            QMessageBox.information(
                self, "成功", "配置已保存！\n部分设置需要重启应用才能生效。"
            )
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置失败: {str(e)}")
