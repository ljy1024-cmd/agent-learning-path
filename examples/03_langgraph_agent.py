"""第 3 课：LangGraph —— 把 Agent 写成一张「可循环、有状态」的图。

运行：python examples/03_langgraph_agent.py

与第 1 课对照着看：
    State.messages        == 我们手写的 history
    agent 节点             == llm(prompt)
    tools 节点(ToolNode)   == run_tool(...)
    tools_condition 条件边 == parse_output() 判断要不要继续
    tools -> agent 的回边  == for 循环
框架的价值在这里：状态管理、断点续跑、人工介入、并行节点都变得可组合。
"""
from __future__ import annotations

from typing import Annotated, TypedDict

from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from llm import API_KEY, BASE_URL, MODEL, has_key


@tool
def multiply(a: int, b: int) -> int:
    """计算两个整数的乘积。"""
    return a * b


@tool
def word_count(text: str) -> int:
    """统计一段文本的字符数。"""
    return len(text)


TOOLS = [multiply, word_count]


class State(TypedDict):
    # add_messages 是 reducer：每个节点返回的新消息会「追加」而不是覆盖历史
    messages: Annotated[list, add_messages]


def build_app():
    # use_responses_api=False 强制走 /chat/completions：
    # 本地 Ollama、多数国内兼容端点和 mock_api_server 都只实现这个协议。
    kwargs = {"model": MODEL, "temperature": 0, "use_responses_api": False}
    if API_KEY:
        kwargs["openai_api_key"] = API_KEY
    if BASE_URL:
        kwargs["openai_api_base"] = BASE_URL

    llm = ChatOpenAI(**kwargs).bind_tools(TOOLS)

    def agent_node(state: State):
        return {"messages": [llm.invoke(state["messages"])]}

    builder = StateGraph(State)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", ToolNode(TOOLS))
    builder.add_edge(START, "agent")
    # 模型返回 tool_calls 就转到 tools 节点，否则结束
    builder.add_conditional_edges("agent", tools_condition, {"tools": "tools", END: END})
    builder.add_edge("tools", "agent")  # 工具结果回流给模型 —— 这就是循环
    return builder.compile()


def main() -> None:
    print("图结构： START -> agent --(有 tool_calls?)--> tools --(结果回流)--> agent -> ... -> END")
    print("练习：把 builder.add_edge('tools', 'agent') 删掉，看看会发生什么。")

    if not has_key():
        print("\n[未配置模型] 配好 .env 后再运行，可逐节点观察消息流。")
        print("零成本方案：用 mock_api_server.py 起一个本地假端点（见 README）。")
        return

    app = build_app()
    question = "请计算 12 乘以 8，再统计 Agent 这个单词的字符数"
    print(f"\n问题：{question}\n")
    for state in app.stream(
        {"messages": [HumanMessage(content=question)]}, stream_mode="values"
    ):
        state["messages"][-1].pretty_print()
        print("-" * 60)

    print("\n下一课：04_rag_mini.py —— 让 Agent 用上外部知识。")


if __name__ == "__main__":
    main()
