// Load CodeMirror 6 directly as ES modules. This avoids a missing dist/app.js
// build artifact being able to leave the entire desktop window blank.
// If the CDN is unavailable, LocalCode falls back to a functional textarea.
let cm = null;
const cmReady = (async () => {
  try {
    const imports = Promise.all([
      import("https://esm.sh/codemirror@6.0.2"),
      import("https://esm.sh/@codemirror/view@6"),
      import("https://esm.sh/@codemirror/language@6"),
      import("https://esm.sh/@codemirror/commands@6"),
      import("https://esm.sh/@codemirror/lang-python@6"),
      import("https://esm.sh/@codemirror/lang-cpp@6"),
      import("https://esm.sh/@codemirror/lang-javascript@6"),
      import("https://esm.sh/@codemirror/theme-one-dark@6")
    ]);
    const timeout = new Promise((_, reject) => setTimeout(() => reject(new Error("CodeMirror download timed out")), 12000));
    const [core, view, language, commands, pyLang, cppLang, jsLang, theme] = await Promise.race([imports, timeout]);
    cm = {
      basicSetup: core.basicSetup, EditorView: core.EditorView,
      keymap: view.keymap, indentUnit: language.indentUnit,
      indentOnInput: language.indentOnInput, indentWithTab: commands.indentWithTab,
      python: pyLang.python, cpp: cppLang.cpp, javascript: jsLang.javascript,
      oneDark: theme.oneDark
    };
  } catch (error) {
    console.warn("CodeMirror 6 could not be loaded; using the built-in editor fallback.", error);
  }
})();

let editor = null;
let selectedProblem = 0;
let selectedLanguage = "python";
let currentMeta = null;
let saveTimer = null;

const $ = (id) => document.getElementById(id);
function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, ch => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[ch]);
}

async function markdownToHtml(md, problemIndex) {
  const lines = String(md || "").replace(/\r\n?/g, "\n").split("\n");
  const blocks = [];
  let paragraph = [], code = [], inCode = false, codeLang = "", listType = null;

  const flushParagraph = async () => {
    if (paragraph.length) {
      blocks.push(`<p>${await renderInline(paragraph.join(" "), problemIndex)}</p>`);
      paragraph = [];
    }
  };
  const closeList = () => {
    if (listType) { blocks.push(`</${listType}>`); listType = null; }
  };

  for (const line of lines) {
    const fence = line.match(/^\s*```\s*([\w+-]*)\s*$/);
    if (fence) {
      if (!inCode) {
        await flushParagraph(); closeList();
        inCode = true; code = []; codeLang = fence[1];
      } else {
        blocks.push(`<pre><code class="language-${escapeHtml(codeLang)}">${escapeHtml(code.join("\n"))}</code></pre>`);
        inCode = false; code = []; codeLang = "";
      }
      continue;
    }
    if (inCode) { code.push(line); continue; }
    if (!line.trim()) { await flushParagraph(); closeList(); continue; }
    if (/^\s*(---+|___+|\*\*\*+)\s*$/.test(line)) { await flushParagraph(); closeList(); blocks.push("<hr>"); continue; }
    const heading = line.match(/^\s*(#{1,6})\s+(.+?)\s*#*\s*$/);
    if (heading) {
      await flushParagraph(); closeList();
      const level = heading[1].length;
      blocks.push(`<h${level}>${await renderInline(heading[2], problemIndex)}</h${level}>`);
      continue;
    }
    const quote = line.match(/^\s*>\s?(.*)$/);
    if (quote) { await flushParagraph(); closeList(); blocks.push(`<blockquote>${await renderInline(quote[1], problemIndex)}</blockquote>`); continue; }
    const unordered = line.match(/^\s*[-*+]\s+(.+)$/);
    const ordered = line.match(/^\s*\d+[.)]\s+(.+)$/);
    if (unordered || ordered) {
      await flushParagraph();
      const wanted = unordered ? "ul" : "ol";
      if (listType !== wanted) { closeList(); listType = wanted; blocks.push(`<${wanted}>`); }
      blocks.push(`<li>${await renderInline((unordered || ordered)[1], problemIndex)}</li>`);
      continue;
    }
    closeList();
    paragraph.push(line.trim());
  }
  await flushParagraph(); closeList();
  if (inCode) blocks.push(`<pre><code>${escapeHtml(code.join("\n"))}</code></pre>`);
  return blocks.join("\n");
}

async function renderInline(source, problemIndex) {
  // Only emit tags created here. Raw HTML in problem.md is escaped by default.
  const tokenPattern = /(!\[([^\]]*)\]\(([^)]+)\)|\[([^\]]+)\]\(([^)]+)\)|`([^`]+)`|\*\*(.+?)\*\*|\*(.+?)\*)/g;
  let html = "", last = 0, match;
  while ((match = tokenPattern.exec(source)) !== null) {
    html += escapeHtml(source.slice(last, match.index));
    if (match[1]?.startsWith("![")) {
      const alt = match[2] || "Problem illustration";
      const target = match[3].trim();
      let src = "";
      if (/^https?:\/\//i.test(target)) {
        src = target;
      } else if (!/^(?:data|javascript|file):/i.test(target) && !target.startsWith("//")) {
        const resolved = await window.pywebview.api.resolve_image(problemIndex, target);
        if (resolved?.ok) src = resolved.src;
      }
      if (src) {
        const safeSrc = escapeHtml(src);
        html += `<figure class="md-image"><img src="${safeSrc}" alt="${escapeHtml(alt)}" loading="lazy" data-preview-image="1"><figcaption>${escapeHtml(alt)}</figcaption></figure>`;
      } else {
        html += `<div class="md-image-missing">Image unavailable: ${escapeHtml(alt)} (${escapeHtml(target)})</div>`;
      }
    } else if (match[4]) {
      const label = match[4], target = match[5].trim();
      if (/^https?:\/\//i.test(target)) html += `<a href="${escapeHtml(target)}" target="_blank" rel="noopener noreferrer">${escapeHtml(label)}</a>`;
      else html += escapeHtml(label);
    } else if (match[6]) html += `<code>${escapeHtml(match[6])}</code>`;
    else if (match[7]) html += `<strong>${escapeHtml(match[7])}</strong>`;
    else if (match[8]) html += `<em>${escapeHtml(match[8])}</em>`;
    last = tokenPattern.lastIndex;
  }
  html += escapeHtml(source.slice(last));
  return html;
}

function wireImagePreviews() {
  document.querySelectorAll("#statement img[data-preview-image]").forEach(img => {
    img.addEventListener("click", () => {
      const modal = $("imagePreview");
      const preview = $("imagePreviewImg");
      preview.src = img.src;
      preview.alt = img.alt || "Image preview";
      modal.classList.add("open");
      modal.setAttribute("aria-hidden", "false");
    });
    img.addEventListener("error", () => {
      const fallback = document.createElement("div");
      fallback.className = "md-image-missing";
      fallback.textContent = `Could not load image: ${img.alt || img.src}`;
      img.closest("figure")?.replaceWith(fallback);
    }, { once: true });
  });
}

function closeImagePreview() {
  const modal = $("imagePreview");
  modal.classList.remove("open");
  modal.setAttribute("aria-hidden", "true");
  $("imagePreviewImg").src = "";
}

function languageMode(language) {
  return cm[language]();
}

function createFallbackEditor(doc, reason = "") {
  const host = $("editor");
  host.innerHTML = "";
  const area = document.createElement("textarea");
  area.className = "fallback-editor";
  area.setAttribute("aria-label", "Code editor");
  area.spellcheck = false;
  area.value = doc;
  area.addEventListener("input", scheduleSave);
  host.appendChild(area);
  editor = {
    state: { doc: { toString: () => area.value } },
    focus: () => area.focus(),
    destroy: () => area.remove()
  };
  if (reason) showToast(`CodeMirror could not initialize; using the built-in editor. ${reason}`, true);
  editor.focus();
}

function createEditor(doc, language) {
  if (editor) editor.destroy();
  const host = $("editor");
  host.innerHTML = "";
  if (!cm) {
    createFallbackEditor(doc, "Check your internet connection to enable CodeMirror features.");
    return;
  }
  try {
    editor = new cm.EditorView({
      doc,
      parent: host,
      extensions: [
        cm.basicSetup,
        cm.oneDark,
        languageMode(language),
        cm.indentUnit.of("    "),
        cm.indentOnInput(),
        cm.keymap.of([cm.indentWithTab]),
        cm.EditorView.theme({
          "&": { height: "100%", fontSize: "14px", backgroundColor: "#1e222b" },
          ".cm-scroller": { overflow: "auto", fontFamily: "Consolas, 'Cascadia Code', monospace" },
          ".cm-content": { padding: "14px 0", minHeight: "100%" },
          ".cm-gutters": { backgroundColor: "#1e222b", border: "none" },
          ".cm-activeLineGutter": { backgroundColor: "#2a303b" },
          ".cm-activeLine": { backgroundColor: "#ffffff08" },
          ".cm-tooltip": { zIndex: "20" }
        }, { dark: true }),
        cm.EditorView.updateListener.of(update => {
          if (update.docChanged) scheduleSave();
        })
      ]
    });
    editor.focus();
  } catch (error) {
    console.error("CodeMirror initialization failed:", error);
    createFallbackEditor(doc, error?.message || String(error));
  }
}

function scheduleSave() {
  const problemIndex = selectedProblem;
  const language = selectedLanguage;
  const code = editor ? editor.state.doc.toString() : "";
  clearTimeout(saveTimer);
  saveTimer = setTimeout(async () => {
    await window.pywebview.api.save_draft(problemIndex, language, code);
  }, 350);
}

async function loadProblem(index, keepLanguage = true) {
  try {
    selectedProblem = Number(index);
    const language = keepLanguage ? selectedLanguage : $("language").value;
    const data = await window.pywebview.api.get_problem(selectedProblem, language);
    if (!data || !data.ok) { showToast(data?.error || "Could not load this problem.", true); return; }
    currentMeta = data;
    $("problemTitle").textContent = `${data.id}. ${data.title}`;
    $("difficulty").textContent = data.difficulty || "";
    $("difficulty").className = `difficulty ${(data.difficulty || "").toLowerCase()}`;
    $("statement").innerHTML = await markdownToHtml(data.statement, selectedProblem);
    wireImagePreviews();
    $("caseCount").textContent = `Run: ${data.run_test_count} sample · Submit: ${data.total_count} total tests`;
    createEditor(data.code || "", language);
    clearResults();
  } catch (error) {
    showToast(`Problem loading failed: ${error?.message || error}`, true);
  }
}

async function loadProblemList() {
  try {
    const data = await window.pywebview.api.list_problems();
    const select = $("problemSelect");
    select.innerHTML = "";
    (data.problems || []).forEach((p) => {
      const option = document.createElement("option");
      option.value = p.index;
      option.textContent = `${p.id}. ${p.title}`;
      select.appendChild(option);
    });
    if (!data.problems?.length) {
      $("problemTitle").textContent = "No problems found";
      $("statement").innerHTML = "<p>Add problem folders containing <code>problem.md</code> and <code>tests.json</code> inside the <code>problems</code> directory.</p>";
      showToast((data.warnings || []).join("\n") || "No valid problem folders found", true);
      return;
    }
    if (data.warnings?.length) showToast(data.warnings.join("\n"), true);
    await loadProblem(0);
  } catch (error) {
    showToast(`Could not connect to LocalCode backend: ${error?.message || error}`, true);
  }
}

function clearResults() {
  $("verdict").textContent = "Ready";
  $("verdict").className = "verdict neutral";
  $("resultMeta").textContent = "Run your code to see test results.";
  $("resultsBody").innerHTML = "<tr><td colspan='5' class='empty'>No test results yet</td></tr>";
  $("detail").textContent = "Select a test case to inspect its details.";
}

function formatValue(value) {
  if (typeof value === "string") return value.length > 100 ? value.slice(0, 97) + "…" : value;
  return JSON.stringify(value);
}

function showToast(message, isError = false) {
  const toast = $("toast");
  toast.textContent = message;
  toast.className = `toast show ${isError ? "error" : ""}`;
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => toast.className = "toast", 4200);
}

function showDetail(row) {
  const lines = [
    `Input:    ${JSON.stringify(row.input)}`,
    `Expected: ${JSON.stringify(row.expected)}`,
    `Actual:   ${JSON.stringify(row.actual)}`,
    `Time:     ${row.ms} ms`
  ];
  if (row.stdout) lines.push("", "Standard output:", row.stdout);
  if (row.error) lines.push("", "Error:", row.error);
  $("detail").textContent = lines.join("\n");
}

async function runCode(submit) {
  if (!editor || !currentMeta) return;
  const runBtn = $("runBtn"), submitBtn = $("submitBtn");
  runBtn.disabled = submitBtn.disabled = true;
  $("verdict").textContent = submit ? "Submitting all tests…" : "Running sample tests…";
  $("verdict").className = "verdict neutral";
  $("resultMeta").textContent = "Executing your solution…";
  $("resultsBody").innerHTML = "<tr><td colspan='5' class='empty'>Running test cases…</td></tr>";
  try {
    const response = await window.pywebview.api.run_solution(
      selectedProblem, selectedLanguage, editor.state.doc.toString(), submit
    );
    if (!response.ok) {
      $("verdict").textContent = "Execution Error";
      $("verdict").className = "verdict bad";
      $("resultsBody").innerHTML = `<tr><td colspan='5' class='empty error-text'>${escapeHtml(response.error)}</td></tr>`;
      $("detail").textContent = response.error;
      return;
    }
    $("verdict").textContent = response.verdict;
    $("verdict").className = `verdict ${response.verdict === "Accepted" ? "good" : "bad"}`;
    const scopeLabel = response.test_mode === "all" ? "total tests" : "sample tests";
    $("resultMeta").textContent = `${response.passed}/${response.total} ${scopeLabel} passed · ${response.ms ?? 0} ms`;
    const body = $("resultsBody");
    body.innerHTML = "";
    response.results.forEach((row, index) => {
      const tr = document.createElement("tr");
      tr.className = row.status === "Passed" ? "passed" : "failed";
      tr.innerHTML = `<td>${row.case}</td><td><span class='status ${row.status === "Passed" ? "good" : "bad"}'>${escapeHtml(row.status)}</span></td><td title='${escapeHtml(JSON.stringify(row.input))}'>${escapeHtml(formatValue(row.input))}</td><td title='${escapeHtml(JSON.stringify(row.expected))}'>${escapeHtml(formatValue(row.expected))}</td><td title='${escapeHtml(JSON.stringify(row.actual))}'>${escapeHtml(formatValue(row.actual))}</td>`;
      tr.addEventListener("click", () => {
        document.querySelectorAll("#resultsBody tr").forEach(el => el.classList.remove("selected"));
        tr.classList.add("selected"); showDetail(row);
      });
      body.appendChild(tr);
      if (index === 0) { tr.classList.add("selected"); showDetail(row); }
    });
    if (!response.results.length) $("detail").textContent = response.verdict;
  } catch (error) {
    showToast(String(error), true);
  } finally {
    runBtn.disabled = submitBtn.disabled = false;
  }
}

let appInitialized = false;
async function initializeLocalCode() {
  if (appInitialized) return;
  if (!window.pywebview || !window.pywebview.api) return;
  appInitialized = true;
  // Wire the UI and load the selected problem immediately. Do not wait for
  // the optional CodeMirror CDN imports: a slow/offline network must never
  // leave the problem statement and starter code blank.
  $("problemSelect").addEventListener("change", e => loadProblem(e.target.value));
  $("language").addEventListener("change", async e => {
    try {
      if (editor) await window.pywebview.api.save_draft(selectedProblem, selectedLanguage, editor.state.doc.toString());
      selectedLanguage = e.target.value;
      await loadProblem(selectedProblem);
    } catch (error) { showToast(`Language change failed: ${error?.message || error}`, true); }
  });
  $("runBtn").addEventListener("click", () => runCode(false));
  $("submitBtn").addEventListener("click", () => runCode(true));
  $("refreshBtn").addEventListener("click", loadProblemList);
  $("imagePreviewClose").addEventListener("click", closeImagePreview);
  $("imagePreview").addEventListener("click", e => { if (e.target === $("imagePreview")) closeImagePreview(); });
  document.addEventListener("keydown", e => { if (e.key === "Escape") closeImagePreview(); });
  $("openFolderBtn").addEventListener("click", async () => {
    try {
      const result = await window.pywebview.api.open_problems_folder();
      if (!result.ok) showToast(result.error, true);
    } catch (error) { showToast(`Could not open problems folder: ${error?.message || error}`, true); }
  });
  document.addEventListener("keydown", e => {
    if ((e.ctrlKey || e.metaKey) && !e.shiftKey && e.key === "Enter") { e.preventDefault(); runCode(false); }
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === "Enter") { e.preventDefault(); runCode(true); }
  });
  await loadProblemList();

  // If CM6 finishes loading after the fallback textarea has been displayed,
  // upgrade the editor in-place while preserving the user's current code.
  await cmReady;
  if (cm && editor && currentMeta) {
    const currentCode = editor.state.doc.toString();
    createEditor(currentCode, selectedLanguage);
  }
}

window.addEventListener("pywebviewready", initializeLocalCode);
// Fallback for WebView2 builds where the bridge becomes available before this bundle runs.
const bridgeCheck = window.setInterval(() => {
  if (window.pywebview?.api) {
    window.clearInterval(bridgeCheck);
    initializeLocalCode();
  }
}, 100);
window.addEventListener("error", event => showToast(`Editor error: ${event.message}`, true));
window.addEventListener("unhandledrejection", event => showToast(`Application error: ${event.reason?.message || event.reason}`, true));
