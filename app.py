"""LocalCode - offline LeetCode-style practice app for Windows. Languages: Python, C++, JavaScript."""
import json, os, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

ROOT = os.path.dirname(sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__))
PY = shutil.which("python") or shutil.which("py") or sys.executable
BG, PANEL, FG, MUTED = "#1e1e1e", "#252526", "#d4d4d4", "#8b8b8b"
GREEN, RED, ORANGE, BLUE = "#2cbb5d", "#ef4743", "#ffa116", "#569cd6"
DIFF = {"Easy": GREEN, "Medium": ORANGE, "Hard": RED}
LANGS = {"python": ("Python", "starter.py", "py"), "cpp": ("C++", "starter.cpp", "cpp"), "javascript": ("JavaScript", "starter.js", "js")}
LKEYS = list(LANGS)
DEFAULT = {"python": "class Solution:\n    pass\n", "cpp": "#include <bits/stdc++.h>\nusing namespace std;\n\nclass Solution {\npublic:\n};\n", "javascript": "class Solution {\n}\n"}
KEYWORDS = (r"\b(class|def|return|if|elif|else|for|while|in|not|and|or|import|from|as|None|True|False|self|pass|break|continue|lambda|try|except|with|"
            r"int|long|double|bool|string|vector|void|auto|const|public|private|using|namespace|include|static|new|this|let|var|function|true|false|null|undefined)\b")

PY_RUNNER = r'''
import json, sys, io, traceback, time, copy
P = json.load(open("payload.json"))
out = {"results": []}
def save(): json.dump(out, open("out.json", "w"), default=str)
try:
    ns = {}
    pre = "from typing import *\nfrom collections import *\nimport math, heapq, itertools, functools, bisect\n"
    exec(compile(pre + open("sol.py", encoding="utf8").read(), "solution", "exec"), ns)
    fn = getattr(ns["Solution"](), P["method"])
except BaseException:
    out["error"] = traceback.format_exc(); save(); sys.exit()
for t in P["tests"]:
    r, buf, old = {}, io.StringIO(), sys.stdout
    sys.stdout = buf; t0 = time.time()
    try:
        value = fn(**copy.deepcopy(t["input"]))
        r["actual"] = buf.getvalue() if P.get("output_mode") == "stdout" else value
    except BaseException:
        r["error"] = traceback.format_exc()
    finally:
        sys.stdout = old
    r["stdout"] = buf.getvalue(); r["ms"] = round((time.time() - t0) * 1000, 2)
    out["results"].append(r)
save()
'''

JS_RUNNER = r'''
const fs = require("fs"), P = JSON.parse(fs.readFileSync("payload.json", "utf8"));
const out = { results: [] }; const save = () => fs.writeFileSync("out.json", JSON.stringify(out));
let S;
try { S = new Function(fs.readFileSync("sol.js", "utf8") + "\nreturn Solution;")(); }
catch (e) { out.error = String(e.stack || e); save(); process.exit(); }
for (const t of P.tests) {
  const logs = [], ol = console.log, r = {}; console.log = (...a) => logs.push(a.join(" "));
  const t0 = Date.now();
  try {
    const v = new S()[P.method](...Object.values(JSON.parse(JSON.stringify(t.input))));
    r.actual = P.output_mode === "stdout" ? (logs.length ? logs.join("\n") + "\n" : "") : (v === undefined ? null : v);
  } catch (e) { r.error = String(e.stack || e); }
  console.log = ol; r.stdout = logs.join("\n"); r.ms = Date.now() - t0; out.results.push(r);
}
save();
'''

CPP_HELP = r'''
#include <bits/stdc++.h>
using namespace std;
static void ws(istream&i){while(isspace(i.peek()))i.get();}
static void rd(istream&i,int&x){i>>x;}
static void rd(istream&i,long long&x){i>>x;}
static void rd(istream&i,double&x){i>>x;}
static void rd(istream&i,bool&x){ws(i);string s;while(isalpha(i.peek()))s+=(char)i.get();x=(s=="true");}
static void rd(istream&i,string&s){ws(i);i.get();s.clear();char c;while((c=i.get())!='"'){if(c=='\\')c=i.get();s+=c;}}
template<class T>static void rd(istream&i,vector<T>&v){ws(i);i.get();v.clear();for(;;){ws(i);if(i.peek()==']'){i.get();break;}T e;rd(i,e);v.push_back(e);ws(i);if(i.peek()==',')i.get();}}
static void pr(ostream&o,int x){o<<x;}
static void pr(ostream&o,long long x){o<<x;}
static void pr(ostream&o,double x){o<<setprecision(12)<<x;}
static void pr(ostream&o,bool x){o<<(x?"true":"false");}
static void pr(ostream&o,const string&s){
    o<<'"';
    for(unsigned char c:s){
        if(c=='"' || c=='\\') { o<<'\\' << (char)c; }
        else if(c=='\n') o<<"\\n";
        else if(c=='\r') o<<"\\r";
        else if(c=='\t') o<<"\\t";
        else if(c<0x20) { const char* h="0123456789abcdef"; o<<"\\u00"<<h[c>>4]<<h[c&15]; }
        else o<<(char)c;
    }
    o<<'"';
}
template<class T>static void pr(ostream&o,const vector<T>&v){o<<'[';for(size_t k=0;k<v.size();k++){if(k)o<<',';pr(o,v[k]);}o<<']';}
'''


def ctype(t):
    if t.endswith("[]"): return f"vector<{ctype(t[:-2])}>"
    return {"int": "int", "long": "long long", "double": "double", "bool": "bool", "string": "string"}[t]


def windows_compiler_env():
    """Ensure MSYS2 UCRT64 runtime DLLs are visible to compiler child processes."""
    env = os.environ.copy()
    if os.name == "nt":
        extra_dirs = [
            r"C:\msys64\ucrt64\bin",
            r"C:\msys64\usr\bin",
        ]
        current = env.get("PATH", "")
        env["PATH"] = os.pathsep.join(
            [p for p in extra_dirs if os.path.isdir(p)] + [current]
        )
    return env


def find_cpp_compiler():
    """Find GCC on PATH or in the standard MSYS2 UCRT64 installation."""
    compiler = shutil.which("g++") or shutil.which("g++.exe")
    if compiler:
        return compiler
    if os.name == "nt":
        candidates = [
            Path(r"C:\msys64\ucrt64\bin\g++.exe"),
            Path(r"C:\msys64\mingw64\bin\g++.exe"),
            Path(r"C:\mingw64\bin\g++.exe"),
        ]
        for candidate in candidates:
            if candidate.is_file():
                return str(candidate)
    return None


def run_proc(cmd, cwd, timeout, stdin=None):
    return subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, input=stdin,
        timeout=timeout, env=windows_compiler_env()
    )


def judge(lang, code, m, tests):
    """Runs `code` against `tests`. Returns {"results": [...]} | {"error": str} | {"tle": True}."""
    tl = m.get("timeout", 10)
    with tempfile.TemporaryDirectory() as tmp:
        w = lambda n, s: Path(tmp, n).write_text(s, encoding="utf8")
        try:
            if lang == "cpp":
                gxx = find_cpp_compiler()
                if not gxx:
                    return {"error": (
                        "g++ was not found. Install MSYS2 UCRT64 GCC, then add "
                        r"C:\msys64\ucrt64\bin" + " to Windows PATH.\n"
                        "You can also verify GCC from MSYS2 UCRT64 with: g++ --version"
                    )}
                if "types" not in m: return {"error": 'tests.json needs a "types" map (e.g. {"nums": "int[]"}) and "returns" for C++.'}
                keys = list(tests[0]["input"])
                decl = "".join(f"  {ctype(m['types'][k])} a{i}; rd(cin,a{i});\n" for i, k in enumerate(keys))
                call = ",".join(f"a{i}" for i in range(len(keys)))
                if m.get("output_mode") == "stdout":
                    main = (
                        f'int main(){{\n{decl}'
                        f'  ostringstream captured; streambuf* old = cout.rdbuf(captured.rdbuf());\n'
                        f'  Solution().{m["method"]}({call});\n'
                        f'  cout.rdbuf(old);\n'
                        f'  ofstream f("result.json"); pr(f,captured.str());\n'
                        f'}}\n'
                    )
                else:
                    main = f'int main(){{\n{decl}  auto r = Solution().{m["method"]}({call});\n  ofstream f("result.json"); pr(f,r);\n}}\n'
                w("main.cpp", code + "\n" + CPP_HELP + main)
                c = run_proc([gxx, "-O2", "-std=c++17", "main.cpp", "-o", "main.exe"], tmp, 120)
                if c.returncode: return {"error": c.stderr}
                res, rp = [], os.path.join(tmp, "result.json")
                for t in tests:
                    inp = "\n".join(json.dumps(v, separators=(",", ":")) for v in t["input"].values())
                    if os.path.exists(rp): os.remove(rp)
                    r, t0 = {}, time.time()
                    try:
                        p = run_proc([os.path.join(tmp, "main.exe")], tmp, tl, inp)
                        r["stdout"] = p.stdout
                        if p.returncode: r["error"] = f"Runtime error (exit code {p.returncode})\n{p.stderr}"
                        else: r["actual"] = json.loads(Path(rp).read_text())
                    except subprocess.TimeoutExpired: r["error"] = "Time Limit Exceeded"
                    except Exception as e: r["error"] = str(e)
                    r["ms"] = round((time.time() - t0) * 1000, 2); res.append(r)
                return {"results": res}
            if lang == "python": exe, name, runner, rn = PY, "sol.py", PY_RUNNER, "runner.py"
            else:
                exe = shutil.which("node")
                if not exe: return {"error": "Node.js not found. Install it from nodejs.org and restart LocalCode."}
                name, runner, rn = "sol.js", JS_RUNNER, "runner.js"
            w(name, code); w(rn, runner); w("payload.json", json.dumps({"method": m["method"], "tests": tests, "output_mode": m.get("output_mode")}))
            run_proc([exe, rn], tmp, tl)
            return json.loads(Path(tmp, "out.json").read_text(encoding="utf8"))
        except subprocess.TimeoutExpired: return {"tle": True}
        except Exception as e: return {"error": f"Runner failed: {e}"}


def norm(x, unordered):
    return sorted(x, key=lambda v: json.dumps(v, sort_keys=True)) if unordered and isinstance(x, list) else x


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LocalCode"); self.geometry("1300x800"); self.configure(bg=BG)
        self.problems, self.cur, self.drafts, self.shown, self.results = [], None, {}, None, []
        s = ttk.Style(self); s.theme_use("clam")
        s.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=FG, rowheight=24, borderwidth=0)
        s.configure("Treeview.Heading", background="#333", foreground=FG)
        s.map("Treeview", background=[("selected", "#094771")])
        self.build_ui()
        self.load_folder(os.path.join(ROOT, "problems"))

    def btn(self, parent, text, cmd, color):
        return tk.Button(parent, text=text, command=cmd, bg=color, fg="white", relief="flat", padx=16, pady=4,
                         font=("Segoe UI", 10, "bold"), activebackground=color, cursor="hand2")

    def build_ui(self):
        top = tk.Frame(self, bg=PANEL); top.pack(fill="x")
        tk.Label(top, text="LocalCode", bg=PANEL, fg=ORANGE, font=("Segoe UI", 13, "bold")).pack(side="left", padx=12)
        self.combo = ttk.Combobox(top, state="readonly", width=36); self.combo.pack(side="left", pady=6)
        self.combo.bind("<<ComboboxSelected>>", lambda e: self.select(self.combo.current()))
        self.btn(top, "Open Folder", lambda: self.load_folder(filedialog.askdirectory()), "#444").pack(side="left", padx=8)
        self.btn(top, "Submit", lambda: self.run(True), GREEN).pack(side="right", padx=8, pady=4)
        self.btn(top, "Run", lambda: self.run(False), "#555").pack(side="right")
        self.lang = ttk.Combobox(top, state="readonly", width=12, values=[v[0] for v in LANGS.values()]); self.lang.current(0)
        self.lang.pack(side="right", padx=10)
        self.lang.bind("<<ComboboxSelected>>", lambda e: self.load_code())

        main = tk.PanedWindow(self, orient="horizontal", bg=BG, sashwidth=5); main.pack(fill="both", expand=True)
        left = tk.Frame(main, bg=BG); main.add(left, width=560)
        self.head = tk.Label(left, bg=BG, fg=FG, font=("Segoe UI", 16, "bold"), anchor="w"); self.head.pack(fill="x", padx=14, pady=(12, 0))
        self.diff = tk.Label(left, bg=BG, anchor="w", font=("Segoe UI", 10, "bold")); self.diff.pack(fill="x", padx=14)
        self.stmt = tk.Text(left, bg=BG, fg=FG, wrap="word", relief="flat", padx=14, pady=8, font=("Segoe UI", 11), state="disabled", cursor="arrow")
        self.stmt.pack(fill="both", expand=True)
        for tag, cfg in {"h1": dict(font=("Segoe UI", 15, "bold"), spacing1=8), "h2": dict(font=("Segoe UI", 12, "bold"), spacing1=10, foreground=BLUE),
                         "b": dict(font=("Segoe UI", 11, "bold")), "c": dict(font=("Consolas", 10), background="#333"),
                         "blk": dict(font=("Consolas", 10), background=PANEL, lmargin1=16, lmargin2=16)}.items():
            self.stmt.tag_configure(tag, **cfg)

        right = tk.PanedWindow(main, orient="vertical", bg=BG, sashwidth=5); main.add(right)
        self.ed = tk.Text(right, bg=PANEL, fg=FG, insertbackground="white", font=("Consolas", 12), undo=True, relief="flat", padx=8, pady=8, wrap="none")
        right.add(self.ed, height=460)
        self.ed.bind("<Tab>", lambda e: (self.ed.insert("insert", "    "), "break")[1])
        self.ed.bind("<KeyRelease>", lambda e: self.highlight())
        for t, c in {"kw": BLUE, "str": "#ce9178", "com": "#6a9955", "num": "#b5cea8"}.items(): self.ed.tag_configure(t, foreground=c)

        res = tk.Frame(right, bg=BG); right.add(res)
        self.summary = tk.Label(res, bg=BG, fg=MUTED, anchor="w", font=("Segoe UI", 12, "bold")); self.summary.pack(fill="x", padx=10, pady=4)
        cols = ("case", "status", "input", "expected", "actual")
        self.tree = ttk.Treeview(res, columns=cols, show="headings", height=6)
        for c, wd in zip(cols, (50, 90, 220, 120, 120)): self.tree.heading(c, text=c.title()); self.tree.column(c, width=wd)
        self.tree.tag_configure("ok", foreground=GREEN); self.tree.tag_configure("bad", foreground=RED)
        self.tree.pack(fill="x", padx=10); self.tree.bind("<<TreeviewSelect>>", self.show_detail)
        self.detail = tk.Text(res, bg=PANEL, fg=FG, height=6, font=("Consolas", 10), relief="flat", state="disabled")
        self.detail.pack(fill="both", expand=True, padx=10, pady=6)

    def load_folder(self, folder):
        if not folder or not os.path.isdir(folder):
            return
        found, errors = [], []
        for d in sorted(os.listdir(folder)):
            p = os.path.join(folder, d)
            if not os.path.isdir(p):
                continue
            test_file, statement_file = Path(p, "tests.json"), Path(p, "problem.md")
            if not test_file.is_file():
                continue
            if not statement_file.is_file():
                errors.append(f"{d}: missing problem.md")
                continue
            try:
                meta = json.loads(test_file.read_text(encoding="utf8"))
                missing = [key for key in ("id", "title", "method", "tests") if key not in meta]
                if missing:
                    errors.append(f"{d}: tests.json missing {', '.join(missing)}")
                    continue
                if not isinstance(meta["tests"], list) or not meta["tests"]:
                    errors.append(f"{d}: tests must be a non-empty array")
                    continue
                meta["dir"] = p
                found.append(meta)
            except Exception as e:
                errors.append(f"{d}: {e}")
        self.problems = sorted(found, key=lambda m: str(m.get("id", "")))
        self.combo["values"] = [f'{m.get("id")}. {m.get("title")}' for m in self.problems]
        if self.problems:
            self.combo.current(0)
            self.select(0)
        else:
            self.cur = None
            self.head.config(text="No valid problems found")
            self.diff.config(text="")
            self.stmt.config(state="normal")
            self.stmt.delete("1.0", "end")
            self.stmt.insert("1.0", "Add a problem folder containing problem.md and tests.json.")
            self.stmt.config(state="disabled")
        if errors:
            messagebox.showwarning("Some problems were skipped", "\\n".join(errors))

    def select(self, i):
        if not self.problems or i < 0 or i >= len(self.problems):
            return
        self.cur = m = self.problems[i]
        self.head.config(text=f'{m.get("id")}. {m.get("title")}')
        self.diff.config(text=m.get("difficulty", ""), fg=DIFF.get(m.get("difficulty"), FG))
        self.render_md(Path(m["dir"], "problem.md").read_text(encoding="utf8"))
        self.tree.delete(*self.tree.get_children()); self.set_detail("")
        self.summary.config(text="Run or submit your code to see results.", fg=MUTED)
        self.load_code()

    def lang_key(self): return LKEYS[self.lang.current()]

    def load_code(self):
        if self.shown: self.drafts[self.shown] = self.ed.get("1.0", "end-1c")
        lang, m = self.lang_key(), self.cur
        key = self.shown = (m["dir"], lang)
        code = self.drafts.get(key)
        if code is None:
            sf = Path(m["dir"], LANGS[lang][1])
            code = sf.read_text(encoding="utf8") if sf.is_file() else DEFAULT[lang]
        self.ed.delete("1.0", "end"); self.ed.insert("1.0", code); self.ed.edit_reset(); self.highlight()

    def render_md(self, md):
        t = self.stmt; t.config(state="normal"); t.delete("1.0", "end")
        def inline(s):
            for part in re.split(r"(\*\*.+?\*\*|`.+?`)", s):
                if part.startswith("**"): t.insert("end", part[2:-2], "b")
                elif part.startswith("`") and len(part) > 1: t.insert("end", part[1:-1], "c")
                elif part: t.insert("end", part)
        in_code = False
        for line in md.splitlines():
            if line.startswith("```"): in_code = not in_code
            elif in_code: t.insert("end", line + "\n", "blk")
            elif line.startswith("# "): t.insert("end", line[2:] + "\n", "h1")
            elif line.startswith("#"): t.insert("end", line.lstrip("# ") + "\n", "h2")
            elif re.match(r"\s*[-*] ", line): t.insert("end", "  \u2022 "); inline(re.sub(r"^\s*[-*] ", "", line)); t.insert("end", "\n")
            else: inline(line); t.insert("end", "\n")
        t.config(state="disabled")

    def highlight(self):
        for tag in ("kw", "str", "com", "num"): self.ed.tag_remove(tag, "1.0", "end")
        src, com = self.ed.get("1.0", "end-1c"), (r"#[^\n]*" if self.lang_key() == "python" else r"//[^\n]*")
        for tag, pat in (("kw", KEYWORDS), ("num", r"\b\d+\b"), ("str", r"(\"[^\"\n]*\"|'[^'\n]*')"), ("com", com)):
            for mt in re.finditer(pat, src): self.ed.tag_add(tag, f"1.0+{mt.start()}c", f"1.0+{mt.end()}c")

    def run(self, submit):
        if not self.cur:
            messagebox.showinfo("No problem selected", "Select a problem from the problems folder first.")
            return
        m, lang, code = self.cur, self.lang_key(), self.ed.get("1.0", "end-1c")
        Path(m["dir"], "user_solution." + LANGS[lang][2]).write_text(code, encoding="utf8")
        tests = [t for t in m["tests"] if submit or not t.get("hidden")]
        self.tree.delete(*self.tree.get_children()); self.results = []
        self.summary.config(text="Running...", fg=MUTED); self.update_idletasks()
        out = judge(lang, code, m, tests)
        if out.get("tle"): return self.summary.config(text="Time Limit Exceeded", fg=ORANGE)
        if "error" in out:
            self.summary.config(text="Compile / Setup Error", fg=RED); return self.set_detail(out["error"])
        passed, verdict = 0, "Accepted"
        for i, (t, r) in enumerate(zip(tests, out["results"]), 1):
            if "error" in r:
                ok, status = False, ("Time Limit" if "Time Limit" in r["error"] else "Runtime Error"); verdict = "Runtime Error"
            else:
                actual_value, expected_value = r.get("actual"), t.get("expected")
                if m.get("output_mode") == "stdout" and isinstance(actual_value, str) and isinstance(expected_value, str):
                    actual_value, expected_value = actual_value.rstrip("\\r\\n"), expected_value.rstrip("\\r\\n")
                ok = norm(actual_value, m.get("unordered")) == norm(expected_value, m.get("unordered"))
                status = "Passed" if ok else "Wrong Answer"
                if not ok and verdict == "Accepted": verdict = "Wrong Answer"
            passed += ok; self.results.append((t, r))
            inp = ", ".join(f"{k}={json.dumps(v)}" for k, v in t["input"].items())
            self.tree.insert("", "end", iid=str(i - 1), tags=("ok" if ok else "bad",),
                             values=(i, status, inp, json.dumps(t.get("expected")), "-" if "error" in r else json.dumps(r.get("actual"))))
        ms = sum(r["ms"] for r in out["results"])
        self.summary.config(text=f"{verdict}  \u2022  {passed}/{len(tests)} cases passed  \u2022  {ms:.1f} ms", fg=GREEN if verdict == "Accepted" else RED)
        if self.results: self.tree.selection_set("0")

    def show_detail(self, _):
        sel = self.tree.selection()
        if not sel: return
        t, r = self.results[int(sel[0])]
        txt = f"Input:    {json.dumps(t['input'])}\nExpected: {json.dumps(t['expected'])}\nOutput:   {json.dumps(r.get('actual'))}\n"
        if r.get("stdout"): txt += f"\nStdout:\n{r['stdout']}"
        if r.get("error"): txt += f"\n{r['error']}"
        self.set_detail(txt)

    def set_detail(self, txt):
        self.detail.config(state="normal"); self.detail.delete("1.0", "end"); self.detail.insert("1.0", txt); self.detail.config(state="disabled")


if __name__ == "__main__":
    App().mainloop()
