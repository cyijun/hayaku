# Hayaku - 前卫好用的语音输入法

一个基于 PyQt5 的现代化语音输入法，参考 [hachimi](../hachimi) 项目实现，支持语音转文字和AI润色功能。

## ✨ 主要特性

- 🎤 **实时语音识别** - 使用 VAD (语音活动检测) 智能检测语音结束
- 🎚️ **电平显示** - 实时显示麦克风音量电平
- ✨ **AI 润色** - 支持多种预设助手模板，使用 OpenAI 兼容 API 进行文本润色
- 🖥️ **双窗口设计** - 主窗口 + 可拖动的悬浮窗
- ⚙️ **GUI 配置** - 所有配置都可以在图形界面中完成
- 📋 **一键复制** - 支持自动复制到剪贴板
- 🎨 **前卫UI** - 现代化的暗色主题界面

## 📦 安装依赖

### 系统依赖

**Linux:**
```bash
sudo apt-get install libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0
```

**macOS:**
```bash
brew install portaudio
```

**Windows:**
通常通过 pip 自动安装，但可能需要 Visual C++ Build Tools。

### Python 依赖

```bash
pip install -r requirements.txt
```

依赖包括:
- PyQt5 - GUI 框架
- pyaudio - 音频采集
- webrtcvad-wheels - 语音活动检测
- numpy - 音频数据处理
- pydub - 音频格式转换
- openai - OpenAI 兼容 API 客户端
- requests - HTTP 请求
- pyyaml - 配置文件解析

## ⚙️ 配置

### 环境变量

创建 `.env` 文件或设置环境变量:

```bash
export SILICONFLOW_API_KEY="your_siliconflow_key"  # 用于 STT
export OPENAI_API_KEY="your_openai_key"  # 用于 LLM 润色
```

### 配置文件

编辑 `config/default_config.yaml` 或在应用中通过图形界面配置:

```yaml
# STT 配置
stt:
  url: "https://api.siliconflow.cn/v1/audio/transcriptions"
  model: "FunAudioLLM/SenseVoiceSmall"
  api_key: "${SILICONFLOW_API_KEY}"

# LLM 配置
llm:
  api_key: "${OPENAI_API_KEY}"
  base_url: "https://api.openai.com/v1"
  model: "gpt-3.5-turbo"
  temperature: 0.7

# 音频配置
audio:
  channels: 1
  rate: 16000
  chunk: 1280
  vad_frame_ms: 30
  silence_limit_seconds: 1.5
  min_record_seconds: 0.5

# 预设助手
presets:
  - name: "写作润色"
    system_prompt: "你是一个专业的写作助手..."
  - name: "代码优化"
    system_prompt: "你是一个代码优化专家..."
  # 更多预设...
```

## 🚀 使用方法

### 启动应用

```bash
python run.py
```

### 基本操作

1. **录音**
   - 点击"🎤 开始录音"按钮
   - 或点击悬浮窗的"录音"按钮
   - 对话筒说话
   - 系统会自动检测语音结束并停止录音

2. **编辑文本**
   - 听写结果显示在左侧文本框
   - 可以手动编辑

3. **润色文本**
   - 选择助手（写作润色、代码优化等）
   - 点击"✨ 润色"按钮
   - 润色结果显示在右侧文本框

4. **复制**
   - 点击"📋 复制"按钮复制到剪贴板
   - 或启用"自动复制到剪贴板"选项

### 悬浮窗

- 拖动悬浮窗到任意位置
- 实时显示麦克风电平
- 快速开始/停止录音
- 一键复制润色结果

### 配置

点击"⚙️ 配置"按钮打开配置对话框，可以:
- 修改 STT API 设置
- 修改 LLM API 设置
- 调整音频参数（采样率、VAD设置等）
- 启用/禁用自动复制
- 添加/编辑预设助手

## 🏗️ 项目结构

```
hayaku_voice_input/
├── run.py                      # 入口文件
├── requirements.txt             # Python 依赖
├── config/
│   └── default_config.yaml      # 默认配置
├── src/
│   ├── __init__.py
│   ├── config.py                # 配置管理
│   ├── audio_processor.py       # 音频处理 (VAD + 电平检测)
│   ├── stt_processor.py          # 语音转文字
│   ├── llm_processor.py         # LLM 润色
│   ├── main_window.py           # 主窗口
│   ├── floating_window.py       # 悬浮窗
│   └── config_dialog.py         # 配置对话框
└── resources/                   # 资源文件
```

## 🔧 高级功能

### 自定义助手

在配置对话框的"预设助手"页面，可以添加自定义助手:

```yaml
- name: "技术文档"
  system_prompt: "你是一个技术文档撰写专家，请将输入转换为清晰的技术文档格式..."
```

### 使用其他 LLM 服务

在配置中修改 `llm.base_url`，支持任何 OpenAI 兼容的 API:
- OpenAI
- DeepSeek
- Claude (通过兼容接口)
- 本地部署的模型 (如 vLLM)

## 🐛 故障排除

### 音频设备问题
- 确保系统麦克风权限已开启
- 检查是否安装了正确的音频驱动

### STT API 错误
- 检查 API Key 是否正确
- 确认服务可访问（可能需要代理）
- 查看终端日志获取详细错误

### LLM 润色失败
- 检查 LLM API Key
- 确认模型名称正确
- 检查网络连接

## 📝 开发说明

本项目参考了 [hachimi](../hachimi) 的实现:
- 使用 `webrtcvad` 进行语音活动检测
- 使用 `pyaudio` 进行音频采集
- 使用 Pydub 进行音频格式转换 (PCM -> MP3)
- 使用多线程处理音频和API请求，避免UI阻塞

## 📄 License

MIT License

---

**享受 Hayaku 带来的便捷语音输入体验！** 🎉
