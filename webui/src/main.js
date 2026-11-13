import { basicSetup, EditorView } from "codemirror";
import { keymap } from "@codemirror/view";
import { indentUnit, indentOnInput } from "@codemirror/language";
import { indentWithTab } from "@codemirror/commands";
import { python } from "@codemirror/lang-python";
import { cpp } from "@codemirror/lang-cpp";
import { javascript } from "@codemirror/lang-javascript";
import { oneDark } from "@codemirror/theme-one-dark";

let editor = null;
let selectedProblem = 0;
let selectedLanguage = "python";
let currentMeta = null;
let saveTimer = null;

const $ = (id) => document.getElementById(id);
const languageExtensions = {
  python: python,
  cpp: cpp,
  javascript: javascript,
};

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, ch => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[ch]);
}

function markdownToHtml(md) {
  const lines = String(md || "").split(/\r?\n/);
  let html = "", inCode = false, code = [];
  for (const line of lines) {
    if (line.trim().startsWith("```")) {
      if (!inCode) { inCode = true; code = []; }
      else { html += `<pre><code>${escapeHtml(code.join("\n"))}</code></pre>`; inCode = false; }
      continue;
    }
    if (inCode) { code.push(line); continue; }
    if (!line.trim()) { html += "<div class='md-gap'></div>"; continue; }
    const inline = escapeHtml(line)
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.+?)\*/g, "<em>$1</em>");
    if (/^###\s/.test(line)) html += `<h3>${inline.replace(/^###\s/, "")}</h3>`;
    else if (/^##\s/.test(line)) html += `<h2>${inline.replace(/^##\s/, "")}</h2>`;
    else if (/^#\s/.test(line)) html += `<h1>${inline.replace(/^#\s/, "")}</h1>`;
    else if (/^\s*[-*]\s/.test(line)) html += `<div class='md-list'>• ${inline.replace(/^\s*[-*]\s/, "")}</div>`;
    else html += `<p>${inline}</p>`;
  }
  if (inCode) html += `<pre><code>${escapeHtml(code.join("\n"))}</code></pre>`;
  return html;
}

function languageMode(language) {
  return languageExtensions[language]();
}

function createEditor(doc, language) {
  if (editor) editor.destroy();
  editor = new EditorView({
    doc,
    parent: $("editor"),
    extensions: [
      basicSetup,
      oneDark,
      languageMode(language),
      indentUnit.of("    "),
      indentOnInput,
      keymap.of([indentWithTab]),
      EditorView.theme({
        "&": { height: "100%", fontSize: "14px", backgroundColor: "#1e222b" },
        ".cm-scroller": { overflow: "auto", fontFamily: "Consolas, 'Cascadia Code', monospace" },
        ".cm-content": { padding: "14px 0", minHeight: "100%" },
        ".cm-gutters": { backgroundColor: "#1e222b", border: "none" },
        ".cm-activeLineGutter": { backgroundColor: "#2a303b" },
        ".cm-activeLine": { backgroundColor: "#ffffff08" },
        ".cm-tooltip": { zIndex: "20" }
      }, { dark: true }),
      EditorView.updateListener.of(update => {
        if (update.docChanged) scheduleSave();
      })
    ]
  });
  editor.focus();
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
    $("statement").innerHTML = markdownToHtml(data.statement);
    $("caseCount").textContent = `${data.visible_count} visible · ${data.total_count} total tests`;
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
  $("verdict").textContent = submit ? "Submitting…" : "Running…";
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
    $("resultMeta").textContent = `${response.passed}/${response.total} cases passed · ${response.ms ?? 0} ms`;
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
