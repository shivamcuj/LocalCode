# LocalCode 2.4

LocalCode is a **Windows desktop, offline-first LeetCode-style practice judge**. Pick a
problem, write a solution in Python, C++ or JavaScript, and run it against local test
files. There is no account, no server and no cloud judging.

Version 2.4 is an **editor reliability fix** built on the v2.3 startup work. The
CodeMirror extension registration bug that produced
`Unrecognized extension value in extension set` is fixed, and CodeMirror initialization is
now wrapped in a fallback path, so a failure no longer destroys the editor pane or blocks
problem loading.

> The in-app badge now reads **2.4**. `README_LOCALCODE.txt` still has the
> "LOCALCODE WINDOWS 2.2" title, but its v2.3 startup notes and new "VERSION 2.4 FIX"
> section are present.

## What's new in v2.4

- **`indentOnInput` registered correctly.** `webui/src/main.js` now passes
  `cm.indentOnInput()` (the extension) instead of `cm.indentOnInput` (the factory
  function). This is the actual fix for the CodeMirror startup error.
- **Reusable fallback editor.** The textarea fallback moved into
  `createFallbackEditor(doc, reason)`, used both when the CDN import fails and when the
  `EditorView` constructor throws. The reason is shown in a toast.
- **Resilient editor construction.** The `new cm.EditorView({...})` call is wrapped in
  `try/catch`. On failure, the error is logged and the textarea fallback is created
  instead of leaving an empty editor host.
- **Version badge bumped** from `2.2` to `2.4` in `webui/index.html`.
- **Release notes** in `README_LOCALCODE.txt` gained a "VERSION 2.4 FIX" section.

## Fixed since v2.3

| v2.3 problem | Status in v2.4 |
| --- | --- |
| `Unrecognized extension value in extension set` from passing `cm.indentOnInput` uncalled | **Fixed** — `cm.indentOnInput()` is called; verified against `@codemirror/state` + `@codemirror/language` |
| CodeMirror upgrade destroyed the working textarea and left the editor pane blank | **Fixed** — the constructor now succeeds; if it does not, the fallback is recreated |
| An editor-initialization failure blocked problem loading | **Fixed** — construction is caught and falls back to the textarea |
| The fallback only covered a failed CDN import, not a failed `EditorView` | **Fixed** — `createFallbackEditor()` handles both, with an error-reason toast |
| In-app badge still said `2.2` | **Fixed** — badge says `2.4` |

## Still broken or carried over from v2.3

These are **not** fixed in v2.4. `app.py`, `engine.py` and `run.bat` are unchanged from
v2.3.

1. **C++ `vector<...>` types still fail.** `engine.ctype()` accepts only `int`, `long`,
   `double`, `bool`, `string` and `T[]`; `vector<int>` raises `KeyError`.
   `problems/695-second-largest-element`, `702-largest-element` and `838-linear-search`
   declare `"types": {"nums": "vector<int>"}`, so C++ Run/Submit reports:

   ```text
   Runner failed: 'vector<int>'
   ```

   (re-verified). Python and JavaScript work for those problems.

2. **C++ standard headers are still emitted after user code.** `engine.py` writes
   `code + "\n" + CPP_HELP + main`. The `695`, `702` and `838` starters use `vector<int>`
   without includes, so they fail with `'vector' has not been declared` even when the type
   map is changed to `int[]` (re-verified).

3. **The full editor still needs the network on every launch.** CodeMirror is imported
   from `https://esm.sh`. Offline, proxied or DNS-blocked users keep the plain textarea:
   no highlighting, autocomplete, folding or bracket matching. The fallback textarea also
   has no Tab-to-indent handling.

4. **Rich Markdown and image previews are still missing.** Headings, paragraphs,
   bold/italic, inline code, fenced code and simple bullets render. Links, images, ordered
   lists, blockquotes, horizontal rules and the click-to-zoom image modal do not.

5. **Run/Submit sample logic is still missing.** `run_test_count` is ignored.
   **Run executes every visible test**; **Submit** executes every test including hidden
   cases. The 205–245 visible tests in `695`/`702`/`838` make Run slow.

6. **`webui/package.json` is dead weight.** Its CodeMirror dependencies and esbuild script
   are unused at runtime, and `webui/dist/` is no longer loaded.

7. **`README_LOCALCODE.txt` title still says 2.2** even though v2.3 and v2.4 notes were
   appended.

8. **The editor upgrade still replays unconditionally.** After `await cmReady`,
   `initializeLocalCode()` calls `createEditor()` again whenever `cm` and an editor exist —
   even if CodeMirror was already active. That discards cursor position and undo history.
   If the first CodeMirror attempt failed, the replay retries and can show the fallback
   toast twice.

9. **`os.chdir(ROOT)` is process-wide.** It is harmless today because `engine.py` runs in
   temporary directories and `PROBLEMS_DIR` is absolute, but any future relative path
   would resolve against the app root.

## Still open from earlier versions

- `returns` is still not validated for C++; only `types` is checked, though the error text
  mentions both.
- Problem ids are sorted as strings (`str(id)`), so `1000` would sort before `695`.
- The MSYS2 GCC workaround only adds the default `C:\msys64\ucrt64\bin` and
  `C:\msys64\usr\bin` paths to the child-process `PATH`.
- `run.bat` prefers `py -3`, while `engine.py` resolves `python` first; the judge can use a
  different interpreter than the launcher.
- Python/JavaScript runner exit codes are ignored; a crash before `out.json` surfaces only
  as `Runner failed: ...`.
- Submissions are not sandboxed. Only the per-case timeout limits them.
- `unordered` still only sorts a top-level list.
- Every Run/Submit writes `user_solution.<ext>` into the problem folder.
- `run.bat` only checks that `webview` imports; it does not enforce
  `pywebview>=5.4,<7`.
- `build_exe.bat` is still a placeholder; there is no standalone EXE build.
- `difficulty: "Basic"` still gets the default green pill (CSS defines only `medium` and
  `hard`).
- `list_problems` rescans the folder on every call, so indices can shift if folders change
  while the app is open.
- No root `.gitignore` for `__pycache__/`, `user_solution.*` or `webui/dist/`.
- `README_LOCALCODE.txt` still contains stale lines about the "first-time editor build"
  and `webui\dist` from v2.1.

## Requirements (Windows)

- Windows 10/11.
- **Python 3** with `py` or `python` on `PATH`.
- **Microsoft Edge WebView2 Runtime** — normally present on current Windows; install the
  Evergreen Runtime if LocalCode reports that the webview could not start.
- **g++** (MSYS2 UCRT64 recommended) — only for C++ judging.
- **Node.js LTS** — only for JavaScript judging (not required to launch).
- **Internet access** for the full CodeMirror editor. Without it, LocalCode uses the
  textarea fallback.

## Quick start

1. Extract the folder (do not run from inside a ZIP preview).
2. Double-click **`run.bat`**.
   - It locates Python (prefers `py -3`, then `python`).
   - If `node` is missing, it prints a warning and continues.
   - If `import webview` fails, it runs `pip install -r requirements.txt`.
   - It starts `app.py`.
3. Select a problem, choose a language, write code, then **Run** or **Submit**.

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
  app.py                  # pywebview shell, HTTP-served UI, JavaScript API, Run/Submit
  engine.py               # judge: Python/JS runners, C++ codegen, compile & execute
  requirements.txt        # pywebview>=5.4,<7
  run.bat                 # Python check, optional Node warning, pywebview install, launch
  build_exe.bat           # placeholder (no EXE build)
  README.md               # this file
  README_LOCALCODE.txt    # plain-text 2.2 notes + v2.3/v2.4 fix notes
  README_GCC_FIX.txt      # MSYS2 GCC runtime-DLL note
  webui/
    index.html            # app shell; loads src/main.js; badge 2.4
    style.css             # dark theme, markdown styles, .fallback-editor
    src/main.js           # UI logic, markdown renderer, CDN CodeMirror loader/fallback
    package.json          # vestigial CodeMirror deps + unused esbuild script
    .gitignore            # node_modules/
  problems/
    001-two-sum/          # return-value example (4 tests, 2 hidden)
    695-second-largest-element/   # 239 tests; C++ currently broken
    702-largest-element/          # 205 tests; C++ currently broken
    838-linear-search/            # 245 tests; C++ currently broken
    984-pattern4/                 # stdout ("print the answer") example
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

| Field         | Meaning                                                                       |
| ------------- | ----------------------------------------------------------------------------- |
| `difficulty`  | `Easy`, `Medium` or `Hard`; `Basic` also appears and uses the default colour   |
| `unordered`   | `true` → compare a top-level list result ignoring order                        |
| `timeout`     | Per-case timeout in seconds (default `10`)                                     |
| `output_mode` | `"stdout"` → compare captured printed output; anything else compares the return value |
| `types`       | **Required for C++**: map of parameter name → type                             |
| `returns`     | Documented for C++ but currently not validated                                 |

A test can set `"hidden": true`; hidden cases run only on **Submit**.

`run_test_count` may appear in older problem files but is **ignored in v2.4**: Run always
executes all non-hidden tests.

Example:

```json
{
  "id": 1,
  "title": "Two Sum",
  "difficulty": "Easy",
  "method": "twoSum",
  "unordered": true,
  "timeout": 10,
  "tests": [
    { "input": { "nums": [2, 7, 11, 15], "target": 9 }, "expected": [0, 1] },
    { "input": { "nums": [3, 3], "target": 6 }, "expected": [0, 1], "hidden": true }
  ],
  "types": { "nums": "int[]", "target": "int" },
  "returns": "int[]"
}
```

### C++ types accepted in v2.4

| JSON type | C++ type     |
| --------- | ------------ |
| `int`     | `int`        |
| `long`    | `long long`  |
| `double`  | `double`     |
| `bool`    | `bool`       |
| `string`  | `string`     |
| `T[]`     | `vector<T>`  |

Nested shorthand works (`int[][]` → `vector<vector<int>>`). Long forms such as
`vector<int>` or `std::vector<int>` do **not** work and are reported as
`Runner failed: 'vector<int>'`.

### Starter code and includes

The generated C++ file order is:

```text
<your code>
<bits/stdc++.h> + reader/writer helpers
main()
```

Because the headers come **after** your code, a starter that uses `vector<int>` without
its own `#include` will not compile. Add `#include <bits/stdc++.h>` at the top of C++
solutions until the ordering is fixed.

### Markdown in `problem.md`

Supported: headings (`#`, `##`, `###`), paragraphs, **bold**, *italic*, inline code,
fenced code blocks and simple `-`/`*` bullet lines. Links, images, blockquotes, ordered
lists and horizontal rules are not rendered. Raw HTML is escaped.

## How the judge works

Every Run/Submit:

1. Saves the editor draft in memory and writes `user_solution.<ext>` into the problem
   folder.
2. Calls `engine.judge(...)` with the selected language and the test list.
3. Runs everything in a fresh temporary directory and returns per-case results.

- **Python** — the solution is `exec`'d in a namespace that pre-imports `typing`,
  `collections`, `math`, `heapq`, `itertools`, `functools` and `bisect`, then
  `Solution().<method>(**input)` is called. `stdout` is captured per case.
- **C++** — compiles with `g++ -O2 -std=c++17` (120 s allowed), feeds each case's
  arguments on stdin and reads the result from `result.json`. In `stdout` mode, `cout` is
  captured and written as a JSON string.
- **JavaScript** — the file is wrapped with `new Function(...)`, `Solution` is
  instantiated per case, and `console.log` is captured.

**Run** executes all visible tests. **Submit** executes every test, including hidden ones.

Verdicts: `Accepted`, `Wrong Answer`, `Runtime Error`, `Time Limit Exceeded`,
`Execution Error` (setup/compile failure).

## Known issues and limitations (v2.4)

- **Full editor requires internet.** Without `esm.sh`, the textarea fallback is used and
  CodeMirror features are unavailable.
- **C++ is broken for `695`, `702`, `838`** — `vector<int>` types are rejected and
  headerless starters do not compile. Use Python or JavaScript for those problems, or
  rewrite the type map and add the include manually.
- **Drafts are memory-only.** `save_draft` keeps code in the Python process; closing the
  app loses unsaved drafts. Only `user_solution.<ext>` is written to disk.
- **`user_solution.*` files pollute the problem folders.**
- **Run can be slow on the large samples** because it executes all visible tests.
- **`run.bat` does not enforce `pywebview>=5.4`.** It only checks that `webview` imports.
- **`build_exe.bat` is a placeholder.** Use `run.bat` from the source folder.
- **No root `.gitignore`** for generated files.
- **Plain-text title still says 2.2.**

## Troubleshooting

| Symptom | Cause / fix |
| --- | --- |
| Editor is a plain textarea | CodeMirror could not be fetched from `esm.sh` (offline, proxy, DNS). The toast explains the reason. Reconnect and restart for the full editor. |
| "CodeMirror could not initialize; using the built-in editor..." | The `EditorView` constructor threw. The textarea is active; the toast/console contains the underlying error. |
| Problems/drafts work but no highlighting or Tab indent | Expected in fallback mode; those features require CodeMirror. |
| C++: `Runner failed: 'vector<int>'` | `ctype()` does not support `vector<int>`. Use `int[]` in `types` **and** add `#include <bits/stdc++.h>` to your code. |
| C++: `'vector' has not been declared` | Headers are emitted after user code. Add the include at the top of your solution. |
| "LocalCode could not start" / webview initialization error | Install or repair the Microsoft Edge WebView2 Evergreen Runtime. |
| Window stays blank | Check that `webui/index.html` exists, then run `python app.py` in a terminal to see the pywebview traceback. |
| `g++ was not found...` | Install MSYS2 UCRT64 GCC and add `C:\msys64\ucrt64\bin` to `PATH`. |
| `cc1plus.exe - Entry Point Not Found` / `libgcc_s_seh-1.dll` missing | MSYS2 runtime DLLs are not on the child-process `PATH`; only default `C:\msys64` locations are auto-added. See `README_GCC_FIX.txt`. |
| `Node.js not found...` warning at launch | Harmless for Python/C++. Install Node.js LTS only if you need JavaScript judging. |
| `tests.json needs a "types" map ... for C++` | Add `types` (and ideally `returns`) for that problem. |
| `Python 3 was not found.` | Python is not installed or `py`/`python` is not on `PATH`. |
| `LocalCode closed with an error.` | Run `python app.py` in a terminal to see the traceback. |
| EXE build fails | Expected: `build_exe.bat` is a placeholder. Use `run.bat`. |

## Version history (this branch)

- **v2.4** — fixes CodeMirror `indentOnInput` registration (`cm.indentOnInput()`), adds a
  shared textarea fallback for both CDN and constructor failures, and bumps the badge to
  2.4. C++ vector types, header ordering, rich Markdown/images and `run_test_count`
  remain unfixed.
- **v2.3** — removes the `Window` reference from the JS API, serves the UI through
  pywebview's local HTTP server, loads problems/starter code without waiting for the
  CodeMirror CDN, and upgrades the fallback textarea in place.
- **v2.2** — removes the npm/esbuild build step, loads `src/main.js` directly, restores
  CDN CodeMirror with a 12-second timeout and textarea fallback, makes Node.js optional
  for launch, and fixes the version badge.
- **v2.1** — locally bundled CodeMirror via esbuild (`webui/dist/app.js`), automated
  first-run build in `run.bat`, Node.js as a hard requirement.
- **v2.0** — pywebview + CodeMirror web UI with CDN imports, rich Markdown and image
  previews, Run sample logic (`run_test_count`), expanded C++ types and header ordering.
- **v1.0** — Tkinter desktop judge with Python/C++/JavaScript support.
