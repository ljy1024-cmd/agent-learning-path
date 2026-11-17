"""第 1 课：不用任何框架，手写一个 ReAct Agent（本课最重要）。

运行：
    python examples/01_react_from_scratch.py
    python examples/01_react_from_scratch.py "现在几点了"
    python examples/01_react_from_scratch.py "先算 12*(3+4)，再告诉我现在几点"

零密钥可运行：没配 .env 时用内置 MockLLM（按脚本输出）演示完整循环；
配好 .env 后自动换成真实大模型，代码一行都不用改。

记住这个公式：
    Agent = LLM（大脑） + Tools（手脚） + Loop（循环） + Memory（对话历史）
ReAct 的一轮 = Thought -> Action -> Action Input -> Observation -> ... -> Final Answer
"""
from __future__ import annotations

import ast
import datetime
import operator
import re
import sys

from llm import MODEL, get_client, has_key

# ---------------------------------------------------------------- 1. 工具层
# 工具就是普通 Python 函数。框架做的事，本质也只是把函数描述塞进 prompt。

NOTES = {
    "react": "ReAct = Reasoning + Acting，让模型先思考再调用工具，根据工具结果继续思考。",
    "memory": "Agent 的记忆分两种：短期记忆（本次对话的上下文）和长期记忆（向量库/数据库）。",
    "loop": "Agent 循环必须设置最大步数，否则模型可能反复调用同一个工具永远不结束。",
    "tool": "工具描述写得越清楚，模型选错工具的概率越低。参数最好用 JSON Schema 约束。",
}

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def _eval_node(node):
    """只允许数字和四则运算，绝不用 eval（避免任意代码执行）。"""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    raise ValueError(f"不支持的表达式片段: {ast.dump(node)}")


def calculator(expr: str) -> str:
    expr = (expr or "").strip()
    try:
        return str(_eval_node(ast.parse(expr, mode="eval").body))
    except Exception as exc:  # noqa: BLE001 - 教学示例，工具失败也要返回可读结果
        return f"计算失败：{exc}"


def now(_: str = "") -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def search_notes(keyword: str) -> str:
    hits = [v for k, v in NOTES.items() if k in keyword.lower() or keyword.strip() == ""]
    if not hits:
        # 中文关键词到英文 key 的简单映射，方便对照笔记
        mapping = {"反应": "react", "记忆": "memory", "循环": "loop", "工具": "tool"}
        hits = [NOTES[k] for cn, k in mapping.items() if cn in keyword and k in NOTES]
    return " / ".join(hits) if hits else f"本地笔记里没有找到「{keyword}」相关内容"


TOOLS = {
    "calculator": {"desc": "四则运算，输入一个算式，例如 12 * (3 + 4)", "fn": calculator},
    "now": {"desc": "获取当前日期和时间，无需输入", "fn": now},
    "search_notes": {"desc": "查询本地 Agent 学习笔记，输入关键词", "fn": search_notes},
}


def run_tool(name: str, arg: str) -> str:
    """统一的工具执行入口：真实项目里这里还要做权限校验、超时、日志。"""
    if name not in TOOLS:
        return f"错误：不存在工具「{name}」，可用工具有 {list(TOOLS)}"
    try:
        return str(TOOLS[name]["fn"](arg))
    except Exception as exc:  # noqa: BLE001
        return f"工具「{name}」执行出错：{exc}"


# ---------------------------------------------------------------- 2. 大脑层
SYSTEM_PROMPT = """你是一个严格遵循 ReAct 范式的助手。每一轮只能输出下面两种格式之一，不要输出多余内容：

格式一（需要调用工具）：
Thought: <简短说明为什么要调用工具>
Action: <工具名>
Action Input: <传给工具的参数>

格式二（可以回答了）：
Thought: <简短说明>
Final Answer: <最终答案>

可用工具：
{tool_desc}

重要：Action 必须严格使用上面的工具名；一次只调用一个工具。"""


def tool_desc() -> str:
    return "\n".join(f"- {name}: {meta['desc']}" for name, meta in TOOLS.items())


class MockLLM:
    """离线假模型：按预设脚本输出，用来把「循环」看清楚，不消耗一分钱。"""

    def __init__(self, question: str) -> None:
        self.script: list[str] = []
        if any(k in question for k in ("计算", "算一下", "乘以", "等于多少", "*", "+")):
            match = re.search(r"[0-9\s\+\-\*\/\(\)\.]+", question)
            expr = match.group(0).strip() if match else "1 + 1"
            self.script.append(
                f"Thought: 这是计算题，我不心算，交给计算器。\n"
                f"Action: calculator\nAction Input: {expr}"
            )
        if any(k in question for k in ("几点", "时间", "日期")):
            self.script.append("Thought: 需要实时时间，查工具。\nAction: now\nAction Input: ")
        if any(k in question for k in ("记忆", "工具", "循环", "react", "是什么", "原理")):
            self.script.append(
                f"Thought: 先查本地笔记再回答。\nAction: search_notes\nAction Input: {question}"
            )
        if not self.script:
            self.script.append(
                "Thought: 没有合适工具，直接回答。\nFinal Answer: 这个问题我没有相关信息。"
            )

    def __call__(self, prompt: str) -> str:
        observations = re.findall(r"^Observation:\s*(.+)$", prompt, flags=re.M)
        if self.script:
            return self.script.pop(0)
        summary = "；".join(observations) if observations else "（没有工具结果）"
        return f"Thought: 工具已经给出了所需信息。\nFinal Answer: 根据工具结果：{summary}"


class RealLLM:
    """真实模型：把拼好的 prompt 发给 OpenAI 兼容端点。"""

    def __call__(self, prompt: str) -> str:
        response = get_client().chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return (response.choices[0].message.content or "").strip()


def build_prompt(question: str, history: list[tuple[str, str]]) -> str:
    """把「问题 + 历史轨迹」拼成下一次给模型看的上下文 —— 这就是短期记忆。"""
    parts = [SYSTEM_PROMPT.format(tool_desc=tool_desc()), f"\nQuestion: {question}\n"]
    for output, observation in history:
        parts.append(f"\n{output}\nObservation: {observation}\n")
    return "".join(parts)


def parse_output(text: str):
    """把模型文本解析成 (动作, 参数1, 参数2)。"""
    final = re.search(r"Final\s*Answer\s*:\s*(.+)", text, flags=re.I | re.S)
    if final:
        return "final", final.group(1).strip(), ""
    action = re.search(r"Action\s*:\s*(\S+)", text, flags=re.I)
    if not action:
        return "error", "模型没有按格式输出", text
    arg = re.search(r"Action\s*Input\s*:\s*(.*)", text, flags=re.I)
    return "action", action.group(1).strip(), (arg.group(1).strip() if arg else "")


# ---------------------------------------------------------------- 3. 循环层
def agent(question: str, llm, max_steps: int = 6) -> str:
    history: list[tuple[str, str]] = []
    for step in range(1, max_steps + 1):
        prompt = build_prompt(question, history)
        output = llm(prompt)
        print(f"\n{'=' * 62}\n[第 {step} 步] 模型输出\n{'-' * 62}\n{output}")
        kind, first, second = parse_output(output)

        if kind == "final":
            return first
        if kind == "error":
            return f"{first}：{second}"

        observation = run_tool(first, second)
        print(f"{'-' * 62}\n[第 {step} 步] 工具结果 (Observation)\n{observation}")
        history.append((output, observation))  # 写入短期记忆，下一轮模型能看见

    return f"达到最大步数 {max_steps}，仍未得出答案（防止死循环是 Agent 的必修课）。"


def main() -> None:
    questions = (
        [sys.argv[1]]
        if len(sys.argv) > 1
        else [
            "先算 12 * (3 + 4)，再告诉我现在几点",
            "Agent 的记忆是什么",
        ]
    )
    if has_key():
        llm = RealLLM()
        print(f"[模式] 真实模型 {MODEL} —— 观察思考与工具调用轨迹")
    else:
        print("[模式] 离线 MockLLM（未配置 .env）—— 同样能看到完整的 Agent 循环")
        print("       配好 .env 后本文件会自动切换成真实模型，无需改代码。")

    for question in questions:
        print(f"\n\n{'#' * 62}\n# 问题：{question}\n{'#' * 62}")
        answer = agent(question, MockLLM(question) if not has_key() else llm)
        print(f"\n{'=' * 62}\n最终答案：{answer}\n{'=' * 62}")

    print("\n思考题：把 max_steps 改成 1 会怎样？给模型一个不存在的工具名会怎样？")
    print("下一课：02_function_calling.py —— 用结构化的 tools 参数替换手写文本协议。")


if __name__ == "__main__":
    main()
