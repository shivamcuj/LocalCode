# LocalCode 2.3

LocalCode is a **Windows desktop, offline-first LeetCode-style practice judge**. Pick a
problem, write a solution in Python, C++ or JavaScript, and run it against local test
files. There is no account, no server and no cloud judging.

Version 2.3 is a **startup and serving fix**. The app is now served through pywebview's
local HTTP server instead of `file://`, the `Window` object is no longer exposed to
JavaScript, and the problem list/starter code load **without waiting** for the optional
CodeMirror CDN import. If CodeMirror eventually loads, the fallback textarea is upgraded
in place with the user's current code.

> The in-app badge still reads **2.2**, and `README_LOCALCODE.txt` is still titled
> "LOCALCODE WINDOWS 2.2" with a "Startup fix notes (v2.3)" section appended. Only the
> release branch is v2.3.

## What's new in v2.3

- **`Window` removed from the JS API.** `app.py` no longer stores `self.window` or assigns
  `api.window = window`. This avoids pywebview recursively inspecting native Windows
  accessibility objects during startup.
- **Served over HTTP instead of `file://`.** `main()` now `os.chdir(ROOT)`, passes
  `webui/index.html` to `create_window`, and lets pywebview auto-start its local HTTP
  server (`http://127.0.0.1:<port>/index.html`). The comment in the code cites
  file-origin restrictions on the ES modules used by CodeMirror.
- **Non-blocking startup.** `initializeLocalCode()` no longer begins with `await cmReady`.
  It wires the UI, loads the problem list and opens the selected problem immediately, so
  an offline or slow network shows the statement, starter code and textarea fallback
  right away.
- **In-place editor upgrade.** After `loadProblemList()` finishes, it awaits `cmReady` and
  — if CodeMirror loaded and an editor exists — re-creates the editor with the current
  text. Users no longer have to restart to get CodeMirror once the CDN import completes.
- **`README_LOCALCODE.txt`** gained a "Startup fix notes (v2.3)" section describing these
  three changes.
- **Sample solution files reformatted** (`user_solution.cpp` / `user_solution.js` under
  `problems/`). No behavior change.

## Fixed since v2.2

| v2.2 problem | Status in v2.3 |
| --- | --- |
| `api.window = window` could trigger recursive native-accessibility inspection and crash startup | **Fixed** — the `Window` reference is no longer attached to the API object |
| `initializeLocalCode()` awaited `cmReady`, so an offline/slow CDN could leave the problem statement and starter code blank for up to 12 s | **Fixed** — the UI and problem list load first; CodeMirror is awaited only for the optional upgrade |
| UI loaded from `file://`, which can block ES-module imports in WebView2 | **Fixed** — pywebview's local HTTP server serves the UI from `http://127.0.0.1` |
| A fallback textarea could not become CodeMirror without restarting the app | **Fixed** — the editor is upgraded in place once `cmReady` resolves, preserving the code |
| Offline users had to wait for an editor import that could not succeed | **Fixed** — the textarea appears immediately and remains usable |

## Still broken or carried over from v2.2

These are **not** fixed in v2.3. `engine.py` and `run.bat` are unchanged from v2.2.

1. **`indentOnInput` is still registered incorrectly — now with a worse failure mode.**
   `webui/src/main.js` passes `cm.indentOnInput` (the function) instead of
   `cm.indentOnInput()` (the extension). CodeMirror rejects the extension set with:

   ```text
   Unrecognized extension value in extension set (function indentOnInput() { ... })
   ```

   (verified against `@codemirror/state` + `@codemirror/language`). Because v2.3 now
   upgrades the working textarea *after* `cmReady`, this bug hits the upgrade path:
   `createEditor()` destroys the textarea, clears the editor host, then the `EditorView`
   constructor throws outside any `try/catch`. The result is an **empty editor pane** plus
   an "Application error: Unrecognized extension value in extension set" toast. If
   CodeMirror resolves before the first problem loads, the same error is caught by
   `loadProblem()` and shown as "Problem loading failed". Offline mode (textarea only) is
   unaffected.

2. **C++ `vector<...>` types still fail.** `engine.ctype()` accepts only `int`, `long`,
   `double`, `bool`, `string` and `T[]`; `vector<int>` raises `KeyError`.
   `problems/695-second-largest-element`, `702-largest-element` and `838-linear-search`
   declare `"types": {"nums": "vector<int>"}`, so C++ Run/Submit reports:

   ```text
   Runner failed: 'vector<int>'
   ```

   (re-verified). Python and JavaScript work for those problems.

3. **C++ standard headers are still emitted after user code.** `engine.py` writes
   `code + "\n" + CPP_HELP + main`. The `695`, `702` and `838` starters use `vector<int>`
   without includes, so they fail with `'vector' has not been declared` even when the type
   map is changed to `int[]` (re-verified).

4. **The full editor still needs the network on every launch.** CodeMirror is imported
   from `https://esm.sh`. Offline, proxied or DNS-blocked users keep the plain textarea:
   no highlighting, autocomplete, folding or bracket matching.

5. **Rich Markdown and image previews are still missing.** Headings, paragraphs,
   bold/italic, inline code, fenced code and simple bullets render. Links, images, ordered
   lists, blockquotes, horizontal rules and the click-to-zoom image modal do not.

6. **Run/Submit sample logic is still missing.** `run_test_count` is ignored.
   **Run executes every visible test**; **Submit** executes every test including hidden
   cases. The 205–245 visible tests in `695`/`702`/`838` make Run slow.

7. **`webui/package.json` is dead weight.** Its CodeMirror dependencies and esbuild script
   are unused at runtime, and `webui/dist/` is no longer loaded.

8. **The version badge is still `2.2`** in `webui/index.html`, and the
   `README_LOCALCODE.txt` title still says 2.2 even though v2.3 notes were appended.

9. **The editor upgrade replays unconditionally.** Even when CodeMirror was ready before
   the first problem loaded, `initializeLocalCode()` calls `createEditor()` again after
   `cmReady`, discarding the current cursor position and undo history. The upgrade call is
   not wrapped in `try/catch`, so a constructor failure cannot fall back to the textarea.

10. **`os.chdir(ROOT)` is process-wide.** It is harmless today because `engine.py` runs in
    temporary directories and `PROBLEMS_DIR` is absolute, but any future relative path
    would now resolve against the app root.

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
  README_LOCALCODE.txt    # plain-text 2.2 notes + v2.3 startup fixes
  README_GCC_FIX.txt      # MSYS2 GCC runtime-DLL note
  webui/
    index.html            # app shell; loads src/main.js
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

`run_test_count` may appear in older problem files but is **ignored in v2.3**: Run always
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

### C++ types accepted in v2.3

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

## Known issues and limitations (v2.3)

- **The editor can go blank after CodeMirror loads** because of the `indentOnInput`
  registration bug. The textarea fallback works, but the upgrade path throws. Fix:
  change `cm.indentOnInput` to `cm.indentOnInput()` in `webui/src/main.js`.
- **Full editor requires internet.** Without `esm.sh`, the textarea fallback is used.
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
- **Version strings are inconsistent:** badge and plain-text title say 2.2.

## Troubleshooting

| Symptom | Cause / fix |
| --- | --- |
| Editor is a plain textarea | CodeMirror could not be fetched from `esm.sh` (offline, proxy, DNS). Reconnect and restart for the full editor. |
| Editor briefly works, then goes blank + "Application error: Unrecognized extension value..." | The v2.3 upgrade path hit the `cm.indentOnInput` bug. Change it to `cm.indentOnInput()` in `webui/src/main.js`. |
| `Unrecognized extension value in extension set` | Same cause: a CodeMirror extension factory is passed instead of being called. |
| "Problem loading failed" right after startup | CodeMirror resolved before the first problem and `createEditor()` threw on `indentOnInput`; check the browser/webview console. |
| Problems load but no highlighting | Expected in fallback mode; CodeMirror is optional and loaded from the CDN. |
| C++: `Runner failed: 'vector<int>'` | `ctype()` does not support `vector<int>`. Use `int[]` in `types` **and** add `#include <bits/stdc++.h>` to your code. |
| C++: `'vector' has not been declared` | Headers are emitted after user code. Add the include at the top of your solution. |
| "LocalCode could not start" / webview initialization error | Install or repair the Microsoft Edge WebView2 Evergreen Runtime. |
| Window stays blank after the HTTP-serving change | Check that `webui/index.html` exists, then run `python app.py` in a terminal to see the pywebview traceback. |
| `g++ was not found...` | Install MSYS2 UCRT64 GCC and add `C:\msys64\ucrt64\bin` to `PATH`. |
| `cc1plus.exe - Entry Point Not Found` / `libgcc_s_seh-1.dll` missing | MSYS2 runtime DLLs are not on the child-process `PATH`; only default `C:\msys64` locations are auto-added. See `README_GCC_FIX.txt`. |
| `Node.js not found...` warning at launch | Harmless for Python/C++. Install Node.js LTS only if you need JavaScript judging. |
| `tests.json needs a "types" map ... for C++` | Add `types` (and ideally `returns`) for that problem. |
| `Python 3 was not found.` | Python is not installed or `py`/`python` is not on `PATH`. |
| `LocalCode closed with an error.` | Run `python app.py` in a terminal to see the traceback. |
| EXE build fails | Expected: `build_exe.bat` is a placeholder. Use `run.bat`. |

## Version history (this branch)

- **v2.3** — removes the `Window` reference from the JS API, serves the UI through
  pywebview's local HTTP server, loads problems/starter code without waiting for the
  CodeMirror CDN, and upgrades the fallback textarea in place. C++ vector types, header
  ordering, `indentOnInput`, rich Markdown/images and `run_test_count` remain unfixed.
- **v2.2** — removes the npm/esbuild build step, loads `src/main.js` directly, restores
  CDN CodeMirror with a 12-second timeout and textarea fallback, makes Node.js optional
  for launch, and fixes the version badge.
- **v2.1** — locally bundled CodeMirror via esbuild (`webui/dist/app.js`), automated
  first-run build in `run.bat`, Node.js as a hard requirement.
- **v2.0** — pywebview + CodeMirror web UI with CDN imports, rich Markdown and image
  previews, Run sample logic (`run_test_count`), expanded C++ types and header ordering.
- **v1.0** — Tkinter desktop judge with Python/C++/JavaScript support.
