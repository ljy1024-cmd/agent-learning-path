"""第 2 课：Function Calling（Tool Use）—— 用结构化协议替代手写文本解析。

运行：python examples/02_function_calling.py

对比第 1 课：ReAct 靠正则从文本里抠 Action，模型格式写歪就崩；
Function Calling 让模型直接返回结构化的 tool_calls，工具描述用 JSON Schema 声明。
没配 .env 也会先打印工具描述，让你看清「模型到底收到了什么」。
"""
from __future__ import annotations

import json

from llm import MODEL, get_client, has_key

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "计算一个四则运算表达式，例如 12 * (3 + 4)",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "合法的算术表达式"}
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市当前天气（本示例返回模拟数据）",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string", "description": "城市名，如 北京"}},
                "required": ["city"],
            },
        },
    },
]

WEATHER = {"北京": "晴 18℃", "深圳": "多云 26℃", "上海": "小雨 20℃"}


def calculator(expr: str) -> str:
    """安全版四则运算：只允许数字与运算符，绝不使用 eval。"""
    import ast
    import operator

    ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
    }

    def ev(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.UnaryOp) and type(node.op) in ops:
            return ops[type(node.op)](ev(node.operand))
        if isinstance(node, ast.BinOp) and type(node.op) in ops:
            return ops[type(node.op)](ev(node.left), ev(node.right))
        raise ValueError("不支持的表达式")

    try:
        return str(ev(ast.parse(expr, mode="eval").body))
    except Exception as exc:  # noqa: BLE001
        return f"计算失败：{exc}"


def dispatch(name: str, arguments: dict) -> str:
    if name == "calculator":
        return calculator(arguments.get("expression", ""))
    if name == "get_weather":
        city = arguments.get("city", "")
        return WEATHER.get(city, f"{city}：暂无数据")
    return f"未知工具 {name}"


def main() -> None:
    print("发给模型的工具描述（JSON Schema）：")
    print(json.dumps(TOOLS[0], ensure_ascii=False, indent=2))

    if not has_key():
        print("\n[未配置模型] 上面的结构就是本课重点。配好 .env 后再运行，可看到完整往返：")
        print("  模型决定调用工具 -> 本地执行 -> 把结果回填给模型 -> 模型给出自然语言答案")
        print("  想零成本跑通，用 mock_api_server.py（见 README）。")
        return

    client = get_client()
    messages: list[dict] = [
        {"role": "user", "content": "帮我算一下 12 * (3 + 4)，顺便看看北京天气"}
    ]

    for turn in range(1, 5):
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS, tool_choice="auto"
        )
        msg = response.choices[0].message
        print(f"\n--- 第 {turn} 轮 | finish_reason={response.choices[0].finish_reason} ---")

        if not msg.tool_calls:
            print("最终回答：", msg.content)
            break

        # 必须把 assistant 的 tool_calls 原样放回消息历史，否则模型不认账
        messages.append(
            {
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": call.function.name,
                            "arguments": call.function.arguments,
                        },
                    }
                    for call in msg.tool_calls
                ],
            }
        )

        for call in msg.tool_calls:
            args = json.loads(call.function.arguments or "{}")
            result = dispatch(call.function.name, args)
            print(f"  调用 {call.function.name}({args}) -> {result}")
            messages.append(
                {"role": "tool", "tool_call_id": call.id, "content": result}
            )
    else:
        print("达到轮次上限，停止。")


if __name__ == "__main__":
    main()
