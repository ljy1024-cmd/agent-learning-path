"""把项目里的文档和代码打包成 library.js，供 index.html 的「资料库」离线阅读。

用法（在 agent-lab 根目录）：
    python build_library.py

改动 README / LEARNING_PATH / examples / notebooks 之后重跑一次即可同步，
index.html 不需要改。生成的 library.js 是纯数据，用 <script src> 加载，
所以双击 file:// 打开网页也能读到内容（不受浏览器本地文件跨域限制）。
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "library.js"
MAX_CHARS = 60000

GROUPS: list[tuple[str, list[str]]] = [
    (
        "入门与环境",
        [
            "BEGINNER_GUIDE.md",
            "README.md",
            "LEARNING_PATH.md",
            "check_env.py",
            "requirements.txt",
            "requirements-heavy.txt",
            ".env.example",
        ],
    ),
    ("课程代码", sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "examples").glob("*.py"))),
    ("面板源码", ["index.html", "app-library.js", "beginner.js", "build_library.py"]),
    ("Notebook", sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "notebooks").glob("*.ipynb"))),
    ("日志", ["install.log"]),
]

STAGE_BY_PREFIX = {"00": 0, "01": 2, "02": 3, "03": 4, "04": 5, "04b": 5, "05": 6}
STAGE_BY_FILE = {
    "README.md": None,
    "LEARNING_PATH.md": None,
    "check_env.py": 0,
    "requirements.txt": 0,
    "requirements-heavy.txt": 5,
    ".env.example": 1,
    "examples/llm.py": 0,
    "examples/rag_utils.py": 5,
    "examples/mock_api_server.py": 3,
}
LANG_BY_SUFFIX = {
    ".py": "python", ".md": "markdown", ".ipynb": "json",
    ".txt": "text", ".log": "text", ".example": "ini",
    ".html": "html", ".js": "javascript",
}

LINKS = [
    {"title": "LangGraph / LangChain 文档", "url": "https://docs.langchain.com/", "note": "图式编排、状态、checkpointer"},
    {"title": "MCP 官方站", "url": "https://modelcontextprotocol.io/", "note": "工具协议规范与 SDK"},
    {"title": "OpenAI API 文档", "url": "https://platform.openai.com/docs", "note": "chat completions 与 tool calling"},
    {"title": "ChromaDB 文档", "url": "https://docs.trychroma.com/", "note": "向量库与检索"},
    {"title": "Ollama 文档", "url": "https://ollama.com/docs", "note": "本地模型运行"},
    {"title": "arXiv 检索：ReAct 论文", "url": "https://arxiv.org/search/?query=ReAct+Synergizing+Reasoning+Acting", "note": "经典论文，按标题检索"},
]


def stage_for(rel: str):
    if rel in STAGE_BY_FILE:
        return STAGE_BY_FILE[rel]
    if rel.startswith("examples/"):
        stem = rel.split("/")[-1]
        match = re.match(r"^(\d+b?)", stem)
        if match:
            return STAGE_BY_PREFIX.get(match.group(1))
    return None


def read_text(rel: str) -> str | None:
    path = ROOT / rel
    if not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="replace")
    if rel.endswith(".log"):
        lines = text.splitlines()
        if len(lines) > 60:
            text = "\n".join(lines[:60]) + f"\n\n... [日志共 {len(lines)} 行，这里只收录前 60 行] ..."
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS] + "\n\n... [内容过长，已截断] ..."
    return text


def main() -> None:
    files = []
    for group, paths in GROUPS:
        for rel in paths:
            text = read_text(rel)
            if text is None:
                continue
            files.append(
                {
                    "path": rel,
                    "name": Path(rel).name,
                    "group": group,
                    "stage": stage_for(rel),
                    "size": len(text.encode("utf-8")),
                    "lines": text.count("\n") + 1,
                    "lang": LANG_BY_SUFFIX.get(Path(rel).suffix, "text"),
                    "content": text,
                }
            )

    payload = {
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "root": str(ROOT).replace("\\", "/"),
        "files": files,
        "links": LINKS,
    }
    # 防止内容里出现 </script> 提前闭合脚本标签
    js = "window.LIBRARY = " + json.dumps(payload, ensure_ascii=False).replace("</", "<\\/") + ";\n"
    OUT.write_text(js, encoding="utf-8")

    print(f"已生成 {OUT.name}  ({OUT.stat().st_size:,} 字节)")
    print(f"收录 {len(files)} 个文件，共 {sum(f['lines'] for f in files):,} 行")
    for group, _ in GROUPS:
        subset = [f for f in files if f["group"] == group]
        print(f"  {group:12s} {len(subset):2d} 个")
    print("改动文档或代码后，重新运行本脚本即可同步到网页。")


if __name__ == "__main__":
    main()
