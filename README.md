# AI Agent 学习实验室

一套**开箱即用、可逐层拆解**的 AI Agent 学习环境，位置 `D:\AIagent\agent-lab`。

- 独立虚拟环境（Python 3.13.9），与系统 Anaconda、WorkBuddy 内置 Python 完全隔离，不会影响其它项目。
- 已安装 21 个直接依赖，全部通过导入自检；离线示例与「模拟端点」全链路均已实际跑通。
- 核心思路：**先不用框架手写一遍 Agent，再用框架重写一遍**，才能真正看懂框架在帮你做什么。

> **完全零基础？** 双击 **`index.html`**，默认显示的就是「**先读这里**」：用大白话讲清 Agent 是什么、我为什么要装这些、每个文件为什么存在，重点都标好了。完整读本见 **[BEGINNER_GUIDE.md](BEGINNER_GUIDE.md)**。
>
> 面板还能点阶段卡片看学习内容、勾任务自动记进度、一键跳到「下一步该学」；「资料库」点开就读全部文档和代码，「练习台」点开就写并自动存草稿。无需服务器、无需联网、无需 API Key。路线全貌见 [LEARNING_PATH.md](LEARNING_PATH.md)。

---

## 一、马上开始

PowerShell：

```powershell
cd D:\AIagent\agent-lab
.\.venv\Scripts\python.exe check_env.py
.\.venv\Scripts\python.exe examples\01_react_from_scratch.py
```

Git Bash：

```bash
cd /d/AIagent/agent-lab
source .venv/Scripts/activate
python check_env.py
python examples/01_react_from_scratch.py
```

> 也可以直接激活环境（PowerShell 的 `.\.venv\Scripts\Activate.ps1`）后用 `python`；若执行策略拦截，用上面的全路径方式即可，功能完全一样。不需要 `conda activate`。

`check_env.py` 会列出每个包的版本、关键 API 是否可用、`.env` 是否配置好，并给出下一步。

### 面板使用说明（第一次打开，照着点）

双击 **`index.html`**，默认显示「**先读这里**」。==先读第 0～2 节（Agent 是什么 / 为什么需要它 / 四个零件），先别碰代码==；遇到不懂的词点左边「黑话小词典」。

1. 点「**学习路线**」→ 点任意阶段卡片 → 右侧最上面是「**这一阶段在讲什么（大白话）**」和「**为什么要学**」，下面才依次是 <span>要理解的知识</span> / <span>代码只是例子</span> / <span>动手验证</span>，三类都打了标签，不会混在一起。
2. 想读文件全文：阶段详情里点文件旁的「**查看**」，或去「**资料库**」。
3. 想写：点「**练习台**」→ 选阶段 → 载入模板 → 改 → 自动保存，写好后下载到项目目录跑。
4. 以后回来点右上角「**继续学习**」，自动到第一个未完成阶段；打勾的进度关掉浏览器也不会丢。
5. 跑不起来先跑 `python check_env.py`；没有 Key 就用 `examples/mock_api_server.py` 零成本练。

> 完整的白话读本（含使用说明、排错表、黑话词典）：**[BEGINNER_GUIDE.md](BEGINNER_GUIDE.md)**，也可以放进 Obsidian 读。

---

## 二、不用申请任何密钥，现在就能学

| 命令 | 你会看到什么 |
| --- | --- |
| `python examples/01_react_from_scratch.py` | 完整的 Thought → Action → Observation → Final Answer 循环，含多步工具调用 |
| `python examples/04_rag_mini.py` | RAG 的检索、打分、prompt 拼装全过程 |
| `python examples/04b_chromadb_rag.py` | 真正的向量数据库入库与距离检索 |
| `python examples/05_mcp_client.py` | MCP 工具发现、调用、资源读取（客户端会自动拉起服务端） |

带自定义问题试试：`python examples/01_react_from_scratch.py "Agent 的循环为什么要有上限"`

---

## 三、零成本跑通「需要模型」的那几课（推荐）

`examples/mock_api_server.py` 是一个本地假 OpenAI 兼容端点，只模拟协议、不含智能，用来观察 tool_calls 的完整往返。

**终端 A**（保持运行）：

```bash
python examples/mock_api_server.py --port 8765
```

**终端 B**（PowerShell 用 `$env:VAR="值"` 设置环境变量，Git Bash 用 `export`）：

```bash
export OPENAI_API_KEY=mock
export OPENAI_BASE_URL=http://127.0.0.1:8765/v1
export MODEL_NAME=mock-model
python examples/00_hello_llm.py
python examples/02_function_calling.py
python examples/03_langgraph_agent.py
python examples/04_rag_mini.py
```

这样不花一分钱，就能看到「模型决定调用工具 → 本地执行 → 结果回填 → 模型作答」以及 LangGraph 的节点流转。

---

## 四、六课学习路线

| # | 文件 | 核心问题 | 需要 Key |
| --- | --- | --- | --- |
| 0 | `00_hello_llm.py` | 密钥 / 端点 / 模型名三件套，最小一次调用 | 是（或 mock） |
| 1 | `01_react_from_scratch.py` | **Agent = LLM + 工具 + 循环 + 记忆**；ReAct、短期记忆、最大步数、工具安全 | 否 |
| 2 | `02_function_calling.py` | 用 JSON Schema + 结构化 `tool_calls` 替代文本正则解析 | 是（或 mock） |
| 3 | `03_langgraph_agent.py` | 图 / 状态 / reducer / 条件边 / 工具结果回流 | 是（或 mock） |
| 4 | `04_rag_mini.py` | 切分、稠密+稀疏混合检索、把证据拼进 prompt | 否（配了才生成答案） |
| 4b | `04b_chromadb_rag.py` | 换成 ChromaDB，理解向量入库与距离 | 否 |
| 5 | `05_mcp_server.py` + `05_mcp_client.py` | MCP：工具写一次，任何 Agent 都能接 | 否 |

配套文件：`examples/llm.py`（统一模型配置）、`examples/rag_utils.py`（检索零件）、`examples/mock_api_server.py`（假端点）。

> 需要**按周排期、每阶段动手任务与通过标准、贯穿式里程碑项目**的完整学习路线，见 **[LEARNING_PATH.md](LEARNING_PATH.md)**（四段十阶，约 14 周）。上面的六课是它的「代码主线」。

**毕业练习**（按难度）：
1. 把第 1 课的工具改造成 MCP server，让手写 ReAct Agent 通过 MCP 调用它们。
2. 给第 3 课的 `build_app()` 加 `checkpointer`，实现断点续跑 / 人工审批。
3. 把第 4 课的 `char_vector` 换成 `sentence-transformers` 的真实 embedding，对比召回质量。

---

## 五、接真实模型

复制 `.env.example` 为 `.env`（`.env` 不要提交到 Git），三种方案：

- **本地 Ollama（免费、离线）**：安装 Ollama 桌面程序 → `ollama pull qwen2.5:7b` → 用 `.env.example` 方案 A 的三行。Ollama 本体是独立软件，不是 pip 包。
- **模拟端点**：见第三节，最省事。
- **云服务**：DeepSeek / 阿里百炼 / 智谱等都提供 OpenAI 兼容接口。端点和模型名会随版本调整，**请以各服务商官方文档的「OpenAI 兼容」章节为准**（DeepSeek: `api-docs.deepseek.com`；阿里百炼: `help.aliyun.com/zh/model-studio`），填 `OPENAI_BASE_URL` 和 `MODEL_NAME` 即可，示例代码一行都不用改。

配好后 `00` / `02` / `03` / `04` 会自动切换到真实模型；`01` 也会自动把 MockLLM 换成真实模型。

---

## 六、装了什么

| 层 | 包 | 作用 |
| --- | --- | --- |
| 基础 | `openai` `python-dotenv` `pydantic` `httpx` `rich` `tenacity` `tiktoken` `pytest` | 调模型、管密钥、结构化输出、重试、token 计数、测试 |
| 框架 | `langchain` `langchain-openai` `langgraph` `mcp` `smolagents` | 抽象与工具、图式编排、工具协议、极简 Agent 源码 |
| 检索/工具 | `chromadb` `rank-bm25` `beautifulsoup4` `ddgs` `fastapi` `uvicorn` | 向量库、关键词检索、网页解析、免费搜索、把 Agent 包成服务 |
| 交互 | `jupyterlab` `ipykernel` | 分步骤运行、观察中间结果 |

关键版本：Python 3.13.9 · openai 3.46.0 · langchain 1.4.9 · langchain-openai 1.7.4 · mcp 2.3.0 · chromadb 1.5.9 · smolagents 1.26.0 · jupyterlab 4.6.6。

**故意没装**的都列在 `requirements-heavy.txt`：`torch` / `sentence-transformers`（约 2–3 GB）、`crewai` / `autogen`（重且 API 变动快）、`gradio` / `streamlit`、`langfuse` 等。学到对应章节再按需单个安装，别一次全装。

Jupyter 内核 `agent-lab` 已注册好，直接：

```bash
jupyter lab
```

新建 Notebook 时选 **Python (agent-lab)**。`notebooks/00_起步.ipynb` 是一个可直接运行的起点。

---

## 七、几个会卡住初学者的坑

1. **MCP 版本**：本环境是 `mcp 2.x`，网上大量教程里的 `from mcp.server.fastmcp import FastMCP` 已改名为 `from mcp.server.mcpserver import MCPServer`。要跟旧教程就 `pip install "mcp<2"`。
2. **LangChain 版本**：`1.x` 里 `initialize_agent` 已移除，用 `from langchain.agents import create_agent`；旧教程（0.x）代码不能直接抄。
3. **兼容端点**：`ChatOpenAI` 显式设了 `use_responses_api=False`，强制走 `/chat/completions`，因为 Ollama 和多数国内兼容端点没有实现 `/responses`。
4. **Python 3.13**：个别老包（旧版 `faiss-cpu` 等）没有对应 wheel，遇到 `No matching distribution` 属正常，换替代品即可。
5. **中文乱码**：PowerShell 里执行 `chcp 65001`，或设 `$env:PYTHONIOENCODING="utf-8"`。
6. **代理**：SDK 会读 `HTTP_PROXY` / `HTTPS_PROXY`；本地 Ollama / mock 端点若被代理拦截，把 `127.0.0.1,localhost` 加进 `NO_PROXY`。
7. **`.env` 不是 `.env.example`**：改完配置记得确认文件名，并且不要提交到 Git。

---

## 八、点开读代码 / 点开写代码

面板顶部除了「学习路线」，还有两个视图：

| 视图 | 能做什么 |
| --- | --- |
| **资料库** | 左侧列出 22 个本地文件：README、完整学习路线、11 个课程示例、3 个面板源码（index.html / app-library.js / build_library.py）、Notebook、运行日志与环境配置。点一下右侧就显示带行号的全文；可按**文件名或正文内容**搜索；支持复制全文、下载、系统打开、跳转到对应学习阶段；底部附官方文档与论文入口。 |
| **练习台** | 按阶段各存一份草稿，点「载入本阶段练习模板」直接生成带 TODO 清单的 Python 框架，可编辑、输入即自动保存到本机；支持导入任意本地 `.py` / `.md` 继续写，写好后下载为 `.py` 或 `.md`，放进项目目录用终端运行。 |

阶段详情里每个文件行也多了「**查看**」按钮，点一下直接跳到资料库读源码，不用自己去文件夹里翻。

**内容从哪来**：`build_library.py` 扫描项目文件生成 `library.js`（纯数据），网页用 `<script src>` 读取，因此 `file://` 双击打开也能读，不受浏览器本地文件跨域限制。改动文档或代码后重新同步一次：

```bash
python build_library.py
```

> 单个文件超过 60000 字符会截断，`install.log` 只收录前 60 行；`.venv`、缓存和二进制文件不收录。浏览器里不能直接运行 Python，练习台写好的代码要下载后用终端执行。

## 九、维护

```bash
# 复现 / 补齐依赖
.venv\Scripts\python.exe -m pip install -r requirements.txt

# 查看实际装了什么
.venv\Scripts\python.exe -m pip freeze

# 环境坏了就重建（不会影响学习资料和 .env）
rm -rf .venv  # Git Bash；PowerShell 用 Remove-Item -Recurse -Force .venv
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

安装日志在 `install.log`。完整依赖清单见 `requirements.txt`。

## 目录

```
agent-lab/
├── .venv/                    独立虚拟环境
├── BEGINNER_GUIDE.md         零基础白话读本（Agent 是什么 / 为什么 / 使用说明）
├── index.html                交互学习面板（双击打开，首屏就是白话讲解）
├── library.js                资料库数据（由 build_library.py 生成）
├── beginner.js               白话讲解内容（「先读这里」视图）
├── app-library.js            资料库、练习台、讲解视图逻辑
├── build_library.py          重新扫描项目文件并同步资料库
├── .env.example              模型配置模板（复制为 .env）
├── requirements.txt          主依赖
├── requirements-heavy.txt    可选重型依赖（默认不装）
├── check_env.py              一键自检
├── README.md                 本文件（快速上手）
├── LEARNING_PATH.md          完整学习路线（四段十阶 / 14 周 / 检查点）
├── install.log               安装日志
├── examples/                 六课示例 + 公共模块 + 模拟端点
└── notebooks/                Jupyter 起点
```
