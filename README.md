# LocalCode 2.0

LocalCode is a **Windows desktop, LeetCode-style practice judge that runs entirely on
your machine**. Pick a problem, write a solution in Python, C++ or JavaScript, and run it
against local test files. There is no account, server or cloud judging.

Version 2.0 replaces the old Tkinter window with a **pywebview desktop shell + HTML/CSS/JS
interface** and a **CodeMirror 6** editor. Problem statements, test execution and
comparison all stay local. The full editor is downloaded from a CDN at launch, so an
internet connection is recommended; without it the app falls back to a plain textarea and
still loads problems, runs code and submits answers.

> The in-app badge currently reads **2.6** (the latest UI revision). This branch is the
> **v2.0** major release; the 2.1–2.6 notes below are the fixes rolled into it.

## What's new in v2.0

### New desktop UI

- Tkinter UI replaced by **pywebview** hosting `webui/index.html`.
- Dark two-pane workspace: problem statement on the left, editor + test results on the
  right.
- Problem picker with a **Refresh** button (rescans `problems/`) and **Open problems
  folder** (opens it in Explorer).
- Live verdict badge, result table (status, input, expected, output), per-case detail
  pane, and toast notifications for errors/warnings.
- Keyboard shortcuts: **Ctrl+Enter** runs, **Ctrl+Shift+Enter** submits, **Esc** closes
  the image preview.
- Window is resizable with a sensible minimum size; layout adapts below 1100 px.

### CodeMirror 6 editor

- Python, C++ and JavaScript syntax highlighting (per-language modes, unlike the single
  shared keyword regex in v1.0).
- Line numbers, active-line highlight, bracket matching, auto-closing brackets/quotes,
  automatic indentation.
- **Tab** inserts a 4-space indent, **Shift+Tab** outdents.
- Autocomplete (**Ctrl+Space**), search, code folding, undo/redo and multiple selections.
- Separate in-session drafts per problem **and** language; switching language restores
  that language's draft.
- Graceful **fallback textarea** if the CodeMirror CDN import fails or times out (12 s).
  The fallback has no highlighting/autocomplete but Run and Submit still work.

### Rich problem statements

- Markdown renderer supports headings, paragraphs, **bold**, *italic*, inline code,
  fenced code blocks, unordered/ordered lists, blockquotes, horizontal rules and links.
- **Images** in `problem.md`:
  - Remote images: `![alt](https://...)` (needs internet).
  - Local images: `![alt](images/example.png)` relative to the problem folder. They are
    read by the Python side and embedded as base64 data URLs, so they work offline.
  - Click any rendered image to open a full-window preview; click outside or press Esc to
    close.
  - Local paths are confined to the selected problem folder; absolute paths, `..`
    traversal and `file:`/`javascript:` URLs are rejected.
  - Raw HTML in `problem.md` is escaped, not executed.

### Smarter Run vs Submit

- **Run** is now a fast feedback loop: it executes only the first 2–4 **visible** test
  cases (default 3). The count is configurable per problem:

  ```json
  "run_test_count": 3
  ```

  Values are clamped to 2–4; if a problem has fewer visible tests, all of them are used.
- **Submit** executes the complete test suite, including cases marked `"hidden": true`.
- The header shows exactly what will run, e.g. `Run: 3 sample · Submit: 9 total tests`.

### Expanded C++ support

- Type declarations now accept both shorthand and C++ syntax:
  `int`, `long`, `long long`, `double`, `float`, `bool`, `string`, `char`,
  `int[]`, `vector<int>`, `std::vector<int>`, and nested forms such as
  `vector<vector<int>>` or `int[][]`.
- Unsupported types now produce a clear `Unsupported C++ input type ...` message instead
  of a raw `KeyError`.
- **Standard headers are emitted before submitted code**, so starter signatures that use
  `vector<int>` without `#include` now compile. (In v1.0 the helper headers were appended
  after the solution, so such starters failed.)

### Other additions

- `engine.py` — the judge/sandbox layer extracted from `app.py` (still not a true
  sandbox; see limitations).
- `webui/` — `index.html`, `style.css`, `src/main.js`, `package.json` (the npm build is
  not used at runtime).
- `requirements.txt` — `pywebview>=5.4,<7`.
- `run.bat` now checks Python and Node.js, installs pywebview if missing, and launches the
  app.
- Three new sample problems:
  - `695-second-largest-element` (239 tests)
  - `702-largest-element` (205 tests)
  - `838-linear-search` (245 tests)
- Existing samples gained `run_test_count`.

## Fixes since v1.0

| v1.0 problem | Status in v2.0 | Where |
| --- | --- | --- |
| Skipped-problem warning joined with the literal text `\n` | **Fixed** — warnings are returned as a list and joined with a real newline in JS | `app.py` `list_problems()`, `webui/src/main.js` |
| Stdout comparison used `rstrip("\\r\\n")`, stripping the characters `\`, `r`, `n` | **Fixed** — uses `rstrip("\r\n")` | `app.py` `run_solution()` |
| C++ helper headers appended after user code, breaking starters without includes | **Fixed** — `CPP_HELP` is emitted first | `engine.py` `judge()` |
| C++ type parser threw `KeyError` and could not read `vector<...>` types | **Fixed** — recursive `ctype()` with a clear error | `engine.py` `ctype()` |
| Syntax highlighting used one keyword list for all languages | **Fixed** — CodeMirror language modes (fallback editor has no highlighting) | `webui/src/main.js` |
| CodeMirror `"Unrecognized extension value in extension set"` error | **Fixed** — `indentOnInput()` is registered as an extension, with fallback | `webui/src/main.js` |
| Blank window / startup crash from attaching the pywebview `Window` to the JS API object | **Fixed** — the API object no longer holds a window reference | `app.py` `LocalCodeAPI` |
| Problem loading blocked by slow/failed editor bundle import | **Fixed** — problems and starter code load before CodeMirror is awaited; bridge is also polled | `webui/src/main.js` |
| Startup race where `pywebviewready` fired before the script loaded | **Fixed** — event plus 100 ms bridge check | `webui/src/main.js` |
| `build_exe.bat` produced a broken/unsupported executable | **Changed** — EXE packaging is a placeholder in this release; use `run.bat` | `build_exe.bat` |

### Still open from v1.0

These were documented in v1.0 and are **not fixed** in v2.0:

1. **`returns` is still not validated** — `engine.py` only checks for `types` for C++,
   although the error text and docs mention `returns`.
2. **Problems are still sorted as strings** — `app.py` uses `str(id)`, so ids `1000`,
   `695`, `702` would order as `1000, 695, 702`. Zero-padded ids avoid this.
3. **The GCC DLL workaround still only covers the default MSYS2 path** — only
   `C:\msys64\ucrt64\bin` and `C:\msys64\usr\bin` are prepended. Other MSYS2/MinGW
   installations can still hit `libgcc_s_seh-1.dll` / `cc1plus.exe` entry-point errors.
   See `README_GCC_FIX.txt`.
4. **`run.bat` and the judge may use different Python interpreters** — `run.bat` prefers
   `py -3`, while `engine.py` resolves `python` first, then `py`.
5. **Runner exit codes are still ignored** — a Python/JS runner that crashes before
   writing `out.json` is reported only as `Runner failed: ...`.
6. **Not a sandbox** — submissions run with full user privileges. Only the per-case
   timeout limits them.
7. **`unordered` still only sorts a top-level list** — nested or non-list results are
   compared exactly.
8. **`user_solution.<ext>` files are still written into the problem folder** on every
   Run/Submit (e.g. `problems/001-two-sum/user_solution.cpp`). They are scratch files and
   are not needed by the app.

## Quick start (Windows)

### Requirements

- Windows 10/11.
- **Python 3** with `py` or `python` on `PATH`.
- **Microsoft Edge WebView2 Runtime** — normally preinstalled on current Windows; install
  the Evergreen Runtime if LocalCode reports the webview could not start.
- **Node.js LTS** — only for judging JavaScript; Python and C++ work without it.
- **g++** (MSYS2 UCRT64 recommended) — only for judging C++.
- Internet access for the CodeMirror editor (optional; offline fallback works).

### Run

1. Extract the folder (do not launch from inside a ZIP preview).
2. Double-click **`run.bat`**.
   - It checks for Python and Node.js.
   - If `import webview` fails, it runs `pip install -r requirements.txt`.
   - It then starts `app.py`.
3. Select a problem, choose a language, write code, then **Run** or **Submit**.

Manual start:

```bat
python -m pip install -r requirements.txt
python app.py
```

There is **no npm build step** and no committed `webui/dist` bundle. `webui/src/main.js`
is loaded directly and imports CodeMirror 6 from `esm.sh` when online.

### Packaging an EXE

Not supported in this release. `build_exe.bat` is a placeholder that explains EXE
packaging will come after WebView2 and the Python runner are bundled together. Use
`run.bat` from the source folder.

## Repository layout

```text
LocalCode/
  app.py                  # pywebview shell, JavaScript API, problem loading, Run/Submit
  engine.py               # judge: Python/JS runners, C++ codegen, compile & execute
  requirements.txt        # pywebview>=5.4,<7
  run.bat                 # dependency check/install + launcher
  build_exe.bat           # placeholder (no EXE build in v2.0)
  README.md               # this file
  README_LOCALCODE.txt    # plain-text release notes (2.1-2.6)
  README_GCC_FIX.txt      # MSYS2 GCC runtime-DLL note
  webui/
    index.html            # app shell
    style.css             # dark theme, markdown/image styles
    src/main.js           # UI logic, markdown renderer, CodeMirror loader/fallback
    package.json          # CodeMirror deps + unused esbuild build script
  problems/
    001-two-sum/          # return-value example (2 hidden tests)
    695-second-largest-element/
    702-largest-element/
    838-linear-search/
    984-pattern4/         # stdout ("print the answer") example
```

Each problem folder contains `problem.md`, `tests.json` and optional `starter.py`,
`starter.cpp`, `starter.js`.

## Problem format

```text
problems/
  1000-my-problem/
    problem.md
    tests.json
    starter.py            # optional
    starter.cpp           # optional
    starter.js            # optional
    images/               # optional, for markdown images
```

### `tests.json`

Required fields:

| Field    | Meaning                                                       |
| -------- | ------------------------------------------------------------- |
| `id`     | Problem number/identifier (currently sorted as a string)      |
| `title`  | Title shown in the picker                                     |
| `method` | Method name on the `Solution` class that the judge calls      |
| `tests`  | Non-empty array of `{ "input": {...}, "expected": ... }` cases |

Optional fields:

| Field             | Meaning                                                                 |
| ----------------- | ----------------------------------------------------------------------- |
| `difficulty`      | `Easy`, `Medium` or `Hard`; `Basic` also appears in sample data and uses the default colour |
| `unordered`       | `true` → compare a top-level list result ignoring order                 |
| `timeout`         | Per-case timeout in seconds (default `10`)                              |
| `output_mode`     | `"stdout"` → compare captured printed output; anything else compares the return value |
| `run_test_count`  | Visible tests used by **Run**, clamped to 2–4 (default 3)               |
| `types`           | **Required for C++**: map of parameter name → type                      |
| `returns`         | Expected C++ return type; documented but currently not validated        |

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

### C++ types

| JSON type          | C++ type          |
| ------------------ | ----------------- |
| `int`              | `int`             |
| `long` / `long long` | `long long`     |
| `double`           | `double`          |
| `float`            | `float`           |
| `bool`             | `bool`            |
| `string`           | `string`          |
| `char`             | `char`            |
| `T[]`              | `vector<T>`       |
| `vector<T>` / `std::vector<T>` | `vector<T>` |

Nested forms work recursively. Example: `int[][]` → `vector<vector<int>>`.

Arguments are passed in the order the keys appear in each test's `input` object.

### Images

```md
![Pattern reference](images/pattern.png)
![Remote diagram](https://example.com/diagram.png)
```

Local images must stay inside the problem folder. A filename only mentioned in inline
code (`` `attached-pattern-reference.png` ``) is not rendered as an image; use a Markdown
image line.

## How the judge works

Every Run/Submit:

1. Saves the editor draft in memory and writes `user_solution.<ext>` into the problem
   folder.
2. Calls `engine.judge(...)` with the selected language and test subset.
3. Runs everything in a fresh temporary directory and returns per-case results.

- **Python** — solution is `exec`'d in a namespace pre-importing `typing`, `collections`,
  `math`, `heapq`, `itertools`, `functools`, `bisect`, then
  `Solution().<method>(**input)` is called. `stdout` is captured per case.
- **C++** — `CPP_HELP` (standard headers + JSON-ish reader/writer) is emitted **before**
  the submitted code, followed by a generated `main()`. Compiles with
  `g++ -O2 -std=c++17` (120 s allowed), feeds each case's arguments on stdin and reads the
  result from `result.json`. In `stdout` mode, `cout` is captured and written as a JSON
  string.
- **JavaScript** — the file is wrapped with `new Function(...)`, `Solution` is
  instantiated per case, and `console.log` is captured.

Verdicts: `Accepted`, `Wrong Answer`, `Runtime Error`, `Time Limit Exceeded`,
`Execution Error` (setup/compile failure).

## Known issues and limitations (v2.0)

- **The full editor needs the network.** CodeMirror 6 is imported from
  `https://esm.sh` at launch (`webui/src/main.js`). Offline, the app shows a plain
  textarea: no highlighting, autocomplete, folding or bracket matching. Problem loading,
  Run and Submit still work.
- **Drafts are memory-only.** `save_draft` stores code in the Python process; closing the
  app loses unsaved drafts. Nothing is persisted to disk except `user_solution.<ext>`.
- **`user_solution.*` files pollute problem folders.** See "Still open" item 8.
- **`run.bat` only checks that `webview` imports.** If an older pywebview is already
  installed, it will not upgrade it to the `>=5.4` requirement.
- **`build_exe.bat` is a placeholder.** There is no working standalone build in v2.0.
- **Likely slow C++ Submit on the large samples.** `695`, `702` and `838` contain
  205–245 visible tests each and no hidden tests. Run uses 3; Submit launches the compiled
  executable once per case, so expect it to take noticeably longer.
- **`difficulty: "Basic"` gets the default green pill**; the CSS only defines
  `medium` and `hard` variants.
- **Problem list is refreshed often.** `list_problems` rescans the folder on every call;
  if folders change while the app is open, indices can shift until the list is reloaded.
- **No `.gitignore` for generated files.** `__pycache__/` and `user_solution.*` can show
  up as untracked changes.

### Remaining v1.0 defects

See the "Still open from v1.0" list above: `returns` validation, string id sorting,
MSYS2 path coverage, interpreter mismatch, ignored runner exit codes, no sandbox,
top-level-only `unordered`, and scratch solution files.

## Troubleshooting

| Symptom | Cause / fix |
| --- | --- |
| "LocalCode could not start" / webview initialization error | Install or repair the Microsoft Edge WebView2 Evergreen Runtime. |
| Editor is a plain textarea | CodeMirror could not be fetched from `esm.sh` (offline, proxy, DNS or 12 s timeout). Reconnect and restart for full editing. |
| `g++ was not found...` | Install MSYS2 UCRT64 GCC and add `C:\msys64\ucrt64\bin` to `PATH`. |
| `cc1plus.exe - Entry Point Not Found` / `libgcc_s_seh-1.dll` missing | MSYS2 runtime DLLs are not on the child-process `PATH`; only the default `C:\msys64` locations are auto-added. See `README_GCC_FIX.txt`. |
| `Node.js not found...` on JavaScript Run | Install Node.js LTS and restart. Python and C++ still work. |
| `tests.json needs a "types" map ... for C++` | Add `types` (and `returns`) for that problem. |
| `Unsupported C++ input type '...'` | Use a supported type such as `int`, `string`, `int[]`, `vector<int>` or a nested vector. |
| A stdout answer ending in `r`, `n` or `\` is wrongly accepted | This v1.0 bug is fixed; if you see it, you are running the old code. |
| `Python 3 was not found.` from `run.bat` | Python is not installed or `py`/`python` is not on `PATH`. |
| `LocalCode closed with an error.` | Run `python app.py` in a terminal to see the traceback. |
| EXE build fails | Expected in v2.0: `build_exe.bat` is a placeholder. Use `run.bat`. |

## Version history (in this branch)

- **v2.0** — web UI (pywebview + CodeMirror 6), rich Markdown and image previews,
  Run/Submit sample logic, expanded C++ types and header ordering, new sample problems,
  auto-installed pywebview, and the fixes listed above.
- **v1.0** — Tkinter desktop judge with Python/C++/JavaScript support and the original
  sample problems.
