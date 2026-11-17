"""第 4 课：手写迷你 RAG —— 检索增强生成（零密钥、零网络即可运行）。

运行：python examples/04_rag_mini.py

RAG 五步：切分 -> 向量化 -> 入库 -> 检索 top-k -> 拼进 prompt。
本课用纯 Python 把每一步摊开，配好 .env 后还会真的让模型基于检索结果作答。
"""
from __future__ import annotations

from llm import MODEL, get_client, has_key
from rag_utils import DOCS, HybridRetriever, build_prompt


def main() -> None:
    retriever = HybridRetriever()
    print(f"语料库共 {len(DOCS)} 段；检索 = 字符哈希向量(稠密) + BM25(稀疏) 混合打分\n")

    questions = [
        "Agent 怎么记住之前说过的话？",
        "工具调用为什么要用 JSON Schema？",
        "MCP 是干什么的？",
    ]

    for question in questions:
        hits = retriever.search(question, k=2)
        print("=" * 66)
        print(f"问题：{question}")
        print("召回片段：")
        for i, (doc, score) in enumerate(hits, 1):
            print(f"  [{i}] score={score:.3f}  {doc[:46]}...")

        prompt = build_prompt(question, hits)
        print(f"\n拼装后的 prompt（前 180 字）：\n  {prompt[:180]} ...")

        if has_key():
            answer = (
                get_client()
                .chat.completions.create(
                    model=MODEL, messages=[{"role": "user", "content": prompt}]
                )
                .choices[0]
                .message.content
            )
            print(f"\n模型基于资料作答：{answer}")
        print()

    if not has_key():
        print("[未配置模型] 上面已经跑完 RAG 的检索与增强两半；配好 .env 后会补上「生成」那一半。")
    print("思考题：把 alpha 从 0.5 改成 0 或 1，召回结果有什么变化？")
    print("       为什么「汽车」和「轿车」在这套向量里毫不相似？")
    print("下一课：04b_chromadb_rag.py —— 换成真正的向量数据库。")


if __name__ == "__main__":
    main()
