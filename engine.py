"""LocalCode - offline LeetCode-style practice app for Windows. Languages: Python, C++, JavaScript."""
import json, os, re, shutil, subprocess, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor
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
template<class T>static void rd(istream&i,deque<T>&v){vector<T>x;rd(i,x);v.assign(x.begin(),x.end());}
template<class T>static void rd(istream&i,list<T>&v){vector<T>x;rd(i,x);v.assign(x.begin(),x.end());}
template<class T>static void rd(istream&i,set<T>&v){vector<T>x;rd(i,x);v.clear();v.insert(x.begin(),x.end());}
template<class T>static void rd(istream&i,unordered_set<T>&v){vector<T>x;rd(i,x);v.clear();v.insert(x.begin(),x.end());}
static void rd(istream&i,float&x){double d;rd(i,d);x=(float)d;}
static void rd(istream&i,long double&x){double d;rd(i,d);x=d;}
static void rd(istream&i,char&x){ws(i);if(i.peek()=='"'){string s;rd(i,s);x=s.empty()?0:s[0];}else{long long v;rd(i,v);x=(char)v;}}
static void rd(istream&i,signed char&x){long long v;rd(i,v);x=(signed char)v;}
static void rd(istream&i,unsigned char&x){long long v;rd(i,v);x=(unsigned char)v;}
static void rd(istream&i,short&x){long long v;rd(i,v);x=(short)v;}
static void rd(istream&i,unsigned short&x){long long v;rd(i,v);x=(unsigned short)v;}
static void rd(istream&i,unsigned int&x){long long v;rd(i,v);x=(unsigned int)v;}
static void rd(istream&i,unsigned long long&x){long long v;rd(i,v);x=(unsigned long long)v;}
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
template<class C>static void pr_seq(ostream&o,const C&v){o<<'[';bool first=true;for(const auto&e:v){if(!first)o<<',';first=false;pr(o,e);}o<<']';}
template<class T>static void pr(ostream&o,const deque<T>&v){pr_seq(o,v);}
template<class T>static void pr(ostream&o,const list<T>&v){pr_seq(o,v);}
template<class T>static void pr(ostream&o,const set<T>&v){pr_seq(o,v);}
template<class T>static void pr(ostream&o,const unordered_set<T>&v){pr_seq(o,v);}
static void pr(ostream&o,float x){pr(o,(double)x);}
static void pr(ostream&o,long double x){pr(o,(double)x);}
static void pr(ostream&o,char x){pr(o,(int)x);}
static void pr(ostream&o,signed char x){pr(o,(int)x);}
static void pr(ostream&o,unsigned char x){pr(o,(int)x);}
static void pr(ostream&o,short x){pr(o,(int)x);}
static void pr(ostream&o,unsigned short x){pr(o,(int)x);}
static void pr(ostream&o,unsigned int x){o<<x;}
static void pr(ostream&o,unsigned long long x){o<<x;}
'''


def ctype(t, kind="input"):
    """Convert tests.json type declarations to C++ types.

    Accepts both the compact legacy form (int[]) and standard C++ forms
    (vector<int>, std::vector<int>, vector<vector<int>>). `kind` is used in
    error messages so bad input and return declarations can be told apart.
    """
    if not isinstance(t, str):
        raise ValueError(f"Invalid C++ {kind} type: {t!r}")

    t = re.sub(r"\s+", " ", t.strip()).replace("std::", "")
    primitive = {
        "int": "int", "signed": "int", "signed int": "int",
        "long": "long long", "long int": "long long", "long long": "long long",
        "long long int": "long long",
        "double": "double", "long double": "long double", "float": "float",
        "bool": "bool", "string": "string",
        "char": "char", "signed char": "signed char", "unsigned char": "unsigned char",
        "short": "short", "short int": "short", "unsigned short": "unsigned short",
        "unsigned": "unsigned int", "unsigned int": "unsigned int",
        "unsigned long": "unsigned long long", "unsigned long int": "unsigned long long",
        "unsigned long long": "unsigned long long", "size_t": "unsigned long long",
    }
    if t in primitive:
        return primitive[t]

    # int[], int [], vector<int> [], int[][]
    array = re.fullmatch(r"(.+?)\s*\[\s*\]\s*", t)
    if array:
        return f"vector<{ctype(array.group(1), kind)}>"

    match = re.fullmatch(r"(vector|deque|list|set|unordered_set)\s*<(.+)>", t)
    if match:
        return f"{match.group(1)}<{ctype(match.group(2).strip(), kind)}>"

    raise ValueError(
        f"Unsupported C++ {kind} type '{t}' in tests.json. "
        "Use types such as int, string, int[], vector<int>, or deque<int>."
    )


def rtype(t):
    """Convert a tests.json "returns" declaration to a C++ type.

    "void" is valid here (for stdout problems) even though it is not a valid
    parameter type for ctype().
    """
    if isinstance(t, str) and t.strip().replace("std::", "") == "void":
        return "void"
    return ctype(t, kind="return")


# Submissions get a restricted environment and, on Windows, a Job Object that
# limits the number of processes and total memory and kills any leftover
# children when the job handle closes. This is not a full OS sandbox, but it
# prevents the common fork-bomb / runaway-memory failure modes.
_SENSITIVE_ENV = (
    "TOKEN", "SECRET", "PASSWORD", "PASSWD", "CREDENTIAL", "APIKEY",
    "API_KEY", "ACCESS_KEY", "PRIVATE_KEY", "AUTH", "SESSION", "COOKIE"
)


def submission_env():
    """Copy the parent environment without credential-like variables."""
    env = os.environ.copy()
    for key in list(env):
        if any(word in key.upper() for word in _SENSITIVE_ENV):
            env.pop(key, None)
    return env


if os.name == "nt":
    import ctypes

    class _IOCounters(ctypes.Structure):
        _fields_ = [(name, ctypes.c_ulonglong) for name in (
            "ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
            "ReadTransferCount", "WriteTransferCount", "OtherTransferCount"
        )]

    class _JobBasicLimits(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_longlong),
            ("PerJobUserTimeLimit", ctypes.c_longlong),
            ("LimitFlags", ctypes.c_ulong),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", ctypes.c_ulong),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", ctypes.c_ulong),
            ("SchedulingClass", ctypes.c_ulong),
        ]

    class _JobExtendedLimits(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", _JobBasicLimits),
            ("IoInfo", _IOCounters),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    def _create_job():
        try:
            kernel = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p]
            kernel.CreateJobObjectW.restype = ctypes.c_void_p
            kernel.SetInformationJobObject.argtypes = [
                ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_ulong
            ]
            kernel.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
            kernel.OpenProcess.restype = ctypes.c_void_p
            kernel.AssignProcessToJobObject.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
            kernel.AssignProcessToJobObject.restype = ctypes.c_int
            kernel.CloseHandle.argtypes = [ctypes.c_void_p]
            job = kernel.CreateJobObjectW(None, None)
            if not job:
                return None
            limits = _JobExtendedLimits()
            limits.BasicLimitInformation.LimitFlags = (
                0x00002000 | 0x00000008 | 0x00000200  # kill-on-close, processes, job memory
            )
            limits.BasicLimitInformation.ActiveProcessLimit = 4
            limits.JobMemoryLimit = 768 * 1024 * 1024
            kernel.SetInformationJobObject(job, 9, ctypes.byref(limits), ctypes.sizeof(limits))
            return kernel, job
        except Exception:
            return None

    def _assign_job(job, pid):
        if not job:
            return False
        kernel, handle = job
        process = kernel.OpenProcess(0x0100 | 0x0001, False, pid)  # SET_QUOTA | TERMINATE
        if not process:
            return False
        try:
            return bool(kernel.AssignProcessToJobObject(handle, process))
        finally:
            kernel.CloseHandle(process)

    def _close_job(job):
        if job:
            try:
                job[0].CloseHandle(job[1])
            except Exception:
                pass
else:
    def _create_job():
        return None

    def _assign_job(job, pid):
        return False

    def _close_job(job):
        pass


def run_submission(cmd, cwd, timeout, stdin=None):
    """Run user code with a restricted environment and, on Windows, a job object."""
    job = _create_job()
    proc = None
    try:
        proc = subprocess.Popen(
            cmd, cwd=cwd, env=submission_env(), text=True,
            stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
        _assign_job(job, proc.pid)
        out, err = proc.communicate(input=stdin, timeout=timeout)
        return subprocess.CompletedProcess(cmd, proc.returncode, out, err)
    except subprocess.TimeoutExpired:
        if proc is not None:
            proc.kill()
            proc.communicate()
        raise
    finally:
        _close_job(job)


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
                if "types" not in m: return {"error": 'tests.json needs a "types" map (e.g. {"nums": "int[]"}) for C++.'}
                if "returns" not in m:
                    return {"error": ('tests.json needs a "returns" field for C++ '
                                      '(e.g. "int", "int[]", or "void" with "output_mode": "stdout").')}
                try:
                    return_type = rtype(m["returns"])
                except ValueError as exc:
                    return {"error": f'Invalid C++ "returns" declaration in tests.json: {exc}'}
                if return_type == "void" and m.get("output_mode") != "stdout":
                    return {"error": '"returns": "void" requires "output_mode": "stdout" in tests.json.'}
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
                exe_path = os.path.join(tmp, "main.exe")

                def run_case(item):
                    case_no, test = item
                    case_dir = os.path.join(tmp, f"case{case_no}")
                    os.mkdir(case_dir)
                    inp = "\n".join(json.dumps(v, separators=(",", ":")) for v in test["input"].values())
                    r, t0 = {}, time.time()
                    try:
                        p = run_submission([exe_path], case_dir, tl, inp)
                        r["stdout"] = p.stdout
                        if p.returncode:
                            r["error"] = f"Runtime error (exit code {p.returncode})\n{p.stderr}"
                        else:
                            result_file = os.path.join(case_dir, "result.json")
                            if not os.path.isfile(result_file):
                                r["error"] = "The runner exited without producing a result."
                            else:
                                r["actual"] = json.loads(Path(result_file).read_text(encoding="utf8"))
                    except subprocess.TimeoutExpired:
                        r["error"] = "Time Limit Exceeded"
                    except Exception as e:
                        r["error"] = str(e)
                    r["ms"] = round((time.time() - t0) * 1000, 2)
                    return r

                # Each case keeps its own directory and timeout, but cases run in
                # parallel so Submit no longer pays process startup N times in a row.
                workers = min(4, os.cpu_count() or 1, max(1, len(tests)))
                with ThreadPoolExecutor(max_workers=workers) as pool:
                    res = list(pool.map(run_case, enumerate(tests, 1)))
                return {"results": res}
            if lang == "python": exe, name, runner, rn = PY, "sol.py", PY_RUNNER, "runner.py"
            else:
                exe = shutil.which("node")
                if not exe: return {"error": "Node.js not found. Install it from nodejs.org and restart LocalCode."}
                name, runner, rn = "sol.js", JS_RUNNER, "runner.js"
            w(name, code); w(rn, runner); w("payload.json", json.dumps({"method": m["method"], "tests": tests, "output_mode": m.get("output_mode")}))
            p = run_submission([exe, rn], tmp, tl)
            out_file = Path(tmp, "out.json")
            if p.returncode:
                detail = (p.stderr or p.stdout or "").strip()
                return {"error": f"Runner exited with code {p.returncode}." + (f"\n{detail}" if detail else "")}
            if not out_file.is_file():
                return {"error": "Runner exited normally but produced no results (out.json missing)."}
            return json.loads(out_file.read_text(encoding="utf8"))
        except subprocess.TimeoutExpired: return {"tle": True}
        except Exception as e: return {"error": f"Runner failed: {e}"}


def norm(x, unordered):
    """Normalize a value for comparison; unordered applies to nested lists too."""
    if not unordered:
        return x

    def walk(value):
        if isinstance(value, list):
            return sorted((walk(item) for item in value), key=lambda item: json.dumps(item, sort_keys=True))
        return value

    return walk(x)


