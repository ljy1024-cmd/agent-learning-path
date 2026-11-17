/* 资料库 + 练习台：为 index.html 增加「点开读文件 / 点开写代码」的能力。
   依赖 window.LIBRARY（build_library.py 生成）与主页面里的 STAGES、switchView。 */
(function () {
  "use strict";

  const LIB = window.LIBRARY || { files: [], links: [], generated: "", root: "" };
  const FILES = LIB.files || [];
  const LINKS = LIB.links || [];
  const DRAFT_KEY = "agent-lab-drafts-v1";
  const Q = (s) => document.querySelector(s);
  const E = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;" }[c]));

  let currentPath = null;
  let filterText = "";
  let draftStage = 0;
  let drafts = loadDrafts();
  let saveTimer = null;

  function loadDrafts() {
    try { return JSON.parse(localStorage.getItem(DRAFT_KEY) || "{}") || {}; }
    catch (e) { return {}; }
  }
  function saveDrafts() {
    try { localStorage.setItem(DRAFT_KEY, JSON.stringify(drafts)); } catch (e) {}
  }
  function notify(msg) {
    try { toast(msg); return; } catch (e) {}
    const n = Q("#toast");
    if (n) { n.textContent = msg; n.classList.add("show"); setTimeout(() => n.classList.remove("show"), 1600); }
  }
  function fmtSize(n) { return n < 1024 ? n + " B" : (n / 1024).toFixed(1) + " KB"; }
  function iconFor(lang) {
    return ({ python: "PY", markdown: "MD", json: "NB", ini: "CFG", text: "TXT", html: "HT", javascript: "JS" })[lang] || "TXT";
  }
  async function copyText(text) {
    try {
      if (navigator.clipboard && window.isSecureContext) { await navigator.clipboard.writeText(text); return true; }
    } catch (e) {}
    try {
      const ta = document.createElement("textarea");
      ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
      document.body.appendChild(ta); ta.select();
      const ok = document.execCommand("copy"); ta.remove(); return ok;
    } catch (e) { return false; }
  }
  function download(name, text) {
    try {
      const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url; a.download = name;
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1500);
      return true;
    } catch (e) { return false; }
  }
  function fileUrl(rel) {
    return "file:///" + String(LIB.root || "").replace(/^\/+/, "") + "/" + rel;
  }

  /* ---------------- 资料库 ---------------- */

  function matches(f) {
    if (!filterText) return true;
    const q = filterText.toLowerCase();
    return f.path.toLowerCase().includes(q) ||
      f.name.toLowerCase().includes(q) ||
      f.content.toLowerCase().includes(q);
  }

  function renderTree() {
    const box = Q("#libTree");
    if (!box) return;
    if (!FILES.length) {
      box.innerHTML = '<div class="lib-empty">没有找到 library.js 的数据。<br>在项目根目录运行 <b>python build_library.py</b> 后刷新页面。</div>';
      return;
    }
    const groups = {};
    FILES.forEach((f) => { (groups[f.group] = groups[f.group] || []).push(f); });
    let hit = 0;
    let html = '<div class="lib-search-row"><input id="libSearch" class="lib-search" type="search" placeholder="搜索文件名或文件内容…" value="' + E(filterText) + '">' +
      '<div class="lib-meta">共 ' + FILES.length + ' 个文件 · ' + FILES.reduce((n, f) => n + f.lines, 0).toLocaleString() + ' 行 · 生成于 ' + E(LIB.generated) + '</div></div>';

    Object.keys(groups).forEach((g) => {
      const list = groups[g].filter(matches);
      hit += list.length;
      if (!list.length) return;
      html += '<div class="lib-group"><div class="lib-group-t">' + E(g) + '<span>' + list.length + '</span></div>';
      list.forEach((f) => {
        html += '<button class="lib-item' + (f.path === currentPath ? " active" : "") + '" data-file="' + E(f.path) + '">' +
          '<span class="lib-icon">' + iconFor(f.lang) + '</span>' +
          '<span class="lib-item-main"><span class="lib-item-name">' + E(f.name) + '</span>' +
          '<span class="lib-item-sub">' + f.lines + ' 行 · ' + fmtSize(f.size) + '</span></span>' +
          (f.stage === null || f.stage === undefined ? "" : '<span class="lib-stage" title="对应学习阶段">S' + f.stage + '</span>') +
          '</button>';
      });
      html += '</div>';
    });
    if (!hit) html += '<div class="lib-empty">没有匹配的文件，换个关键词试试。</div>';
    box.innerHTML = html;
  }

  function renderViewer(f) {
    const box = Q("#libViewer");
    if (!box) return;
    if (!f) {
      box.innerHTML = '<div class="lib-placeholder"><div class="ph-title">从左边选一个文件</div>' +
        '<p>文档、课程代码、Notebook 和日志内容都已经打包进网页，点开就能读，不用去文件夹里翻。</p>' +
        '<p>搜索框可以按<b>文件名或文件内容</b>检索；每个文件都能复制全文、下载，或跳到它对应的学习阶段。</p></div>';
      return;
    }
    const lines = f.content.split("\n");
    const body = lines.map((line, i) =>
      '<div class="cl"><span class="ln">' + (i + 1) + '</span><span class="ct">' + E(line) + '</span></div>'
    ).join("");
    const stageBtn = (f.stage === null || f.stage === undefined) ? "" :
      '<button class="btn small" data-jump-stage="' + f.stage + '">看对应阶段 S' + f.stage + '</button>';
    box.innerHTML =
      '<div class="viewer-head"><div class="viewer-title"><span class="lib-icon">' + iconFor(f.lang) + '</span>' +
      '<div><div class="mono">' + E(f.path) + '</div><div class="viewer-sub">' + E(f.lang) + ' · ' + f.lines + ' 行 · ' + fmtSize(f.size) + '</div></div></div>' +
      '<div class="viewer-actions">' +
      '<button class="btn small" data-copy-file="' + E(f.path) + '">复制全文</button>' +
      '<button class="btn small" data-download-file="' + E(f.path) + '">下载</button>' + stageBtn +
      '<a class="btn small" href="' + E(fileUrl(f.path)) + '" target="_blank" rel="noopener" title="双击本地 index.html 打开时可用；在线预览可能被浏览器拦截">系统打开</a>' +
      '</div></div>' +
      '<div class="code-view">' + body + '</div>' +
      '<div class="viewer-foot">内容来自 ' + E(fileUrl(f.path)) + ' · 若本地文件已修改，重跑 <b>python build_library.py</b> 同步</div>';
  }

  function renderLinks() {
    const box = Q("#libLinks");
    if (!box || !LINKS.length) return;
    box.innerHTML = '<div class="links-title">延伸阅读 · 官方文档与经典论文</div><div class="links-grid">' +
      LINKS.map((l) => '<a class="link-card" href="' + E(l.url) + '" target="_blank" rel="noopener">' +
        '<span class="link-title">' + E(l.title) + ' ↗</span><span class="link-note">' + E(l.note) + '</span></a>').join("") +
      '</div><div class="links-foot">本地资料（README / 学习路线 / 课程代码）在上面的文件树里，离线也能读；外链需要联网。</div>';
  }

  function openFile(path, switchToView) {
    const f = FILES.find((x) => x.path === path);
    if (!f) { notify("没有找到文件：" + path); return; }
    currentPath = path;
    if (switchToView) { try { switchView("library"); } catch (e) {} }
    renderTree(); renderViewer(f);
    const viewer = Q("#libViewer");
    if (viewer) viewer.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }

  /* ---------------- 练习台 ---------------- */

  function templateFor(id) {
    const s = STAGES[id];
    if (!s) return "";
    const todo = s.tasks.map((t, i) => "#   " + (i + 1) + ". " + t).join("\n");
    return "# AI Agent 学习练习 · 阶段 " + s.id + "：" + s.title + "\n" +
      "# 目标：" + s.goal + "\n" +
      "# 周次：" + s.weeks + "\n#\n" +
      "# 本阶段动手任务：\n" + todo + "\n#\n" +
      "# 参考文件：" + s.files.join(" / ") + "\n" +
      "# 运行：在项目根目录执行 " + s.cmds[0] + "\n" +
      "# 建议：先读懂 examples，再关掉它自己写一遍。\n\n" +
      "from pathlib import Path\n\n\n" +
      "def main():\n" +
      "    \"\"\"在这里写下你的练习代码或笔记。\"\"\"\n" +
      "    print(\"阶段 " + s.id + "：" + s.title + "\")\n\n\n" +
      "if __name__ == \"__main__\":\n    main()\n";
  }

  function updateCount() {
    const el = Q("#pgEditor");
    const out = Q("#pgCount");
    if (!el || !out) return;
    const text = el.value;
    out.textContent = (text ? text.split("\n").length : 0) + " 行 · " + text.length + " 字符";
  }
  function setStatus(msg) {
    const el = Q("#pgStatus");
    if (el) el.textContent = msg;
  }
  function loadDraft(id) {
    const el = Q("#pgEditor");
    if (!el) return;
    el.value = drafts[id] || "";
    updateCount();
    setStatus(drafts[id] ? "已载入本机草稿" : "空白，可点「载入练习模板」开始");
  }

  function renderPlayground() {
    const sel = Q("#pgStage");
    if (!sel) return;
    sel.innerHTML = STAGES.map((s) => '<option value="' + s.id + '">阶段 ' + s.id + ' · ' + E(s.title) + '</option>').join("");
    sel.value = String(draftStage);
    loadDraft(draftStage);
  }

  /* ---------------- 先读这里（零基础白话讲解） ---------------- */

  function renderBeginner() {
    const B = window.BEGINNER || { sections: [] };
    const nav = Q("#bgNav"), box = Q("#bgContent");
    if (!nav || !box) return;
    nav.innerHTML = '<div class="bg-nav-t">目录 · 点标题跳到该节</div>' +
      B.sections.map((s, i) => '<button data-bg-nav="' + E(s.id) + '"' +
        (i === 0 ? ' class="active"' : '') + '>' + E(s.nav) + '</button>').join("");
    box.innerHTML = B.sections.map((s) =>
      '<section class="bg-sec" id="bg-' + E(s.id) + '"><h2>' + E(s.title) + '</h2>' + s.html + '</section>'
    ).join("");
  }

  function gotoSection(id) {
    const el = Q("#bg-" + id);
    if (el && el.scrollIntoView) el.scrollIntoView({ behavior: "smooth", block: "start" });
    document.querySelectorAll("#bgNav button").forEach((b) =>
      b.classList.toggle("active", b.dataset.bgNav === id));
  }

  /* ---------------- 事件 ---------------- */

  document.addEventListener("click", async (e) => {
    const t = e.target;

    const bgNav = t.closest("[data-bg-nav]");
    if (bgNav) { gotoSection(bgNav.dataset.bgNav); return; }

    const bgStage = t.closest("[data-beginner-stage]");
    if (bgStage) {
      try { selectStage(Number(bgStage.dataset.beginnerStage), true); }
      catch (err) { notify("请先打开「学习路线」"); }
      return;
    }

    const bgGo = t.closest("[data-beginner-go]");
    if (bgGo) {
      const dest = bgGo.dataset.beginnerGo;
      try { switchView(dest); } catch (err) {}
      if (dest === "beginner") gotoSection("what");
      return;
    }

    const item = t.closest("[data-file]");
    if (item) { openFile(item.dataset.file, false); return; }

    const openBtn = t.closest("[data-open-file]");
    if (openBtn) { openFile(openBtn.dataset.openFile, true); return; }

    const jump = t.closest("[data-jump-stage]");
    if (jump) {
      try { selectStage(Number(jump.dataset.jumpStage), true); } catch (err) { notify("请先在「学习路线」里查看该阶段"); }
      return;
    }

    const cpFile = t.closest("[data-copy-file]");
    if (cpFile) {
      const f = FILES.find((x) => x.path === cpFile.dataset.copyFile);
      notify(await copyText(f ? f.content : "") ? "已复制全文" : "复制失败，请手动选中");
      return;
    }
    const dlFile = t.closest("[data-download-file]");
    if (dlFile) {
      const f = FILES.find((x) => x.path === dlFile.dataset.downloadFile);
      if (f) notify(download(f.name, f.content) ? "已下载 " + f.name : "下载失败");
      return;
    }

    if (t.closest("#pgTemplate")) {
      const el = Q("#pgEditor");
      if (el) {
        el.value = templateFor(draftStage);
        drafts[draftStage] = el.value; saveDrafts(); updateCount(); setStatus("已载入模板 · 已保存到本机");
        notify("已载入阶段 " + draftStage + " 的练习模板");
      }
      return;
    }
    if (t.closest("#pgImport")) { const inp = Q("#pgFile"); if (inp) inp.click(); return; }
    if (t.closest("#pgCopy")) {
      const el = Q("#pgEditor");
      notify(await copyText(el ? el.value : "") ? "已复制编辑内容" : "复制失败");
      return;
    }
    if (t.closest("#pgDownloadPy") || t.closest("#pgDownloadMd")) {
      const el = Q("#pgEditor");
      const isMd = !!t.closest("#pgDownloadMd");
      const ext = isMd ? "md" : "py";
      const name = "agent-lab-stage-" + draftStage + "." + ext;
      notify(download(name, el ? el.value : "") ? "已下载 " + name : "下载失败");
      return;
    }
    if (t.closest("#pgClear")) {
      if (confirm("清空当前阶段的草稿？此操作不可撤销。")) {
        const el = Q("#pgEditor");
        if (el) { el.value = ""; delete drafts[draftStage]; saveDrafts(); updateCount(); setStatus("已清空"); }
      }
      return;
    }
  });

  document.addEventListener("input", (e) => {
    const el = e.target;
    if (el.id === "libSearch") {
      filterText = el.value;
      renderTree();
      const again = Q("#libSearch");
      if (again) { again.focus(); again.setSelectionRange(again.value.length, again.value.length); }
      return;
    }
    if (el.id === "pgEditor") {
      drafts[draftStage] = el.value;
      updateCount();
      setStatus("正在输入…");
      clearTimeout(saveTimer);
      saveTimer = setTimeout(() => { saveDrafts(); setStatus("已自动保存到本机"); }, 500);
    }
  });

  document.addEventListener("change", (e) => {
    const el = e.target;
    if (el.id === "pgStage") {
      const elEditor = Q("#pgEditor");
      if (elEditor) { drafts[draftStage] = elEditor.value; saveDrafts(); }
      draftStage = Number(el.value) || 0;
      loadDraft(draftStage);
      return;
    }
    if (el.id === "pgFile" && el.files && el.files[0]) {
      const file = el.files[0];
      const reader = new FileReader();
      reader.onload = (ev) => {
        const ed = Q("#pgEditor");
        if (ed) {
          ed.value = String(ev.target.result || "");
          drafts[draftStage] = ed.value; saveDrafts(); updateCount();
          setStatus("已导入 " + file.name + " · 已保存");
          notify("已导入 " + file.name + "，可以直接编辑");
        }
      };
      reader.readAsText(file, "utf-8");
      el.value = "";
    }
  });

  /* ---------------- 初始化 ---------------- */

  renderTree();
  renderLinks();
  renderPlayground();
  renderBeginner();
  if (FILES.length) openFile(FILES[0].path, false);
  else renderViewer(null);
})();
