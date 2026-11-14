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
    """Convert tests.json type declarations to C++ types.

    Accepts both the compact legacy form (int[]) and standard C++ forms
    (vector<int>, std::vector<int>, vector<vector<int>>).
    """
    if not isinstance(t, str):
        raise ValueError(f"Invalid C++ input type: {t!r}")

    t = t.strip().replace("std::", "")
    primitive = {
        "int": "int",
        "long": "long long",
        "long long": "long long",
        "double": "double",
        "float": "float",
        "bool": "bool",
        "string": "string",
        "char": "char",
    }
    if t in primitive:
        return primitive[t]

    if t.endswith("[]"):
        return f"vector<{ctype(t[:-2])}>"

    match = re.fullmatch(r"vector\s*<(.+)>", t)
    if match:
        return f"vector<{ctype(match.group(1).strip())}>"

    raise ValueError(
        f"Unsupported C++ input type '{t}' in tests.json. "
        "Use types such as int, string, int[], or vector<int>."
    )


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
                w("main.cpp", CPP_HELP + "\n" + code + "\n" + main)
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


