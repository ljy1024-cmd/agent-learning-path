"""第 5 课 b：MCP 客户端 —— 发现工具、调用工具、读取资源。

运行：python examples/05_mcp_client.py
不需要 API Key：这里演示的是「Agent 与工具之间的协议」，不是模型推理。
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


async def main() -> None:
    server_script = Path(__file__).with_name("05_mcp_server.py")
    params = StdioServerParameters(
        command=sys.executable,  # 用当前虚拟环境的 Python 启动服务端
        args=[str(server_script)],
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("发现的工具：")
            for item in tools.tools:
                print(f"  - {item.name}: {(item.description or '').strip()}")

            resources = await session.list_resources()
            print("\n发现的资源：", [str(r.uri) for r in resources.resources])

            result = await session.call_tool("add", {"a": 12, "b": 30})
            print("\n调用 add(12, 30) ->", result.content[0].text)

            result = await session.call_tool("get_time", {})
            print("调用 get_time()  ->", result.content[0].text)

            note = await session.read_resource("notes://agent-basics")
            print("\n读取资源 ->", note.contents[0].text)

    print("\n下一步：把这个 server 配进支持 MCP 的客户端，就能让真实 Agent 用上同一批工具。")
    print("毕业练习：把 01 课手写的工具改造成 MCP server，再让 ReAct Agent 通过 MCP 调用它们。")


if __name__ == "__main__":
    asyncio.run(main())
