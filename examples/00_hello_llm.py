"""第 0 课：最小的一次大模型调用。

运行：python examples/00_hello_llm.py
目的：先确认「密钥 / 端点 / 模型名」三件套配置正确，再往下学 Agent。
"""
from llm import BASE_URL, MODEL, get_client


def main() -> None:
    client = get_client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "你是一位耐心的 AI Agent 导师，回答简洁。"},
            {"role": "user", "content": "用一句话说明 LLM 和 Agent 的区别。"},
        ],
        temperature=0.3,
    )
    print(f"端点    : {BASE_URL or 'OpenAI 官方默认'}")
    print(f"模型    : {MODEL}")
    print(f"回复    : {response.choices[0].message.content}")
    print(f"token   : {response.usage}")
    print("\n下一步：01_react_from_scratch.py —— 不靠框架，手写一个 Agent。")


if __name__ == "__main__":
    main()
