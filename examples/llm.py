"""所有示例共用的模型配置。

只要遵循 OpenAI 兼容协议，同一份代码可以切换：
OpenAI 官方 / DeepSeek / 阿里百炼 / 智谱 / 本地 Ollama / vLLM。
配置写在项目根目录的 .env 里（参考 .env.example）。
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
BASE_URL = os.getenv("OPENAI_BASE_URL", "").strip() or None
MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini").strip() or "gpt-4o-mini"


def has_key() -> bool:
    """是否配置了可用的密钥（本地 Ollama 随便填一个非空值即可）。"""
    return bool(API_KEY)


def get_client():
    """构造 OpenAI 兼容客户端；没配置密钥时给出可操作的提示。"""
    if not has_key():
        raise SystemExit(
            "\n[未配置模型]\n"
            "  1. 把 .env.example 复制为 .env\n"
            "  2. 填入 OPENAI_API_KEY / OPENAI_BASE_URL / MODEL_NAME\n"
            "  3. 想先零成本跑通原理，请运行：\n"
            "     python examples/01_react_from_scratch.py\n"
            "     python examples/04_rag_mini.py\n"
        )
    from openai import OpenAI

    return OpenAI(api_key=API_KEY, base_url=BASE_URL, timeout=60)
