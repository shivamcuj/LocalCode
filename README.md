# LocalCode 2.1

LocalCode is a **Windows desktop, offline LeetCode-style practice judge**. Pick a problem,
write a solution in Python, C++ or JavaScript, and run it against local test files. There
is no account, server or cloud judging.

Version 2.1 keeps the **pywebview desktop shell + CodeMirror 6 UI** introduced in v2.0,
but changes how the editor is delivered: the CodeMirror modules are now bundled locally by
**esbuild** and loaded from `webui/dist/app.js` instead of being imported from `esm.sh` on
every launch. `run.bat` performs the one-time npm build, after which the editor works
offline.

> The in-app badge reads **2.0** on this branch (the version string was not bumped), and
> `README_LOCALCODE.txt` still calls the release "2.0". The branch/release is **v2.1**.

## What's new in v2.1

- **Locally bundled editor.** `webui/src/main.js` now uses normal ES imports from
  `codemirror`, `@codemirror/view`, `@codemirror/language`, `@codemirror/commands`, the
  Python/C++/JavaScript language packages and `one-dark`. esbuild bundles everything into
  `webui/dist/app.js`; `index.html` loads that one file.
- **Offline editing after setup.** No runtime CDN request and no `esm.sh` dependency. Once
  `webui/dist/app.js` exists, the full CodeMirror UI can start without internet.
- **Automated first-run build.** `run.bat` checks for `webui\dist\app.js`; if missing it
  runs `npm install --no-audit --no-fund` and `npm run build` inside `webui/`, verifies
  that the bundle was produced, and stops with a clear error otherwise.
- **Node.js check promoted to a hard requirement.** The launcher exits if Node.js is
  missing (previously it only warned).
- **UI simplification.** The editor host, results table, verdict badge, problem picker,
  Refresh/Open-folder buttons, toasts and Ctrl+Enter / Ctrl+Shift+Enter shortcuts remain.
- `README_LOCALCODE.txt` rewritten as short 2.0/2.1 install notes.

## Fixed since v2.0

| v2.0 issue | v2.1 status |
| --- | --- |
| Full editor required `https://esm.sh` at every launch; offline users got the plain textarea fallback | **Fixed** — CodeMirror is bundled locally and loaded from `webui/dist/app.js` |
| No automated editor build; a missing `dist/app.js` could leave the app unusable | **Fixed** — `run.bat` builds the bundle on first launch and validates the output |
| CDN import timeout (12 s) and network-dependent editor startup | **Removed** — the bundle is local, so there is no CDN timeout path |

## Regressions and removals in v2.1

These are present in the current working tree and were **not** in the v2.0 commit. They
are documented so they are not mistaken for fixed behavior.

1. **C++ `vector<...>` types fail again.** `engine.ctype()` was reverted to the v1.0
   implementation and only accepts `int`, `long`, `double`, `bool`, `string` and `T[]`.
   Problems `695`, `702` and `838` declare `"types": {"nums": "vector<int>"}`, so C++
   Run/Submit returns:
   `Runner failed: 'vector<int>'`
   (verified with `engine.judge`).

2. **C++ helper headers are appended after user code again.**
   `engine.py` writes `code + "\n" + CPP_HELP + main`. The `695`, `702` and `838`
   starters use `vector<int>` without includes, so compilation fails with
   `'vector' has not been declared` even if the type map is changed to `int[]`
   (verified).

3. **CodeMirror `indentOnInput` is registered incorrectly.** `webui/src/main.js` passes
   the function itself (`indentOnInput`) instead of calling it (`indentOnInput()`).
   In CodeMirror 6 it is `indentOnInput(): Extension`, so this produces the
   `Unrecognized extension value in extension set` error that v2.4 of the previous line
   fixed. The editor can fail to initialize as soon as a problem is loaded.

4. **No fallback editor.** v2.0 caught CodeMirror load/initialization failures and
   replaced the editor with a textarea. v2.1 has no fallback: if `dist/app.js` is missing
   or the editor constructor throws, the editor area stays empty/unusable.

5. **`api.window = window` was re-added.** The v2.3 startup fix explicitly removed the
   pywebview `Window` reference from the JS API object to avoid recursive inspection of
   native Windows accessibility objects. `app.py` now attaches it again, reintroducing
   that startup-crash risk.

6. **Rich Markdown and image previews were removed.** The v2.0 renderer supported links,
   ordered lists, blockquotes, horizontal rules, local/remote images and a click-to-zoom
   image modal (plus `resolve_image()` in `app.py`). v2.1 renders only headings,
   paragraphs, bold/italic, inline code, fenced code, and simple bullet lines. There are
   no images in statements and no image-preview modal.

7. **Run/Submit sample logic was removed.** `run_test_count` is gone from `app.py` and the
   sample `tests.json` files. **Run now executes every visible test**, not the first 2–4;
   `run_test_count` in a problem file is ignored. **Submit** still runs everything,
   including hidden tests.

8. **Node.js is now mandatory for everyone.** `run.bat` exits when `node` is not on
   `PATH`, even for users who only write Python or C++ and already have a built
   `dist/app.js`.

9. **`webui/dist/app.js` is not committed.** `index.html` loads `dist/app.js`, but the
   `dist` directory is empty in the repo. Launching `python app.py` directly before
   running `run.bat` leaves the page without JavaScript (only static HTML appears). The
   first `run.bat` launch fixes this by building the bundle.

## Still open from earlier versions

- `returns` is still not validated for C++; only `types` is checked.
- Problem ids are still sorted as strings (`str(id)`), so `1000` sorts before `695`.
- The MSYS2 GCC runtime workaround still covers only the default `C:\msys64` paths.
- `run.bat` prefers `py -3` while `engine.py` prefers `python`; the judge may use a
  different interpreter than the launcher.
- Python/JavaScript runner exit codes are still ignored; a crash before `out.json` shows
  only `Runner failed: ...`.
- Submissions are still not sandboxed; only the per-case timeout limits them.
- `unordered` still only sorts a top-level list.
- Every Run/Submit still writes `user_solution.<ext>` into the problem folder.
- `run.bat` still checks only that `webview` imports, not that it meets
  `pywebview>=5.4,<7`.
- `build_exe.bat` is still a placeholder; there is no working standalone EXE build.
- `difficulty: "Basic"` still receives the default green pill (CSS only defines
  `medium` and `hard`).
- `list_problems` rescans the problems folder on every call, so indices can shift if
  folders change while the app is open.
- There is no root `.gitignore` for `__pycache__/`, `user_solution.*` or the generated
  `webui/dist/`.

## Requirements (Windows)

- Windows 10/11.
- **Python 3** with `py` or `python` on `PATH`.
- **Node.js LTS** — now required by `run.bat` for the editor build check and JavaScript
  judging.
- **Microsoft Edge WebView2 Runtime** — normally present on current Windows; install the
  Evergreen Runtime if LocalCode reports the webview could not start.
- **g++** (MSYS2 UCRT64 recommended) — only for C++ judging.
- Internet access on the **first** launch for `npm install`; after `webui/dist/app.js`
  exists, no network is needed for editing.

## Quick start

1. Extract the folder (do not run from inside a ZIP preview).
2. Double-click **`run.bat`**.
   - It locates Python.
   - It requires Node.js and exits with instructions if `node` is missing.
   - If `webui\dist\app.js` does not exist, it installs npm dependencies and builds the
     editor bundle.
   - If `import webview` fails, it runs `pip install -r requirements.txt`.
   - It starts `app.py`.
3. Select a problem, choose a language, write code, then **Run** or **Submit**.

Manual start (after the one-time build):

```bat
python -m pip install -r requirements.txt
python app.py
```

Node/npm commands used by the launcher:

```bat
cd webui
npm install --no-audit --no-fund
npm run build
```

There is no working EXE packaging in this release. `build_exe.bat` only prints a notice.

## Repository layout

```text
LocalCode/
  app.py                  # pywebview shell, JavaScript API, problem loading, Run/Submit
  engine.py               # judge: Python/JS runners, C++ codegen, compile & execute
  requirements.txt        # pywebview>=5.4,<7
  run.bat                 # Python/Node checks, editor build, pywebview install, launch
  build_exe.bat           # placeholder (no EXE build)
  README.md               # this file
  README_LOCALCODE.txt    # short install/version notes
  README_GCC_FIX.txt      # MSYS2 GCC runtime-DLL note
  webui/
    index.html            # app shell; loads dist/app.js
    style.css             # dark theme
    src/main.js           # CodeMirror setup + UI logic (bundled by esbuild)
    dist/app.js           # generated bundle (not present until npm run build)
    package.json          # CodeMirror deps + esbuild build script
    .gitignore            # node_modules/
  problems/
    001-two-sum/
    695-second-largest-element/   # C++ currently broken, see regressions
    702-largest-element/          # C++ currently broken, see regressions
    838-linear-search/            # C++ currently broken, see regressions
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

| Field    | Meaning                                                       |
| -------- | ------------------------------------------------------------- |
| `id`     | Problem number/identifier (currently sorted as a string)      |
| `title`  | Title shown in the picker                                     |
| `method` | Method name on the `Solution` class that the judge calls      |
| `tests`  | Non-empty array of `{ "input": {...}, "expected": ... }` cases |

Optional fields:

| Field         | Meaning                                                                 |
| ------------- | ----------------------------------------------------------------------- |
| `difficulty`  | `Easy`, `Medium` or `Hard`; `Basic` also appears and uses the default colour |
| `unordered`   | `true` → compare a top-level list result ignoring order                  |
| `timeout`     | Per-case timeout in seconds (default `10`)                               |
| `output_mode` | `"stdout"` → compare captured printed output; anything else compares the return value |
| `types`       | **Required for C++**: map of parameter name → type                       |
| `returns`     | Documented for C++ but currently not validated                           |

A test can set `"hidden": true`; hidden cases run only on **Submit**.

`run_test_count` is **not used in v2.1**. It may still appear in older problem files, but
**Run** always executes all non-hidden tests.

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

### C++ types accepted in v2.1

| JSON type | C++ type     |
| --------- | ------------ |
| `int`     | `int`        |
| `long`    | `long long`  |
| `double`  | `double`     |
| `bool`    | `bool`       |
| `string`  | `string`     |
| `T[]`     | `vector<T>`  |

Nested shorthand works (`int[][]` → `vector<vector<int>>`), but the long form
`vector<int>` / `std::vector<int>` does **not** — it raises `KeyError` and is reported as
`Runner failed: 'vector<int>'`. The three new sample problems use that form, so their C++
tests fail until `ctype()` is restored.

### Starter code and includes

For C++ in v2.1 the generated file order is:

```text
<your code>
<bits/stdc++.h> + reader/writer helpers
main()
```

Because the standard headers come **after** your code, a starter that uses `vector<int>`
without its own `#include` will not compile. Add `#include <bits/stdc++.h>` (or the
specific headers) at the top of C++ solutions for now.

### Markdown in `problem.md`

v2.1 supports headings (`#`, `##`, `###`), paragraphs, **bold**, *italic*, inline code,
fenced code blocks and simple `-`/`*` bullet lines. Links, images, blockquotes, ordered
lists and horizontal rules are shown as plain text / not rendered. Raw HTML is escaped.

## How the judge works

Every Run/Submit:

1. Saves the editor draft in memory and writes `user_solution.<ext>` into the problem
   folder.
2. Calls `engine.judge(...)` with the selected language and tests.
3. Runs everything in a fresh temporary directory and returns per-case results.

- **Python** — solution is `exec`'d in a namespace pre-importing `typing`, `collections`,
  `math`, `heapq`, `itertools`, `functools`, `bisect`, then
  `Solution().<method>(**input)` is called. `stdout` is captured per case.
- **C++** — compiles with `g++ -O2 -std=c++17` (120 s allowed), feeds each case's
  arguments on stdin and reads the result from `result.json`. In `stdout` mode, `cout` is
  captured and written as a JSON string.
- **JavaScript** — the file is wrapped with `new Function(...)`, `Solution` is
  instantiated per case, and `console.log` is captured.

**Run** executes all non-hidden tests. **Submit** executes every test, including hidden
ones.

Verdicts: `Accepted`, `Wrong Answer`, `Runtime Error`, `Time Limit Exceeded`,
`Execution Error` (setup/compile failure).

## Known issues and limitations (v2.1)

- **Editor may fail to initialize** because `indentOnInput` is passed instead of
  `indentOnInput()` (`webui/src/main.js`). Error:
  `Unrecognized extension value in extension set`. There is no fallback editor.
- **C++ is broken for `695`, `702`, `838`** — `vector<int>` types are rejected and
  headerless starters do not compile. Python and JavaScript work for those problems.
- **`webui/dist/app.js` is not in the repository.** `run.bat` builds it on first launch.
  Running `app.py` before that shows a static page with no working problem list.
- **Node.js is required even when the editor bundle already exists**, because `run.bat`
  checks `node` before testing `dist/app.js`.
- **First setup needs internet** for `npm install`; if it fails, the launcher stops before
  starting the app.
- **Drafts are memory-only.** `save_draft` stores code in the Python process; closing the
  app loses unsaved drafts. Only `user_solution.<ext>` is persisted.
- **`user_solution.*` files still pollute the problem folders.**
- **Run can be slow on the large samples.** `695`, `702` and `838` contain 205–245
  visible tests each; Run now executes all of them, and C++ launches the compiled binary
  once per case.
- **`run.bat` does not enforce `pywebview>=5.4`.** It only checks that `webview` imports.
- **No `.gitignore` for generated files.** `__pycache__/`, `user_solution.*` and
  `webui/dist/` can appear as untracked changes.
- **In-app version badge says `2.0`**, while this branch is v2.1.

## Troubleshooting

| Symptom | Cause / fix |
| --- | --- |
| `Node.js was not found.` | Install Node.js LTS and run `run.bat` again. Node is now required even for Python/C++. |
| `Failed to install CodeMirror dependencies` | `npm install` could not reach the registry. Check internet/proxy and rerun. |
| `Failed to build the CodeMirror editor` | esbuild failed; run `npm run build` in `webui/` to see the full error. |
| Blank editor / static page only | `webui/dist/app.js` is missing. Run `run.bat` (or `npm install && npm run build` in `webui/`). |
| `Unrecognized extension value in extension set` | The `indentOnInput` registration bug above. Change `indentOnInput` to `indentOnInput()` in `webui/src/main.js` and rebuild. |
| C++: `Runner failed: 'vector<int>'` | `ctype()` does not support `vector<int>` in v2.1. Use `int[]` in `types` **and** add `#include <bits/stdc++.h>` to your code. |
| C++: `'vector' has not been declared` | Headers are emitted after user code. Add the include at the top of your solution. |
| "LocalCode could not start" / webview initialization error | Install or repair the Microsoft Edge WebView2 Evergreen Runtime. If it crashes on launch, the `api.window = window` regression may be involved; remove that assignment. |
| `g++ was not found...` | Install MSYS2 UCRT64 GCC and add `C:\msys64\ucrt64\bin` to `PATH`. |
| `cc1plus.exe - Entry Point Not Found` / `libgcc_s_seh-1.dll` missing | MSYS2 runtime DLLs are not on the child-process `PATH`; only default `C:\msys64` locations are auto-added. See `README_GCC_FIX.txt`. |
| `Node.js not found...` during JavaScript Run | Same as above; JavaScript judging always needs Node.js. |
| `tests.json needs a "types" map ... for C++` | Add `types` (and `returns`) for that problem. |
| `Python 3 was not found.` | Python is not installed or `py`/`python` is not on `PATH`. |
| `LocalCode closed with an error.` | Run `python app.py` in a terminal to see the traceback. |
| EXE build fails | Expected: `build_exe.bat` is a placeholder. Use `run.bat`. |

## Version history (this branch)

- **v2.1** — local esbuild bundle for CodeMirror (offline editor after one-time setup),
  automated build in `run.bat`, Node.js as a hard requirement; rich Markdown/images,
  sample-test Run mode, vector C++ types and header ordering regressed as listed above.
- **v2.0** — pywebview + CodeMirror web UI with CDN imports, rich Markdown and image
  previews, Run sample logic (`run_test_count`), expanded C++ types and header ordering.
- **v1.0** — Tkinter desktop judge with Python/C++/JavaScript support.
