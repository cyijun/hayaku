# Hayaku 语音输入法 - 快速开始指南

## 🚀 首次使用

### 1. 安装依赖

```bash
cd hayaku_voice_input
pip install -r requirements.txt
```

### 2. 配置 API 密钥

创建 `.env` 文件（从示例复制）：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API 密钥：

```bash
# 使用你喜欢的编辑器
nano .env
```

填入你的密钥：

```bash
SILICONFLOW_API_KEY=sk-xxxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
```

### 3. 运行应用

```bash
python run.py
```

## 📱 使用界面

启动后会出现两个窗口：

1. **主窗口** - 完整的编辑和润色界面
2. **悬浮窗** - 可拖动的小窗口，显示电平和快速控制

### 基本流程

1. 🎤 点击"开始录音"按钮
2. 🗣️ 对着麦克风说话
3. ⏹️ 等待自动检测语音结束
4. 📝 查看转录结果
5. ✨ 点击"润色"按钮进行AI润色
6. 📋 复制结果到其他应用

## 💡 配置说明

### 获取 API 密钥

**SiliconFlow (STT):**
- 访问: https://siliconflow.cn/
- 注册并获取免费 API Key
- 用于语音转文字功能

**OpenAI (LLM):**
- 访问: https://platform.openai.com/
- 创建 API Key
- 用于文本润色功能
- 或者使用其他 OpenAI 兼容服务（如 DeepSeek）

### 调整音频设置

在配置对话框的"音频设置"标签页可以调整：
- 采样率（默认 16000 Hz）
- 静音检测时间（默认 1.5 秒）
- VAD 帧长等参数

**提示：** 如果录音经常中断，增加"静音限制"时间。

## 🎨 功能特点

- ✅ 实时电平显示
- ✅ 智能语音活动检测
- ✅ 多种预设助手（写作润色、代码优化等）
- ✅ 可编辑的文本区域
- ✅ 自动复制到剪贴板选项（可配置）
- ✅ 前卫暗色主题
- ✅ 可拖动悬浮窗
- ✅ 纯GUI配置（无需编辑配置文件）

## ⚠️ 常见问题

### "录音错误"或"无法访问麦克风"

**解决方案:**
- Linux: `sudo apt-get install libasound-dev portaudio19-dev`
- 检查系统麦克风权限设置
- 确认麦克风设备被正确识别

### "STT错误"或"转录失败"

**解决方案:**
- 检查 `SILICONFLOW_API_KEY` 是否正确
- 确认网络连接正常
- 尝试使用代理或更换网络环境

### "LLM错误"或"润色失败"

**解决方案:**
- 检查 `OPENAI_API_KEY` 是否正确
- 确认 API 额度充足
- 检查 `llm.base_url` 和 `llm.model` 设置

### 界面显示异常

**解决方案:**
- 确保安装了 PyQt5: `pip install PyQt5`
- 检查系统字体支持（需要中文字体）

## 🔧 高级使用

### 使用本地模型

在配置对话框中修改 LLM 设置：

```
Base URL: http://localhost:8000/v1  # vLLM 本地部署
Model: your-local-model-name
```

### 添加自定义助手

1. 点击"⚙️ 配置"按钮
2. 切换到"预设助手"标签页
3. 编辑 YAML 格式的配置
4. 点击"保存"

示例：

```yaml
presets:
  - name: "我的翻译助手"
    system_prompt: "你是一个中英翻译专家，请准确翻译以下内容..."
```

### 环境变量优先级

环境变量优先于配置文件中的值：

```bash
export OPENAI_API_KEY="env_override_key"
python run.py
```

## 📚 更多信息

查看完整文档：[README.md](README.md)

---

**祝使用愉快！** 🎉
