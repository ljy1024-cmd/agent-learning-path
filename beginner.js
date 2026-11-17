/* 「先读这里」的白话讲解内容：面向完全零基础，重点讲「是什么 / 为什么 / 文件为什么存在」。
   纯静态内容，由 app-library.js 渲染成卡片与导航。 */
window.BEGINNER = {
  sections: [
    {
      id: "what", nav: "0 · Agent 是什么", title: "一句话说清 Agent 是什么",
      html: `
<div class="lead">这一节回答：<b>我到底在学个什么东西？</b>　<span class="tag knowledge">要理解的知识</span></div>
<div class="key">Agent = 一个会自己「想一想 → 动一下手 → 看看结果 → 再想一想」，直到把事情做完的程序。</div>
<p>先用三样你熟悉的东西对比：</p>
<table class="bg-table">
<tr><th>东西</th><th>像什么</th><th>你给它一句话，它会…</th></tr>
<tr><td>普通程序</td><td>自动售货机</td><td>按哪个键出哪瓶水，<b>固定的</b></td></tr>
<tr><td>聊天 AI</td><td>一本百科全书</td><td>回答你，但<b>只动嘴，不动手</b></td></tr>
<tr><td><b>Agent</b></td><td><b>一个实习生</b></td><td>自己去查、自己算、自己判断，最后把事情做完</td></tr>
</table>
<p>举个例子：你说「帮我算 12 乘以 3 加 4 的和，再告诉我现在几点」。</p>
<div class="analogy"><b>聊天 AI</b>：直接猜。它不擅长算数，也不知道现在几点，很可能算错、时间瞎编。<br>
<b>Agent</b>：想「这要算数，我不该心算」→ 叫计算器工具 → 拿到 84 → 再想「还要时间」→ 叫时钟工具 → 拿齐了才回答。</div>
<div class="key">关键区别只有一句：<b>大模型只会「说」，Agent 会「做」</b>。大模型是大脑，Agent 是大脑 + 手脚 + 记事本 + 不达目的不罢休的循环。</div>
<div class="whybox"><b>为什么你要先知道这个：</b>后面所有要装的东西、要看的代码、要学的阶段，全都是在给这个「实习生」补零件。先记住这张脸，再看细节就不会迷路。</div>
`
    },
    {
      id: "why-agent", nav: "1 · 为什么需要它", title: "为什么需要 Agent：大模型有三个做不到",
      html: `
<div class="lead">这一节回答：<b>有聊天 AI 了，为什么还要多此一举？</b></div>
<div class="key">下面三个坑，每一个都得靠一个零件来填 —— 这就是后面所有学习内容的来源。</div>
<table class="bg-table">
<tr><th>大模型做不到</th><th>具体表现</th><th>所以要补什么</th></tr>
<tr><td><b>不知道最新的、私人的事</b></td><td>不知道今天几号、你电脑里有什么、你笔记写了啥</td><td>工具（去查）+ RAG（把你的资料递给它）</td></tr>
<tr><td><b>不会真的动手</b></td><td>不能算数、不能读文件，只能生成文字</td><td>工具：让 Python 代码替它动手</td></tr>
<tr><td><b>说完就完，不会检查</b></td><td>答错不会自己发现，更不会重来</td><td>循环：把结果拿回来给它看，让它再判断</td></tr>
</table>
<div class="whybox"><b>为什么要知道：</b>只有大模型，你得到的是一个聊天窗口；加上这层，才得到能替你干活的助手。这一句话就是整门课的主线。</div>
`
    },
    {
      id: "parts", nav: "2 · 四个零件（重点）", title: "Agent 的四个零件 —— 这才是真正要学的内容",
      html: `
<div class="lead">这一节回答：<b>哪些是知识，哪些只是代码？</b>　<span class="tag knowledge">下面四块是知识</span> <span class="tag code">.py 文件只是演示</span></div>
<div class="key">大脑负责判断，工具负责动手，循环负责不放弃，记忆负责不忘事。<br>剩下的名词（LangGraph、MCP、向量库）都只是<b>让这四个零件更省事、更标准</b>，不是新知识。</div>

<div class="part-card">
  <div class="part-head"><span class="part-num">1</span><b>大脑（LLM）</b><span class="tag knowledge">知识</span></div>
  <p><b>是什么：</b>负责「理解你的话、决定下一步说什么」的模型，跑在服务器上（或你电脑上的 Ollama）。</p>
  <div class="whybox"><b>为什么必须有：</b>没有它，程序只会按固定规则走，遇到没写过的情况就傻了。类比：实习生的脑子。</div>
  <p><b>一个反直觉的事实：</b>它<b>自己不记得上一句话</b>。每次调用都像第一次见面，必须把之前的对话重新发一遍。</p>
  <p class="fileline"><b>文件 <code>examples/llm.py</code> 为什么存在：</b>连哪个模型、密钥写在哪这些杂事，散在十个示例里就要改十次。收在一个文件里，<b>改一处，全部示例跟着变</b>。</p>
</div>

<div class="part-card">
  <div class="part-head"><span class="part-num">2</span><b>工具（Tools）</b><span class="tag knowledge">知识</span></div>
  <p><b>是什么：</b>普通的 Python 函数，比如「算数」「取当前时间」「在本地笔记里找一句话」。类比：实习生的手和桌上的计算器。</p>
  <div class="whybox"><b>为什么必须有：</b>模型只会输出文字，<b>它算不了数、读不了文件</b>。真正干活的是你写的函数。</div>
  <p><b>关键认识：</b>所谓「让 AI 用工具」，其实是模型输出一句「请调用某某工具，参数是…」，<b>由你的程序去执行</b>，再把结果告诉它。模型从头到尾没碰过你的电脑。</p>
  <p class="fileline"><b>文件 <code>01_react_from_scratch.py</code> 为什么存在：</b>它故意不用任何框架、纯手写，短、没有黑盒，能看清每一步。<b>这是全程最值钱的文件</b>。</p>
</div>

<div class="part-card">
  <div class="part-head"><span class="part-num">3</span><b>循环（Loop）</b><span class="tag knowledge">知识</span></div>
  <p><b>是什么：</b>把「想 → 调工具 → 看结果 → 再想」重复起来，直到模型说「可以回答了」。类比：实习生做完一步回来问「接下来呢」。</p>
  <div class="whybox"><b>为什么必须有：</b>一次调用只能做一步，「先算再查时间」这种事必须来回好几轮。<b>有没有循环，是 Agent 和一次问答的唯一分界线。</b></div>
  <p><b>为什么还要有上限：</b>模型可能反复调同一个工具停不下来，所以必须写 <code>max_steps</code> 强制结束。这是 Agent 最容易出的 bug，也是必考题。</p>
</div>

<div class="part-card">
  <div class="part-head"><span class="part-num">4</span><b>记忆（Memory）</b><span class="tag knowledge">知识</span></div>
  <p><b>是什么：</b>每轮把「之前问了什么、调了什么工具、拿到什么结果」重新拼进下一次提问里。类比：实习生的记事本。</p>
  <div class="whybox"><b>为什么必须有：</b>API 是无状态的，你不重发，它就真的不记得（接零件 1 那个事实）。</div>
  <p><b>进阶一点：</b>短期记忆 = 本次对话；长期记忆 = 存在向量库里、要用时检索出来的你自己的资料，这就是 <b>RAG</b>。</p>
  <p class="fileline"><b>文件 <code>04_rag_mini.py</code> 为什么存在：</b>光靠对话历史记不住几百页笔记。RAG = 先翻出相关几段，连同问题交给模型，让它照着答而不是凭空编。</p>
</div>
<button class="btn primary" data-beginner-stage="2">去看阶段 2：亲手造一个 →</button>
`
    },
    {
      id: "why-install", nav: "3 · 为什么装这些", title: "我为什么要安装这些（按麻烦看，别按包名看）",
      html: `
<div class="lead">这一节回答：<b>装那一堆包到底图什么？</b></div>
<div class="key">这些不是要背的清单，是<b>你路上会踩的坑，提前垫好的板子</b>。现在不用全懂，用到再回来查。</div>
<table class="bg-table">
<tr><th>你会遇到的麻烦</th><th>装的什么</th><th>不装会怎样</th></tr>
<tr><td>想跟模型说句话</td><td><code>openai</code> <code>python-dotenv</code></td><td>自己手拼 HTTP 请求，密钥还得硬写在代码里（很危险）</td></tr>
<tr><td>想把模型的话交给程序用</td><td><code>pydantic</code></td><td>靠字符串切割，格式一变就崩</td></tr>
<tr><td>网络抖一下就全停</td><td><code>tenacity</code></td><td>每次失败都手动重跑</td></tr>
<tr><td>想知道花了多少、会不会超长</td><td><code>tiktoken</code></td><td>两眼一抹黑</td></tr>
<tr><td>不想每次手写循环和状态</td><td><code>langchain</code> <code>langgraph</code></td><td>消息历史、断点、分支全自己管</td></tr>
<tr><td>想让 Agent 读我的笔记</td><td><code>chromadb</code> <code>rank-bm25</code></td><td>模型只能凭记忆瞎编</td></tr>
<tr><td>想让工具写一次到处用</td><td><code>mcp</code></td><td>每个项目重写一遍工具</td></tr>
<tr><td>想一步步看中间结果</td><td><code>jupyterlab</code></td><td>只能整段运行，不知哪步坏了</td></tr>
<tr><td>想确认改完没弄坏</td><td><code>pytest</code></td><td>全靠肉眼</td></tr>
<tr><td><b>想不花钱先跑通</b></td><td><code>mock_api_server.py</code></td><td>得先注册、绑卡，还没学就卡住</td></tr>
</table>
<div class="whybox"><b>为什么有的没装：</b><code>torch</code> 这些好几 GB 的东西故意留在 <code>requirements-heavy.txt</code>。初学用不到，装了只会让电脑变慢、安装更容易出错。<b>学到 RAG 那节再装，来得及。</b></div>
<div class="whybox"><b>为什么单独建 <code>.venv</code>：</b>不同项目要的包版本会打架。把它想成「这个项目的专属工具箱」，装坏了删掉重来，不会连累电脑上其它 Python 程序。</div>
`
    },
    {
      id: "why-files", nav: "4 · 文件为什么存在", title: "每个文件为什么存在（路径不是学习清单）",
      html: `
<div class="lead">这一节回答：<b>这些路径我为什么要有？要一个个啃完吗？</b></div>
<div class="key">文件是「遇到问题时去查的工具」，不是「要逐个啃完的课本」。<b>真正要学的是第 2 节那四块知识。</b></div>
<table class="bg-table">
<tr><th>文件</th><th>它回答的一个问题</th><th>什么时候看</th></tr>
<tr><td><code>index.html</code></td><td>我今天该学什么、学到哪了</td><td><b>每天打开这个就行</b>，不用记其它路径</td></tr>
<tr><td><code>BEGINNER_GUIDE.md</code></td><td>这些黑话到底啥意思</td><td>看不懂任何东西时</td></tr>
<tr><td><code>README.md</code></td><td>东西装哪了、命令怎么敲</td><td>环境出问题、忘了怎么启动</td></tr>
<tr><td><code>LEARNING_PATH.md</code></td><td>接下来学什么、怎样算学会</td><td>想知道全貌和检查点</td></tr>
<tr><td><code>check_env.py</code></td><td>是不是我环境坏了</td><td><b>任何示例跑不起来，第一个跑它</b></td></tr>
<tr><td><code>examples/llm.py</code></td><td>密钥和模型地址放哪</td><td>要接自己的模型时</td></tr>
<tr><td><code>examples/00_hello_llm.py</code></td><td>一次最简调用长什么样</td><td>阶段 1</td></tr>
<tr><td><code>examples/01_react_from_scratch.py</code></td><td>Agent 的循环到底怎么转</td><td><b>阶段 2，最重要</b></td></tr>
<tr><td><code>examples/02_function_calling.py</code></td><td>怎样让模型按规矩给参数</td><td>阶段 3</td></tr>
<tr><td><code>examples/03_langgraph_agent.py</code></td><td>框架替我省了哪些事</td><td>阶段 4</td></tr>
<tr><td><code>examples/04_rag_mini.py</code> 等</td><td>怎么让它读我自己的资料</td><td>阶段 5</td></tr>
<tr><td><code>examples/05_mcp_server.py</code> 等</td><td>工具怎么给别人复用</td><td>阶段 6</td></tr>
<tr><td><code>examples/mock_api_server.py</code></td><td>没 Key 怎么练</td><td>想零成本跑通时</td></tr>
<tr><td><code>build_library.py</code> / <code>library.js</code></td><td>网页为什么能读到文件内容</td><td>改动文档后跑一次同步</td></tr>
<tr><td><code>requirements.txt</code></td><td>这台电脑到底装了啥</td><td>换电脑、重装环境</td></tr>
<tr><td><code>.env.example</code></td><td>密钥写在哪、什么格式</td><td>第一次配模型（真实密钥绝不写进去）</td></tr>
</table>
<div class="whybox"><b>为什么示例要拆成 00～05 六个文件：</b>一个文件只演示一个新东西。看不懂时能确定「问题就出在这一小段」，而不是在一大坨代码里迷路。<b>这不是代码堆叠，是把知识切开。</b></div>
`
    },
    {
      id: "glossary", nav: "5 · 黑话小词典", title: "看不懂的词，回来查这里",
      html: `
<div class="lead">这一节回答：<b>他们说的那些词到底是什么意思？</b>　不用背，随查随用。</div>
<table class="bg-table">
<tr><th>词</th><th>大白话</th><th>为什么你要知道</th></tr>
<tr><td>大模型 / LLM</td><td>很会理解和生成文字的程序</td><td>它是 Agent 的大脑</td></tr>
<tr><td>API</td><td>别人留的一个「窗口」，按格式递话进去，递结果出来</td><td>你和模型之间靠它通信</td></tr>
<tr><td>Key（密钥）</td><td>证明「是你在用」的密码</td><td>没有它调不通；<b>不能写进代码或发给别人</b></td></tr>
<tr><td>端点 / base_url</td><td>那个窗口的地址</td><td>换服务商、换本地 Ollama 就是改它</td></tr>
<tr><td>token</td><td>模型眼里的「字块」</td><td>按它收费、按它限制长度</td></tr>
<tr><td>prompt</td><td>你发给模型的全部文字</td><td>Agent 一大半功夫在「该把什么拼进去」</td></tr>
<tr><td>上下文窗口</td><td>一次能塞给模型的文字上限</td><td>塞不下要截断，历史太长会出事</td></tr>
<tr><td>消息角色</td><td>谁说的话：system 规矩 / user 你 / assistant 模型 / tool 工具结果</td><td>顺序错了模型会懵</td></tr>
<tr><td>temperature</td><td>回答的随机程度，0 最稳</td><td>要稳定结果就调低</td></tr>
<tr><td>工具 / Tool</td><td>你写的、能被模型叫去干活的普通函数</td><td>模型自己不会动手</td></tr>
<tr><td>Function Calling</td><td>模型说「请调用 X，参数是 Y」的固定格式</td><td>比让它自由发挥文本稳得多</td></tr>
<tr><td>Observation</td><td>工具跑完拿回来的结果</td><td>循环靠它决定下一步</td></tr>
<tr><td>ReAct</td><td>「想一步、做一步、看一步」的套路</td><td>最经典的 Agent 工作方式</td></tr>
<tr><td>循环 / Loop</td><td>上面这套动作重复好几轮</td><td><b>有没有它，是 Agent 和问答的分界</b></td></tr>
<tr><td>记忆</td><td>把之前发生过什么重新发给模型</td><td>模型默认什么都不记得</td></tr>
<tr><td>RAG</td><td>先从你资料里翻出相关几段，再让模型照着答</td><td>不这么做它就只能编</td></tr>
<tr><td>向量 / embedding</td><td>把文字变成一串数字，好比较「像不像」</td><td>检索靠它找相似内容</td></tr>
<tr><td>框架</td><td>把常用套路打包好的工具箱（LangChain / LangGraph）</td><td>省事，但<b>先懂原理再用</b></td></tr>
<tr><td>MCP</td><td>工具的「统一插座」标准</td><td>工具写一次，不同 Agent 都能插上用</td></tr>
<tr><td>虚拟环境 / venv</td><td>本项目专属的工具箱</td><td>防止不同项目互相搞坏</td></tr>
<tr><td>依赖</td><td>别人写好的、你的程序要用的代码包</td><td>就是第 3 节那些</td></tr>
</table>
`
    },
    {
      id: "map", nav: "6 · 到底学什么", title: "十个阶段到底在学什么（按知识分层）",
      html: `
<div class="lead">这一节回答：<b>那些阶段卡片背后，我究竟要获得什么认识？</b>　<span class="tag knowledge">内容地图</span></div>
<div class="key">每一层学的是一种认识；代码只是拿来验证你有没有真的懂。</div>

<div class="layer"><div class="layer-t">第一层 · 先搞懂对象 <span>阶段 0–1</span></div>
<p><b>学什么：</b>Python 够用的部分、HTTP/密钥是什么、大模型一次调用发生了什么。<br>
<b>为什么：</b>还不会走路之前别急着造机器人，这两阶段<b>不需要写 Agent</b>。<br>
<b>学完能回答：</b>「为什么模型不记得我上一句？」</p>
<button class="btn small" data-beginner-stage="0">看阶段 0</button> <button class="btn small" data-beginner-stage="1">看阶段 1</button></div>

<div class="layer hot"><div class="layer-t">第二层 · 亲手造一个 <span>阶段 2–3，最值钱</span></div>
<p><b>学什么：</b>四个零件怎么拼起来（阶段 2）；怎样让工具调用变可靠（阶段 3）。<br>
<b>为什么：</b>只有自己手写过一遍循环，后面看框架才知道框架在替你做什么；直接学框架会变成「会调包但不会排错」。<br>
<b>学完能回答：</b>「第 2 轮给模型的提问，比第 1 轮多了什么？」</p>
<button class="btn small" data-beginner-stage="2">看阶段 2</button> <button class="btn small" data-beginner-stage="3">看阶段 3</button></div>

<div class="layer"><div class="layer-t">第三层 · 用框架重做一遍 <span>阶段 4</span></div>
<p><b>学什么：</b>状态、节点、条件边、断点续跑。<br>
<b>为什么：</b>不是学新知识，是学「怎么把上一层手写的循环管得更好」。做一张和手写版的一一对照表，这节就通了。</p>
<button class="btn small" data-beginner-stage="4">看阶段 4</button></div>

<div class="layer"><div class="layer-t">第四层 · 给它知识和手脚 <span>阶段 5–6</span></div>
<p><b>学什么：</b>RAG（读你的资料）、MCP（工具复用）。<br>
<b>为什么：</b>前两层的 Agent 只会用写死的两个工具、只有对话历史；要真正有用，得接触外部资料和标准工具。</p>
<button class="btn small" data-beginner-stage="5">看阶段 5</button> <button class="btn small" data-beginner-stage="6">看阶段 6</button></div>

<div class="layer"><div class="layer-t">第五层 · 让它靠谱 <span>阶段 7–9</span></div>
<p><b>学什么：</b>多智能体（选修）、评估与测试、安全、把它变成能给别人用的服务。<br>
<b>为什么：</b>能跑 ≠ 能用。得能证明「改了之后变好了」，得防住恶意输入，得让别人也启动得起来。</p>
<button class="btn small" data-beginner-stage="8">看阶段 8</button> <button class="btn small" data-beginner-stage="9">看阶段 9</button></div>
`
    },
    {
      id: "howto", nav: "7 · 使用说明", title: "使用说明：第一次打开，照着点就行",
      html: `
<div class="lead">这一节回答：<b>我现在具体该点哪里、按什么顺序？</b></div>
<div class="key">你不需要记任何文件路径。所有东西都在 <code>index.html</code> 里，点着走。</div>

<h3>第一次（约 15 分钟）</h3>
<div class="step"><b>1</b><span>双击 <code>index.html</code>（或在预览面板打开）。默认显示的就是「先读这里」。</span></div>
<div class="step"><b>2</b><span>从上往下读第 0～2 节：Agent 是什么、为什么需要它、四个零件。<b>先别碰代码</b>，读完就知道这门课在干什么。</span></div>
<div class="step"><b>3</b><span>遇到不懂的词，点左边「黑话小词典」。</span></div>
<div class="step"><b>4</b><span>点顶部「学习路线」→ 点「阶段 0」卡片 → 右边告诉你：学完能干什么、要懂哪些概念、要做哪几件事。</span></div>
<div class="step"><b>5</b><span>阶段详情里每个文件名旁有「<b>查看</b>」按钮，点一下直接跳「资料库」看全文，不用自己去文件夹翻。</span></div>
<div class="step"><b>6</b><span>想动手写：点「练习台」→ 选阶段 → 「载入本阶段练习模板」→ 改一改 → 自动保存；写好后下载成 .py，放进项目用终端跑。</span></div>

<h3>以后每次回来</h3>
<div class="step"><b>·</b><span>点右上角「<b>继续学习</b>」，直接到第一个没完成的阶段。</span></div>
<div class="step"><b>·</b><span>做完的任务<b>打勾就自动记住</b>，关掉浏览器再打开还在。</span></div>
<div class="step"><b>·</b><span>想看代码 → 资料库；想查词 → 黑话小词典；忘了下一步 → 学习路线。</span></div>

<h3>跑不起来 / 看不懂时</h3>
<table class="bg-table">
<tr><th>情况</th><th>怎么办</th></tr>
<tr><td>任何示例报错</td><td>先跑 <code>python check_env.py</code>，排除环境问题</td></tr>
<tr><td>代码看不懂</td><td>回第 2 节把四个零件想明白 —— <b>这是正常的</b></td></tr>
<tr><td>名词不认识</td><td>查「黑话小词典」</td></tr>
<tr><td>没有 API Key</td><td>用 <code>mock_api_server.py</code> 零成本跑通，或装 Ollama 本地免费跑</td></tr>
<tr><td>不知道学到哪了</td><td>看顶部进度条，或点「继续学习」</td></tr>
<tr><td>觉得阶段 2 很慢</td><td><b>正常，那是最值钱的一节</b>，慢一点没关系</td></tr>
</table>
<div class="whybox"><b>每天 30 分钟的最小节奏：</b>读 1 小节 → 跑 1 个示例 → 勾 1 个任务 → 在练习台写 3 行「今天懂了什么」。四步做完就可以关掉。</div>

<div class="key">最后一句：你要学的不是这 22 个文件，也不是那 21 个包，而是<b>「一个只会说话的模型，怎么被加上手脚、记事本和不放弃的循环，变成能替你做事的东西」</b>。代码、框架、路径都只是这句话的注脚。</div>
<div class="end-actions"><button class="btn primary" data-beginner-stage="0">从阶段 0 开始 →</button> <button class="btn" data-beginner-go="library">去资料库看文件</button></div>
`
    }
  ]
};
