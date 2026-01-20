#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Hayaku - 前卫好用的语音输入法
参考 hachimi 项目实现，使用 PyQt5 构建界面
"""

import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from main_window import main


if __name__ == "__main__":
    main()
