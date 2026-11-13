# LocalCode 2.2

LocalCode is a **Windows desktop, offline-first LeetCode-style practice judge**. Pick a
problem, write a solution in Python, C++ or JavaScript, and run it against local test
files. There is no account, no server and no cloud judging.

Version 2.2 keeps the **pywebview shell + CodeMirror 6 interface**, but reverses the v2.1
delivery change: the editor is **no longer bundled with npm/esbuild**. `webui/index.html`
loads `webui/src/main.js` directly, and that file imports CodeMirror 6 from `esm.sh` at
launch. If the CDN cannot be reached, LocalCode falls back to a built-in **textarea
editor**, so problems, Run and Submit keep working.

> The in-app badge now reads **2.2** (v2.1 still showed `2.0`), and
> `README_LOCALCODE.txt` is titled "LOCALCODE WINDOWS 2.2".

## What's new in v2.2

- **No build step.** `run.bat` no longer runs `npm install` or `npm run build`, and no
  longer requires `webui/dist/app.js` to exist. The source is served as-is.
- **Direct source loading.** `webui/index.html` now uses `<script src="src/main.js">`
  instead of the generated `dist/app.js`.
- **CDN CodeMirror with timeout.** `webui/src/main.js` dynamically imports CodeMirror 6
  modules from `https://esm.sh` (core, view, language, commands, Python/C++/JavaScript
  modes, one-dark). A 12-second timeout guards startup.
- **Restored fallback editor.** When CodeMirror cannot load, a styled `<textarea>`
  (`.fallback-editor`, re-added to `webui/style.css`) replaces it. The user is told via
  toast that CodeMirror features need an internet connection.
- **Node.js is optional again.** `run.bat` only prints a warning when `node` is missing;
  Python and C++ users can launch without it. JavaScript judging still needs Node.js.
- **Version badge corrected.** The header now shows `2.2`.
- **Startup ordering.** `initializeLocalCode()` waits for the CodeMirror import attempt
  (`await cmReady`) before wiring the UI, then loads the problem list.

## Fixed since v2.1

| v2.1 problem | Status in v2.2 |
| --- | --- |
| A missing `webui/dist/app.js` left the page as static HTML with no problem list | **Fixed** — the page loads `src/main.js` directly; no build artifact is needed |
| `run.bat` exited when Node.js was absent, even for Python/C++-only users | **Fixed** — Node.js is now a warning; the app still launches |
| Editor had no fallback; a failed bundle left an unusable editor pane | **Fixed** — a styled textarea fallback is restored (problem loading, Run and Submit still work) |
| First launch required internet for `npm install` and could abort on registry errors | **Fixed** — no npm step at all; internet is only needed for the full CodeMirror editor |
| Node.js was a hard launch requirement | **Fixed** — only JavaScript judging needs it now |
| In-app version badge said `2.0` while the release was v2.1 | **Fixed** — badge says `2.2` |
| `README_LOCALCODE.txt` described the esbuild/dist workflow | **Updated** — the release notes now describe CDN modules + offline fallback |

## Still broken or regressed from v2.1

These were **not** fixed in v2.2. `app.py` and `engine.py` are unchanged from v2.1.

1. **C++ `vector<...>` types still fail.** `engine.ctype()` accepts only `int`, `long`,
   `double`, `bool`, `string` and `T[]`; `vector<int>` raises `KeyError`.
   `problems/695-second-largest-element`, `702-largest-element` and `838-linear-search`
   declare `"types": {"nums": "vector<int>"}`, so C++ Run/Submit reports:

   ```text
   Runner failed: 'vector<int>'
   ```

   (verified with `engine.ctype` / `engine.judge`). Python and JavaScript work for those
   problems.

2. **C++ standard headers are still emitted after user code.** `engine.py` writes
   `code + "\n" + CPP_HELP + main`. The `695`, `702` and `838` C++ starters use
   `vector<int>` without includes, so they fail with `'vector' has not been declared` even
   if the type map is changed to `int[]` (verified).

3. **`indentOnInput` is still registered incorrectly.** `webui/src/main.js` passes
   `cm.indentOnInput` (the function) instead of `cm.indentOnInput()` (the extension). This
   raises CodeMirror's `Unrecognized extension value in extension set` error when a
   problem is opened. The new textarea fallback only covers a failed **CDN import**; it
   does not catch an `EditorView` constructor failure, so this bug can still leave the
   editor pane empty or show "Problem loading failed".

4. **The full editor needs the network on every launch.** CodeMirror is imported from
   `https://esm.sh` each time. Offline, proxied or DNS-blocked users get the plain
   textarea: no syntax highlighting, autocomplete, folding or bracket matching. If
   `esm.sh` hangs instead of failing fast, startup can wait up to the 12-second timeout
   because the UI awaits `cmReady`.

5. **`api.window = window` is still present.** `app.py` attaches the pywebview `Window`
   to the JS API object, which previously caused recursive inspection of native Windows
   accessibility objects and startup failures. The safer v2.0 behavior (no window
   reference) has not been restored.

6. **Rich Markdown and image previews are still missing.** Headings, paragraphs,
   bold/italic, inline code, fenced code and simple `-`/`*` bullets render. Links, images,
   ordered lists, blockquotes, horizontal rules and the click-to-zoom image modal do not.

7. **Run/Submit sample logic is still missing.** `run_test_count` is ignored.
   **Run executes every visible test**; **Submit** executes every test including hidden
   cases. With 205–245 visible tests in `695`/`702`/`838`, Run can be slow.

8. **`webui/package.json` is now dead weight.** Its CodeMirror dependencies and esbuild
   build script are unused at runtime; `webui/dist/` is no longer loaded. Keeping them is
   harmless but can mislead.

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
- `README_LOCALCODE.txt` still mentions the "first-time editor build" and `webui\dist`
  in its requirements/troubleshooting sections; those lines are stale for v2.2.

## Requirements (Windows)

- Windows 10/11.
- **Python 3** with `py` or `python` on `PATH`.
- **Microsoft Edge WebView2 Runtime** — normally present on current Windows; install the
  Evergreen Runtime if LocalCode reports that the webview could not start.
- **g++** (MSYS2 UCRT64 recommended) — only for C++ judging.
- **Node.js LTS** — only for JavaScript judging (no longer required to launch).
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

There is **no npm install and no build step** in v2.2.

## Repository layout

```text
LocalCode/
  app.py                  # pywebview shell, JavaScript API, problem loading, Run/Submit
  engine.py               # judge: Python/JS runners, C++ codegen, compile & execute
  requirements.txt        # pywebview>=5.4,<7
  run.bat                 # Python check, optional Node warning, pywebview install, launch
  build_exe.bat           # placeholder (no EXE build)
  README.md               # this file
  README_LOCALCODE.txt    # plain-text 2.2 install notes
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

`run_test_count` may appear in older problem files but is **ignored in v2.2**: Run always
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

### C++ types accepted in v2.2

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

## Known issues and limitations (v2.2)

- **Full editor requires internet.** CodeMirror is fetched from `esm.sh` each launch; the
  textarea fallback has no highlighting/autocomplete. A hanging CDN request can delay
  startup up to 12 seconds.
- **Editor initialization can still fail** because of the `indentOnInput` bug. The
  fallback does not cover `EditorView` constructor errors.
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

## Troubleshooting

| Symptom | Cause / fix |
| --- | --- |
| Editor is a plain textarea | CodeMirror could not be fetched from `esm.sh` (offline, proxy, DNS, or 12 s timeout). Reconnect and restart for the full editor. |
| `Unrecognized extension value in extension set` | `cm.indentOnInput` is passed instead of `cm.indentOnInput()` in `webui/src/main.js`. Change it to a call. |
| Blank editor / "Problem loading failed" | Could be the `indentOnInput` bug or a failed CDN import. Open DevTools/webview console for the exact error. |
| C++: `Runner failed: 'vector<int>'` | `ctype()` does not support `vector<int>`. Use `int[]` in `types` **and** add `#include <bits/stdc++.h>` to your code. |
| C++: `'vector' has not been declared` | Headers are emitted after user code. Add the include at the top of your solution. |
| "LocalCode could not start" / webview initialization error | Install or repair the Microsoft Edge WebView2 Evergreen Runtime. The `api.window = window` assignment may also be involved; removing it reduces startup risk. |
| `g++ was not found...` | Install MSYS2 UCRT64 GCC and add `C:\msys64\ucrt64\bin` to `PATH`. |
| `cc1plus.exe - Entry Point Not Found` / `libgcc_s_seh-1.dll` missing | MSYS2 runtime DLLs are not on the child-process `PATH`; only default `C:\msys64` locations are auto-added. See `README_GCC_FIX.txt`. |
| `Node.js not found...` warning at launch | Harmless for Python/C++. Install Node.js LTS only if you need JavaScript judging. |
| `tests.json needs a "types" map ... for C++` | Add `types` (and ideally `returns`) for that problem. |
| `Unsupported C++ input type '...'` | Not currently reached for `vector<int>` (it raises `KeyError` first). Use a supported shorthand such as `int[]`. |
| `Python 3 was not found.` | Python is not installed or `py`/`python` is not on `PATH`. |
| `LocalCode closed with an error.` | Run `python app.py` in a terminal to see the traceback. |
| EXE build fails | Expected: `build_exe.bat` is a placeholder. Use `run.bat`. |

## Version history (this branch)

- **v2.2** — removes the npm/esbuild build step, loads `src/main.js` directly, restores
  CDN CodeMirror with a 12-second timeout and textarea fallback, makes Node.js optional
  for launch, fixes the version badge, and updates the plain-text release notes. C++
  vector types, header ordering, `indentOnInput`, `api.window`, rich Markdown/images and
  `run_test_count` remain unfixed.
- **v2.1** — locally bundled CodeMirror via esbuild (`webui/dist/app.js`), automated
  first-run build in `run.bat`, Node.js as a hard requirement. Introduced the C++,
  Markdown/image and editor regressions listed above.
- **v2.0** — pywebview + CodeMirror web UI with CDN imports, rich Markdown and image
  previews, Run sample logic (`run_test_count`), expanded C++ types and header ordering.
- **v1.0** — Tkinter desktop judge with Python/C++/JavaScript support.
