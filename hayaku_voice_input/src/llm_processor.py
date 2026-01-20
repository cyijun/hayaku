import openai
from threading import Thread


class LLMProcessor:
    """LLM处理器 - 用于润色功能"""

    def __init__(self, config):
        self.config = config
        self.api_key = config.get("api_key", "")
        self.base_url = config.get("base_url", "https://api.openai.com/v1")
        self.model = config.get("model", "gpt-3.5-turbo")
        self.temperature = config.get("temperature", 0.7)

        # 初始化OpenAI客户端
        self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)

        self.system_prompt = ""
        self.processing = False

    def set_system_prompt(self, prompt):
        """设置系统提示"""
        self.system_prompt = prompt

    def process(self, text, callback=None):
        """处理文本（润色）"""
        if not text or not text.strip():
            return None

        try:
            messages = [
                {
                    "role": "system",
                    "content": self.system_prompt
                    or "你是一个有用的助手，请润色和改进用户的输入。",
                },
                {"role": "user", "content": text},
            ]

            response = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=self.temperature
            )

            result = response.choices[0].message.content
            print(f"[LLM] 处理结果: {result}")

            if callback:
                callback(result)

            return result

        except Exception as e:
            print(f"[LLM] 异常: {e}")
            return None

    def process_async(self, text, callback=None):
        """异步处理文本"""

        def _process():
            self.processing = True
            try:
                result = self.process(text, callback)
                return result
            finally:
                self.processing = False

        thread = Thread(target=_process, daemon=True)
        thread.start()
