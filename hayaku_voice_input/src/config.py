import os
import yaml
import re
from pathlib import Path


class Config:
    """配置管理类"""

    def __init__(self, config_path=None):
        if config_path is None:
            # 默认配置文件路径
            base_dir = Path(__file__).parent.parent
            config_path = base_dir / "config" / "default_config.yaml"

        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self):
        """加载配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        # 解析环境变量
        config = self._resolve_env_vars(config)
        return config

    def _resolve_env_vars(self, config):
        """递归解析配置中的环境变量"""
        if isinstance(config, dict):
            return {k: self._resolve_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._resolve_env_vars(item) for item in config]
        elif isinstance(config, str):
            # 匹配 ${VAR_NAME:default_value} 或 ${VAR_NAME}
            pattern = r"\$\{([^:}]+)(?::([^}]*))?\}"
            matches = re.findall(pattern, config)

            for match in matches:
                var_name = match[0]
                default_value = match[1] if match[1] else ""
                env_value = os.environ.get(var_name, default_value)
                # 替换第一个匹配项
                config = re.sub(pattern, env_value, config, count=1)

            return config
        else:
            return config

    def save(self, config=None):
        """保存配置到文件"""
        if config is not None:
            self.config = config

        # 创建备份
        if self.config_path.exists():
            backup_path = self.config_path.with_suffix(".yaml.bak")
            import shutil

            shutil.copy2(self.config_path, backup_path)

        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(self.config, f, allow_unicode=True, sort_keys=False)

    def get(self, key_path, default=None):
        """获取配置值，支持点号分隔的路径，如 'stt.url'"""
        keys = key_path.split(".")
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path, value):
        """设置配置值，支持点号分隔的路径"""
        keys = key_path.split(".")
        config = self.config

        # 导航到倒数第二层
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        # 设置最后一层
        config[keys[-1]] = value

    @property
    def stt(self):
        return self.config.get("stt", {})

    @property
    def llm(self):
        return self.config.get("llm", {})

    @property
    def audio(self):
        return self.config.get("audio", {})

    @property
    def ui(self):
        return self.config.get("ui", {})

    @property
    def presets(self):
        return self.config.get("presets", [])


# 全局配置实例
global_config = Config()
