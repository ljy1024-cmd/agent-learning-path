"""迷你 RAG 的公共零件：语料、分词、哈希向量、BM25、混合检索。

刻意用纯 Python + rank_bm25 实现，是为了让你看清检索的每一步；
真实项目里把 HybridRetriever 换成 embedding 模型 + 向量数据库即可（见 04b）。
"""
from __future__ import annotations

import hashlib
import math
import re

from rank_bm25 import BM25Okapi

DOCS = [
    "ReAct 模式让大模型交替进行推理 Thought 与行动 Action，工具返回的 Observation 会写回上下文。",
    "Agent 的短期记忆是当前对话的消息列表；长期记忆通常存在向量数据库里，按需检索后注入提示词。",
    "Function Calling 用 JSON Schema 描述工具参数，模型返回结构化 tool_calls，比正则解析文本更稳定。",
    "LangGraph 用图编排 Agent：节点表示步骤，边表示流转，条件边实现工具调用循环，状态可持久化。",
    "RAG 流程是：切分文档、向量化入库、检索 top-k 片段、拼进 prompt、让模型基于证据回答。",
    "MCP 即 Model Context Protocol，把工具、资源和提示词标准化，让不同 Agent 复用同一个工具服务器。",
    "多智能体系统把任务拆给不同角色，但会增加沟通成本与调试难度，初学建议先吃透单 Agent。",
]


# 中文虚词会稀释检索信号，先过滤掉。真实项目用分词器 + 停用词表。
STOPWORDS = set(
    "的 了 是 在 和 与 有 也 就 都 而 及 着 或 一 个 什 么 怎 如何 吗 呢 吧 把 被 "
    "让 对 中 为 上 下 这 那 我 你 它 要 会 能 用 使 问 答 请 帮 一下".split()
)


def tokenize(text: str) -> list[str]:
    """极简中英文分词：英文取词，中文取单字，过滤停用词。"""
    tokens = re.findall(r"[a-zA-Z]+|[\u4e00-\u9fff]", text.lower())
    return [t for t in tokens if t not in STOPWORDS]


def char_vector(text: str, dim: int = 128) -> list[float]:
    """hashing trick：把 token 哈希到固定维度并做 L2 归一化。

    英文缩写（MCP、RAG、Agent）是强信号，给 2 倍权重。
    注意：这只是「词面重合」的伪向量，不理解语义（"汽车"和"轿车"毫无关系）。
    换成 sentence-transformers 的 embedding，检索质量才会质变。
    """
    vec = [0.0] * dim
    for token in tokenize(text):
        weight = 2.0 if token.isascii() else 1.0
        idx = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16) % dim
        vec[idx] += weight
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]


def cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))  # 两个向量都已归一化


def _minmax(scores: list[float]) -> list[float]:
    low, high = min(scores), max(scores)
    span = high - low or 1.0
    return [(x - low) / span for x in scores]


class HybridRetriever:
    """稠密(字符哈希) + 稀疏(BM25) 混合检索，两路分数先归一化再加权。"""

    def __init__(self, docs: list[str] | None = None, dim: int = 128) -> None:
        self.docs = list(docs or DOCS)
        self.dim = dim
        self.vectors = [char_vector(d, dim) for d in self.docs]
        self.bm25 = BM25Okapi([tokenize(d) for d in self.docs])

    def search(self, query: str, k: int = 2, alpha: float = 0.5):
        query_vec = char_vector(query, self.dim)
        dense = _minmax([cosine(query_vec, v) for v in self.vectors])
        sparse = _minmax(list(self.bm25.get_scores(tokenize(query))))
        scores = [alpha * dense[i] + (1 - alpha) * sparse[i] for i in range(len(self.docs))]
        order = sorted(range(len(scores)), key=lambda i: -scores[i])[:k]
        return [(self.docs[i], round(scores[i], 3)) for i in order]


def build_prompt(question: str, hits: list[tuple[str, float]]) -> str:
    context = "\n".join(f"[{i + 1}] {doc}" for i, (doc, _) in enumerate(hits))
    return (
        "只根据下面的资料回答问题；资料里没有就直说不知道，不要编造。\n\n"
        f"资料：\n{context}\n\n"
        f"问题：{question}\n答案："
    )
