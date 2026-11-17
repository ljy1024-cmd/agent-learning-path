"""第 4 课 b：把检索换成真正的向量数据库 ChromaDB（依然零密钥、零下载）。

运行：python examples/04b_chromadb_rag.py

关键技巧：直接传 embeddings= 预计算好的向量，绕开默认的 embedding 模型，
所以不用下载几百 MB 的模型文件也能完整体验「入库 / 检索 / 距离」。
真实项目把 char_vector 换成 sentence-transformers 即可，其余代码不用动。
"""
from __future__ import annotations

import chromadb

from rag_utils import DOCS, build_prompt, char_vector


def main() -> None:
    client = chromadb.EphemeralClient()  # 内存版，进程结束即清空
    collection = client.create_collection("agent-notes")

    collection.add(
        ids=[f"doc-{i}" for i in range(len(DOCS))],
        documents=DOCS,
        embeddings=[char_vector(doc) for doc in DOCS],
    )
    print(f"已入库 {collection.count()} 条文档\n")

    queries = ["长期记忆放在哪里", "图编排有什么好处"]
    for query in queries:
        result = collection.query(
            query_embeddings=[char_vector(query)],
            n_results=2,
            include=["documents", "distances"],
        )
        docs = result["documents"][0]
        distances = result["distances"][0]
        print(f"问题：{query}")
        for i, (doc, dist) in enumerate(zip(docs, distances), 1):
            print(f"  [{i}] L2距离={dist:.3f}  {doc[:44]}...")
        print(f"\n{build_prompt(query, [(d, 1 - x) for d, x in zip(docs, distances)])[:160]} ...\n")

    print("持久化版本只需换一行：")
    print('  client = chromadb.PersistentClient(path="./.chroma_data")')
    print("  collection = client.get_or_create_collection(\"agent-notes\")  # 用 get_or_create 避免重复建表")
    print("\n下一课：05_mcp_client.py —— 让工具变成可复用的标准服务。")


if __name__ == "__main__":
    main()
