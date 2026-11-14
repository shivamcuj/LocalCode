# LocalCode 2.6.1

LocalCode is a **Windows desktop, offline-first LeetCode-style practice judge**. Pick a
problem, write a solution in Python, C++ or JavaScript, and run it against local test
files. There is no account, no server and no cloud judging.

Version 2.6.1 is a **C++ judge release**. The long-standing `vector<int>` type error and
the header-ordering bug are fixed: C++ starters that use `vector`, `string`, `cout` and
friends now compile without the user adding `#include <bits/stdc++.h>` manually. A new
problem, `213-maximum-consecutive-ones`, uses those C++ signatures. The `838` test data
was also reworked (much smaller file, smaller maximum input).

> Version strings are still mixed: the UI badge says **2.6**, and
> `README_LOCALCODE.txt` still has the "LOCALCODE WINDOWS 2.2" title, although its body
> now includes v2.3–v2.6.1 notes.

## What's new in v2.6.1

### C++ type system expanded

`engine.ctype()` in `engine.py` was rewritten. It now accepts:

| `tests.json` type | Generated C++ type |
| --- | --- |
| `int` | `int` |
| `long` | `long long` |
| `long long` | `long long` |
| `double` | `double` |
| `float` | `float` |
| `bool` | `bool` |
| `string` | `string` |
| `char` | `char` |
| `T[]` | `vector<T>` |
| `vector<T>` | `vector<T>` |
| `std::vector<T>` | `vector<T>` (prefix stripped) |
| nested forms | `vector<vector<int>>`, `vector<string>`, `int[][][]`, … |

It normalizes whitespace inside `vector< … >`, handles `std::` prefixes, and raises a
readable `ValueError` for anything it cannot map:

```text
Unsupported C++ input type 'map<int,int>' in tests.json.
Use types such as int, string, int[], or vector<int>.
```

Previously this path raised a bare `KeyError`, which surfaced as
`Runner failed: 'vector<int>'`.

### C++ header ordering fixed

The generated file order used to be:

```text
<your code>
<bits/stdc++.h> + reader/writer helpers
main()
```

It is now:

```text
<bits/stdc++.h> + using namespace std + reader/writer helpers
<your code>
main()
```

`engine.py` changed one line:

```python
w("main.cpp", CPP_HELP + "\n" + code + "\n" + main)
```

As a result, starters that use `vector<int>`, `string` or `cout` without their own include
compile again. This affects `695`, `702`, `838`, the new `213`, and `951`'s stdout
solution.

### New problem: `213-maximum-consecutive-ones`

- **Easy**, `method: findMaxConsecutiveOnes`, return mode, 10 s per case.
- **344 tests**, binary arrays of length 1–500, expected answers 0–500.
- Types: `{"nums": "vector<int>"}` — the exact form that used to break C++.
- Starters for Python, C++ and JavaScript are included.

Adding it inserts it at **index 1** in the picker (ids are sorted as strings), so the other
problems shift down by one. Drafts are keyed by problem folder, so saved drafts are not
lost by the renumbering.

### `838-linear-search` data rework

- Test count: **256 → 245**.
- Largest array: **100,000 → 10,000** elements.
- `tests.json`: **≈ 8 MB → ≈ 0.54 MB**.
- Distribution: 199 cases with ≤100 elements, 44 with 101–1,000, 2 with 1,001–10,000.
- The starter lost its blank lines; `user_solution.cpp` was reformatted and again contains
  a placeholder `return true;`.

> This is a **coverage reduction** compared with v2.5/v2.6, traded for a much faster load
> and a smaller repository. The statement's **Constraints** section was also removed and
> replaced with an **Input Assumption** note, reversing the v2.5 change.

### Docs

- `README_LOCALCODE.txt` gained two v2.6.1 lines about the expanded C++ types and the new
  header order.

## Fixed since v2.6

| v2.6 problem | Status in v2.6.1 |
| --- | --- |
| C++ `vector<int>` types raised `Runner failed: 'vector<int>'` for `695`, `702`, `838` | **Fixed** — `ctype()` accepts `vector<int>` and nested forms |
| C++ `'vector' has not been declared` because headers came after user code | **Fixed** — `CPP_HELP` is emitted before user code |
| C++ `951` solution failed with `'cout' was not declared in this scope` | **Fixed** — `using namespace std` and `<bits/stdc++.h>` are now in scope |
| Type errors were raw `KeyError`s with no guidance | **Fixed** — actionable `ValueError` message |
| `vector<std::vector<int>>` / `std::vector<int>` could not be described | **Fixed** — normalized to `vector<vector<int>>` / `vector<int>` |
| New C++-heavy problems could not use `vector<int>` signatures | **Fixed** — `213` uses one and passes |
| `838` shipped an 8 MB test file | **Improved** — now about 0.54 MB |
| `838` starter had stray blank lines | **Cosmetic** — reformatted |

Verified end to end with `g++ 16.2.0` (MSYS2) and the real `engine.judge` path:

- `213`, `695`, `702`, `838` and `951` C++ solutions **without any includes** compile and
  return the expected values for the first cases (including `951`'s stdout pattern).
- `ctype("vector<int>")` → `vector<int>`, `std::vector<int>` → `vector<int>`,
  `vector<vector<int>>` → `vector<vector<int>>`, `int[][][]` →
  `vector<vector<vector<int>>>`.
- Python and JavaScript still pass `213` and `838`.

## Regressions and new issues in v2.6.1

1. **`838-linear-search` coverage shrank.** 256 → 245 tests and maximum array length
   100,000 → 10,000. Large-input performance is no longer exercised.
2. **`838` constraints were removed.** `problem.md` no longer states
   `1 <= nums.length <= 10^5`; it says the statement "does not specify" limits. This
   reverses the v2.5 documentation improvement.
3. **`838/user_solution.cpp` has `return true;` again** inside an `int` function. It
   compiles (true → 1) but is a leftover placeholder.
4. **Badge still says `2.6`.** The release is v2.6.1 but `webui/index.html` was not
   bumped.
5. **`README_LOCALCODE.txt` title still says 2.2.**
6. **`ctype` still rejects spaced legacy forms** such as `int []` (no space support before
   `[]`), `unsigned int`, and any STL type other than `vector`.

## Still broken or carried over

`app.py`, `webui/src/main.js`, `webui/style.css` and `run.bat` have no functional changes in
v2.6.1.

1. **`returns` is still not validated for C++**, even though the error text mentions it.
2. **`951` stdout matching is exact and does not ignore trailing spaces.** Expected strings
   have no trailing spaces; a common `"* "`-per-cell solution emits one and fails. Only
   trailing `\r\n` is stripped before comparison.
3. **The full editor still needs the network on every launch.** CodeMirror is imported
   from `https://esm.sh`; offline users get the plain textarea without highlighting,
   autocomplete, folding or Tab indentation.
4. **`webui/package.json` is dead weight.** Its CodeMirror dependencies and esbuild script
   are unused at runtime.
5. **The editor upgrade still replays unconditionally** after `cmReady`, discarding cursor
   position and undo history and potentially showing the fallback toast twice.
6. **`os.chdir(ROOT)` is process-wide.** Harmless today because the judge uses temporary
   directories and absolute problem paths, but fragile for future relative paths.
7. **`run_test_count` can display values below 2.** The backend clamps to 2–4 and then
   takes `min(…, visible_count)`, so a problem with one visible test shows
   `Run: 1 sample`.
8. **`__pycache__/` is untracked noise.** Importing `app.py` creates it and there is still
   no root `.gitignore`.
9. **Markdown image/link URLs cannot contain `)` or titles** (`![a](pic.png "caption")`),
   local images are re-read and base64-encoded on every load with no size cap or cache,
   and remote images are fetched directly by the WebView.
10. **Submit still runs the whole suite**, one C++ process per case. `838` and `951` are
    faster now thanks to the smaller `838` file, but there is no batching.

## Still open from earlier versions

- String id sorting (`1000` would sort before `213`), MSYS2 path coverage, `py`/`python`
  interpreter mismatch, ignored runner exit codes, no sandbox, top-level-only `unordered`,
  and `user_solution.*` scratch files.
- `run.bat` only checks that `webview` imports; it does not enforce
  `pywebview>=5.4,<7`.
- `build_exe.bat` is still a placeholder; there is no standalone EXE build.
- `difficulty: "Basic"` still gets the default green pill (CSS defines only `medium` and
  `hard`).
- `list_problems` rescans the folder on every call, so indices can shift if folders change
  while the app is open.
- No root `.gitignore` for `__pycache__/`, `user_solution.*` or `webui/dist/`.
- `README_LOCALCODE.txt` still contains stale v2.1 lines about the "first-time editor
  build" and `webui\dist`.

## Requirements (Windows)

- Windows 10/11.
- **Python 3** with `py` or `python` on `PATH`.
- **Microsoft Edge WebView2 Runtime** — normally present on current Windows; install the
  Evergreen Runtime if LocalCode reports that the webview could not start.
- **g++** (MSYS2 UCRT64 recommended) — only for C++ judging.
- **Node.js LTS** — only for JavaScript judging (not required to launch).
- **Internet access** for the full CodeMirror editor. Without it, LocalCode uses the
  textarea fallback. Local problem images still work offline.

## Quick start

1. Extract the folder (do not run from inside a ZIP preview).
2. Double-click **`run.bat`**.
   - It locates Python (prefers `py -3`, then `python`).
   - If `node` is missing, it prints a warning and continues.
   - If `import webview` fails, it runs `pip install -r requirements.txt`.
   - It starts `app.py`.
3. Select a problem, choose a language, write code, then **Run** (samples) or **Submit**
   (all tests).
4. Click any image in the statement to enlarge it; press Escape to close.

Manual start:

```bat
python -m pip install -r requirements.txt
python app.py
```

There is **no npm install and no build step**, and the UI is served by pywebview's local
HTTP server rather than from `file://`.

## Repository layout

```text
LocalCode/
  app.py                  # pywebview shell, HTTP-served UI, Run/Submit, resolve_image
  engine.py               # judge: Python/JS runners, C++ codegen, compile & execute
  requirements.txt        # pywebview>=5.4,<7
  run.bat                 # Python check, optional Node warning, pywebview install, launch
  build_exe.bat           # placeholder (no EXE build)
  README.md               # this file
  README_LOCALCODE.txt    # plain-text 2.2 notes + v2.3–v2.6.1 sections
  README_GCC_FIX.txt      # MSYS2 GCC runtime-DLL note
  webui/
    index.html            # app shell (LocalCode); image-preview modal; badge 2.6
    style.css             # dark theme, rich-Markdown, image and preview styles
    src/main.js           # UI logic, Markdown renderer, image resolution, CDN loader
    package.json          # vestigial CodeMirror deps + unused esbuild script
    .gitignore            # node_modules/
  problems/
    001-two-sum/                  # 4 tests (2 hidden); Run uses 2
    213-maximum-consecutive-ones/ # 344 tests, arrays 1–500; vector<int>, all languages
    695-second-largest-element/   # 239 tests; C++ now compiles
    702-largest-element/          # 205 tests; C++ now compiles
    838-linear-search/            # 245 tests up to 10k elements; C++ now compiles
    951-pattern-19/               # 100 stdout tests; C++ now compiles
    984-pattern4/                 # 9 stdout tests
```

Each problem folder contains `problem.md`, `tests.json` and optional `starter.py`,
`starter.cpp`, `starter.js` (plus any images or reference files).

## Problem format

```text
problems/
  1000-my-problem/
    problem.md
    tests.json
    starter.py            # optional
    starter.cpp           # optional
    starter.js            # optional
    attached.png          # optional; reference as ![alt](attached.png)
    images/               # optional; reference as ![alt](images/example.png)
```

### `tests.json`

Required fields:

| Field    | Meaning                                                        |
| -------- | -------------------------------------------------------------- |
| `id`     | Problem number/identifier (currently sorted as a string)       |
| `title`  | Title shown in the picker                                      |
| `method` | Method name on the `Solution` class that the judge calls       |
| `tests`  | Non-empty array of `{ "input": {...}, "expected": ... }` cases |

Optional fields:

| Field            | Meaning                                                                       |
| ---------------- | ----------------------------------------------------------------------------- |
| `difficulty`     | `Easy`, `Medium` or `Hard`; `Basic` also appears and uses the default colour   |
| `unordered`      | `true` → compare a top-level list result ignoring order                        |
| `timeout`        | Per-case timeout in seconds (default `10`)                                     |
| `output_mode`    | `"stdout"` → compare printed output; anything else compares the return value   |
| `run_test_count` | Visible tests used by **Run**; clamped to **2–4**, default `3`                 |
| `types`          | **Required for C++**: map of parameter name → type                             |
| `returns`        | Documented for C++ but currently not validated                                 |

A test can set `"hidden": true`; hidden cases run only on **Submit**.

Example:

```json
{
  "id": 1,
  "title": "Two Sum",
  "difficulty": "Easy",
  "method": "twoSum",
  "unordered": true,
  "timeout": 10,
  "run_test_count": 3,
  "tests": [
    { "input": { "nums": [2, 7, 11, 15], "target": 9 }, "expected": [0, 1] },
    { "input": { "nums": [3, 3], "target": 6 }, "expected": [0, 1], "hidden": true }
  ],
  "types": { "nums": "int[]", "target": "int" },
  "returns": "int[]"
}
```

### C++ types accepted in v2.6.1

See the table in [“C++ type system expanded”](#c-type-system-expanded). Both the compact
legacy form (`int[]`) and the standard C++ form (`vector<int>`, `std::vector<int>`) work,
including nesting. `unsigned`, `const`, STL types other than `vector`, and `int []` with a
space before `[]` are not supported and produce a clear error.

### Starter code and includes

Generated C++ file order:

```text
<bits/stdc++.h> + using namespace std + reader/writer helpers
<your code>
main()
```

You no longer need to add `#include <bits/stdc++.h>` to a solution. Keep in mind that the
helper functions `ws`, `rd` and `pr` are declared before your code; avoid redefining those
names.

### Markdown in `problem.md`

Supported:

| Syntax | Result |
| --- | --- |
| `# …` … `###### …` | `<h1>` … `<h6>` |
| Blank-line-separated text | `<p>` (wrapped lines are joined) |
| `**bold**`, `*italic*`, `` `code` `` | `<strong>`, `<em>`, `<code>` |
| ` ```lang ` fences | `<pre><code class="language-lang">` |
| `-`, `*`, `+` items | `<ul><li>` |
| `1.`, `1)` items | `<ol><li>` |
| `> quote` | `<blockquote>` |
| `---`, `___`, `***` | `<hr>` |
| `[label](https://…)` | link, opens in a new tab |
| `![alt](https://…)` | remote image + caption |
| `![alt](relative/path.png)` | local image via `resolve_image`, offline |
| Anything else / raw HTML | escaped text |

Known gaps: image/link targets containing `)` and optional titles
(`![a](pic.png "caption")`) are not parsed; unmatched syntax is shown as text.

Local image rules:

- The path is relative to the **selected problem folder**.
- `images/…` subfolders are fine.
- Absolute paths, `../` traversal, `file:`/`data:`/`javascript:` and remote URLs are
  rejected with an error message.
- Only files whose MIME type is `image/*` are served.

## How the judge works

Every Run/Submit:

1. Saves the editor draft in memory and writes `user_solution.<ext>` into the problem
   folder.
2. Chooses the test list: Run = first `run_test_count` visible tests; Submit = all tests.
3. Calls `engine.judge(...)` with the selected language and test list.
4. Runs everything in a fresh temporary directory and returns per-case results.

- **Python** — the solution is `exec`'d in a namespace that pre-imports `typing`,
  `collections`, `math`, `heapq`, `itertools`, `functools` and `bisect`, then
  `Solution().<method>(**input)` is called. `stdout` is captured per case.
- **C++** — generates `main.cpp` (headers → user code → `main()`), compiles with
  `g++ -O2 -std=c++17` (120 s allowed), feeds each case's arguments on stdin and reads the
  result from `result.json`. In `stdout` mode, `cout` is captured and written as a JSON
  string.
- **JavaScript** — the file is wrapped with `new Function(...)`, `Solution` is
  instantiated per case, and `console.log` is captured.

**Run** executes the sample subset. **Submit** executes every test, including hidden ones.

Verdicts: `Accepted`, `Wrong Answer`, `Runtime Error`, `Time Limit Exceeded`,
`Execution Error` (setup/compile failure).

In `stdout` mode a trailing `\r\n` is ignored, but other whitespace (including trailing
spaces) must match exactly.

## Known issues and limitations (v2.6.1)

- **`838` coverage is smaller than v2.6** (245 tests, max 10k elements) and its constraints
  section is gone.
- **`951` expects no trailing spaces.** Build lines with a separator (`j ? " *" : "*"`)
  rather than appending `"* "`.
- **Badge still says 2.6; plain-text title still says 2.2.**
- **Full editor requires internet.** Without `esm.sh`, the textarea fallback is used.
- **Submit can be slow** on `951` (100 cases) and `213` (344 cases), especially in C++.
- **Drafts are memory-only.** Closing the app loses unsaved drafts; only
  `user_solution.<ext>` is written to disk.
- **`user_solution.*` files pollute the problem folders.**
- **`run.bat` does not enforce `pywebview>=5.4`.** It only checks that `webview` imports.
- **`build_exe.bat` is a placeholder.** Use `run.bat` from the source folder.
- **No root `.gitignore`** for generated files.

## Troubleshooting

| Symptom | Cause / fix |
| --- | --- |
| C++: `Runner failed: Unsupported C++ input type '…'` | `ctype()` does not know that type. Use `int`, `string`, `int[]`, `vector<int>` or another supported form. |
| C++: something still "has not been declared" | Headers are now emitted first, so this should be gone. If it persists, check for a local name clash with `ws`, `rd` or `pr`, or an unsupported type in `types`. |
| `951`: Wrong Answer on a visually correct pattern | The expected strings have no trailing spaces; avoid emitting `"* "` at the end of each line. |
| An image in the statement shows `Image unavailable: …` | The file is missing, is outside the problem folder, or is not an `image/*` type. |
| `951`'s reference PNG is not displayed | It is only mentioned as inline code. Add `![Pattern reference](attached-pattern-reference.png)` to `problem.md`. |
| Run shows only 2–4 cases | Expected: Run uses sample tests. Use Submit for the full suite. |
| C++: compile error about a missing include | Should no longer happen in v2.6.1. Verify you are on this branch and that `engine.CPP_HELP` precedes your code. |
| Editor is a plain textarea | CodeMirror could not be fetched from `esm.sh` (offline, proxy, DNS). The toast explains the reason. |
| "LocalCode could not start" / webview initialization error | Install or repair the Microsoft Edge WebView2 Evergreen Runtime. |
| Window stays blank | Check that `webui/index.html` exists, then run `python app.py` in a terminal for the traceback. |
| `g++ was not found...` | Install MSYS2 UCRT64 GCC and add `C:\msys64\ucrt64\bin` to `PATH`. |
| `cc1plus.exe - Entry Point Not Found` / `libgcc_s_seh-1.dll` missing | MSYS2 runtime DLLs are not on the child-process `PATH`; only default `C:\msys64` locations are auto-added. See `README_GCC_FIX.txt`. |
| `Node.js not found...` warning at launch | Harmless for Python/C++. Install Node.js LTS only if you need JavaScript judging. |
| `tests.json needs a "types" map ... for C++` | Add `types` (and ideally `returns`) for that problem. |
| `Python 3 was not found.` | Python is not installed or `py`/`python` is not on `PATH`. |
| EXE build fails | Expected: `build_exe.bat` is a placeholder. Use `run.bat`. |

## Version history (this branch)

- **v2.6.1** — fixes the C++ judge: `ctype()` accepts `vector<int>`, `std::vector<int>` and
  nested vector forms, unsupported types raise a readable error, and `CPP_HELP` is emitted
  before user code so `vector`/`cout` no longer need manual includes. Adds
  `213-maximum-consecutive-ones` (344 tests) and shrinks `838-linear-search` to 245 tests
  up to 10k elements (removing its constraints section).
- **v2.6** — restores rich Markdown (headings 1–6, lists, blockquotes, rules, links,
  fenced-code languages), renders remote and local images via `resolve_image` with
  path/MIME validation and base64 data URLs, adds a click-to-zoom image modal, and restores
  the **LocalCode** brand with a **2.6** badge.
- **v2.5** — restores Run-vs-Submit sample logic (`run_test_count`, default 3, clamp 2–4),
  adds scope labels and an empty-test guard, adds `951-pattern-19` (100 stdout tests),
  expands `838-linear-search` to 256 tests with documented constraints, and rebrands the
  page to `SRKCode`.
- **v2.4** — fixes CodeMirror `indentOnInput` registration and adds a resilient textarea
  fallback for CDN and constructor failures.
- **v2.3** — removes the `Window` reference from the JS API, serves the UI through
  pywebview's local HTTP server, and loads problems before the CodeMirror CDN.
- **v2.2** — removes the npm/esbuild build step, loads `src/main.js` directly, restores
  CDN CodeMirror with a textarea fallback, and makes Node.js optional at launch.
- **v2.1** — locally bundled CodeMirror via esbuild, automated first-run build, Node.js
  as a hard requirement.
- **v2.0** — pywebview + CodeMirror web UI, rich Markdown and image previews, Run sample
  logic, expanded C++ types and header ordering.
- **v1.0** — Tkinter desktop judge with Python/C++/JavaScript support.
