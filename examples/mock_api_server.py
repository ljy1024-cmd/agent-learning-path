"""本地「假」OpenAI 兼容端点：不花钱、不联网，也能跑通完整 tool_calls 往返。

用途：在第 0/2/3 课里观察「模型请求 -> 本地执行工具 -> 结果回填 -> 模型作答」，
      而不用先去申请任何 API Key。它只做协议模拟，不含任何智能。

启动（另开一个终端，保持运行）：
    python examples/mock_api_server.py --port 8765

然后在 .env 里填：
    OPENAI_API_KEY=mock
    OPENAI_BASE_URL=http://127.0.0.1:8765/v1
    MODEL_NAME=mock-model

再运行：python examples/00_hello_llm.py / 02_function_calling.py / 03_langgraph_agent.py
"""
from __future__ import annotations

import argparse
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# 按请求里声明的工具集，生成对应的模拟调用
CANDIDATES = {
    "calculator": {"expression": "12 * (3 + 4)"},
    "get_weather": {"city": "北京"},
    "multiply": {"a": 12, "b": 8},
    "word_count": {"text": "Agent"},
}


def make_reply(body: dict) -> dict:
    messages = body.get("messages", [])
    tools = body.get("tools") or []
    tool_results = [str(m.get("content", "")) for m in messages if m.get("role") == "tool"]
    user_text = next(
        (str(m.get("content", "")) for m in reversed(messages) if m.get("role") == "user"),
        "",
    )

    message: dict = {"role": "assistant"}
    if tools and not tool_results:
        # 第一轮：模型「决定」调用工具（这里简单地把声明的工具都调一遍）
        names = [t.get("function", {}).get("name", "") for t in tools]
        calls = []
        for i, name in enumerate(names):
            if name in CANDIDATES:
                calls.append(
                    {
                        "id": f"call_mock_{i}",
                        "type": "function",
                        "function": {
                            "name": name,
                            "arguments": json.dumps(CANDIDATES[name], ensure_ascii=False),
                        },
                    }
                )
        message["tool_calls"] = calls
        message["content"] = ""
        finish_reason = "tool_calls"
    elif tool_results:
        message["content"] = "根据工具结果：" + "；".join(tool_results) + "。这是本地模拟服务的汇总回答。"
        finish_reason = "stop"
    elif "只根据下面的资料回答问题" in user_text:
        message["content"] = "（模拟回答）已收到 RAG 拼装好的资料片段；换成真实模型后，这里会基于资料生成答案。"
        finish_reason = "stop"
    else:
        message["content"] = "LLM 负责理解和生成；Agent 在它外面加上工具、循环与记忆，才能执行真实任务。"
        finish_reason = "stop"

    return {
        "id": "chatcmpl-mock",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": body.get("model", "mock-model"),
        "choices": [{"index": 0, "message": message, "finish_reason": finish_reason}],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }


class Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802 - 标准库方法名
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        try:
            body = json.loads(raw or b"{}")
        except json.JSONDecodeError:
            body = {}
        print(
            f"  <- {self.path}  messages={len(body.get('messages', []))}  "
            f"tools={len(body.get('tools') or [])}"
        )
        payload = json.dumps(make_reply(body), ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args) -> None:  # 关掉默认访问日志，保持输出干净
        pass


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Mock OpenAI API 已启动： http://127.0.0.1:{args.port}/v1")
    print("把 .env 的 OPENAI_BASE_URL 指向它，然后另开终端运行示例。Ctrl+C 停止。")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止。")


if __name__ == "__main__":
    main()
