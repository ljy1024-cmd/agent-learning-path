"""一键自检：依赖是否齐全、关键 API 是否可用、模型是否已配置。

运行：.venv/Scripts/python.exe check_env.py
"""
from __future__ import annotations

import importlib
import importlib.metadata as md
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# (发行包名, 实际导入名)
PACKAGES = [
    ("openai", "openai"),
    ("python-dotenv", "dotenv"),
    ("pydantic", "pydantic"),
    ("httpx", "httpx"),
    ("rich", "rich"),
    ("tenacity", "tenacity"),
    ("tiktoken", "tiktoken"),
    ("pytest", "pytest"),
    ("langchain", "langchain"),
    ("langchain-openai", "langchain_openai"),
    ("langgraph", "langgraph"),
    ("mcp", "mcp"),
    ("smolagents", "smolagents"),
    ("chromadb", "chromadb"),
    ("rank-bm25", "rank_bm25"),
    ("beautifulsoup4", "bs4"),
    ("ddgs", "ddgs"),
    ("fastapi", "fastapi"),
    ("uvicorn", "uvicorn"),
    ("jupyterlab", "jupyterlab"),
    ("ipykernel", "ipykernel"),
]

APIS = [
    ("openai", "OpenAI"),
    ("langchain.agents", "create_agent"),
    ("langchain_openai", "ChatOpenAI"),
    ("langgraph.graph", "StateGraph"),
    ("langgraph.prebuilt", "ToolNode"),
    ("chromadb", "EphemeralClient"),
    ("mcp.server.mcpserver", "MCPServer"),
]


def main() -> None:
    print("=" * 64)
    print("AI Agent 学习环境自检")
    print("=" * 64)
    failed = []
    for dist, module in PACKAGES:
        try:
            importlib.import_module(module)
            version = md.version(dist)
            print(f"  [OK]   {dist:22s} {version}")
        except Exception as exc:  # noqa: BLE001
            failed.append(dist)
            print(f"  [FAIL] {dist:22s} {type(exc).__name__}: {exc}")

    print("\n关键 API：")
    for module, attr in APIS:
        try:
            obj = importlib.import_module(module)
            status = "OK" if hasattr(obj, attr) else "MISSING"
            print(f"  [{status:7s}] {module}.{attr}")
        except Exception as exc:  # noqa: BLE001
            print(f"  [FAIL   ] {module}: {exc}")

    env_file = ROOT / ".env"
    print("\n模型配置：")
    if not env_file.exists():
        print("  [未配置] 没有找到 .env —— 01 / 04 / 04b / 05 课仍然可以直接跑")
        print("           复制 .env.example 为 .env 后，00 / 02 / 03 课也能跑")
    else:
        from dotenv import dotenv_values

        cfg = dotenv_values(env_file)
        key = (cfg.get("OPENAI_API_KEY") or "").strip()
        print(f"  [已配置] .env 存在，API Key = {'已填写' if key else '空'}")
        print(f"           端点 = {cfg.get('OPENAI_BASE_URL') or 'OpenAI 官方默认'}")
        print(f"           模型 = {cfg.get('MODEL_NAME') or 'gpt-4o-mini'}")

    print("\n" + "=" * 64)
    if failed:
        print(f"有 {len(failed)} 个包未就绪：{', '.join(failed)}")
        print("修复：.venv\\Scripts\\python.exe -m pip install -r requirements.txt")
    else:
        print("全部依赖就绪。建议从这条命令开始：")
        print("  .venv\\Scripts\\python.exe examples\\01_react_from_scratch.py")
    print("=" * 64)


if __name__ == "__main__":
    main()
