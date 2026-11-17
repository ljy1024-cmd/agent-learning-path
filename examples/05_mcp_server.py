"""第 5 课 a：用 MCP 把工具发布成「标准服务」。

运行：python examples/05_mcp_client.py （客户端会自动拉起本文件，不用手动启动）

重要版本提示：本环境装的是 mcp 2.x，旧教程里的
    from mcp.server.fastmcp import FastMCP
在 2.x 已改名为
    from mcp.server.mcpserver import MCPServer
若你要跟着 mcp 1.x 的旧教程走，可执行：pip install "mcp<2"

MCP 的意义：工具写一次，任何支持 MCP 的 Agent / IDE 都能直接接入，
不用在每个项目里重写一遍工具定义。
"""
from __future__ import annotations

from datetime import datetime

from mcp.server.mcpserver import MCPServer

mcp = MCPServer("agent-lab-demo")


@mcp.tool()
def add(a: int, b: int) -> int:
    """计算两个整数的和。"""
    return a + b


@mcp.tool()
def get_time() -> str:
    """获取当前的日期和时间。"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@mcp.resource("notes://agent-basics")
def agent_basics() -> str:
    """一份可供 Agent 读取的静态资料。"""
    return "Agent = LLM + Tools + Loop + Memory。工具通过 MCP 暴露，就能被不同客户端复用。"


if __name__ == "__main__":
    mcp.run(transport="stdio")
