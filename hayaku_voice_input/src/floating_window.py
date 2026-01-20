from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QProgressBar, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class FloatingWindow(QWidget):
    """悬浮窗 - 显示电平和快速控制"""

    # 自定义信号
    record_clicked = pyqtSignal()
    copy_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        # 设置窗口属性
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(200, 280)

        # 创建主部件
        main_widget = QWidget()
        main_widget.setStyleSheet("""
            QWidget {
                background: rgba(30, 30, 40, 230);
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            QLabel {
                color: white;
                background: transparent;
            }
            QPushButton {
                background: rgba(60, 60, 80, 200);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: rgba(80, 80, 100, 200);
            }
            QPushButton:pressed {
                background: rgba(100, 100, 120, 200);
            }
            QProgressBar {
                background: rgba(50, 50, 60, 200);
                border: none;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(76, 175, 80, 200),
                    stop:0.5 rgba(255, 193, 7, 200),
                    stop:1 rgba(244, 67, 54, 200));
                border-radius: 4px;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        main_widget.setLayout(layout)

        # 标题
        title = QLabel("🎤 Hayaku")
        title.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 电平条
        self.level_bar = QProgressBar()
        self.level_bar.setRange(0, 100)
        self.level_bar.setValue(0)
        self.level_bar.setFixedHeight(20)
        layout.addWidget(self.level_bar)

        # 电平文本
        self.level_label = QLabel("0%")
        self.level_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.level_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.level_label)

        # 录音按钮
        self.record_btn = QPushButton("录音")
        self.record_btn.setFixedHeight(40)
        self.record_btn.clicked.connect(self.on_record_clicked)
        layout.addWidget(self.record_btn)

        # 复制按钮
        self.copy_btn = QPushButton("复制结果")
        self.copy_btn.setFixedHeight(35)
        self.copy_btn.clicked.connect(self.on_copy_clicked)
        layout.addWidget(self.copy_btn)

        # 设置主部件
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(main_widget)
        self.setLayout(main_layout)

    def update_level(self, level):
        """更新电平显示"""
        self.level_bar.setValue(level)
        self.level_label.setText(f"{level}%")

    def set_recording_state(self, recording):
        """设置录音状态"""
        if recording:
            self.record_btn.setText("停止")
            self.record_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(244, 67, 54, 220);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: rgba(200, 50, 50, 220);
                }
            """)
        else:
            self.record_btn.setText("录音")
            self.record_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(60, 60, 80, 200);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: rgba(80, 80, 100, 200);
                }
            """)

    def on_record_clicked(self):
        """录音按钮点击"""
        self.record_clicked.emit()

    def on_copy_clicked(self):
        """复制按钮点击"""
        self.copy_clicked.emit()

    def mousePressEvent(self, event):
        """鼠标按下事件 - 用于拖动"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 用于拖动"""
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
