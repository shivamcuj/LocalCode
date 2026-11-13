# LocalCode 2.5 (SRKCode UI)

LocalCode is a **Windows desktop, offline-first LeetCode-style practice judge**. Pick a
problem, write a solution in Python, C++ or JavaScript, and run it against local test
files. There is no account, no server and no cloud judging.

Version 2.5 restores the **Run vs Submit sample logic** and expands the problem set. The
UI is also rebranded to **SRKCode** in the page title and header. Run is a fast feedback
loop again (first 2–4 visible tests, default 3), while Submit evaluates the complete suite.

> Version strings are inconsistent in this release: the header badge still says **2.4**,
> `README_LOCALCODE.txt` still has the "LOCALCODE WINDOWS 2.2" title, and the app window
> title is still "LocalCode" while the in-page brand is "SRKCode".

## What's new in v2.5

### Run vs Submit

- **Run uses sample tests only.** `app.py` now selects the first `run_test_count`
  non-hidden tests (default **3**, clamped to **2–4**, then limited to the number of
  visible tests). Submit still uses every test, including `"hidden": true` cases.
- **Per-problem `run_test_count` is honored again.** `tests.json` may set it at the top
  level. `001-two-sum` and `984-pattern4` now declare `"run_test_count": 3`.
- **Clearer UI.** The editor bar shows `Run: N sample · Submit: M total tests`; verdicts
  read `Running sample tests…` / `Submitting all tests…`, and the results line labels the
  scope as `sample tests` or `total tests`.
- **Empty-selection guard.** If an action has no tests to run (e.g. a problem with only
  hidden tests), the backend returns
  `This problem has no test cases available for this action.` instead of an empty result.

### New and expanded content

- **New problem `951-pattern-19`** (difficulty `Basic`):
  - 100 tests, `output_mode: "stdout"`, `n` from 1 to 100.
  - Includes a text version of the pattern for `n = 4` and `n = 2`.
  - References two remote images and ships `attached-pattern-reference.png`, but the
    Markdown renderer does **not** render images (see limitations).
- **`838-linear-search` expanded**: 256 tests (up from 245), now including arrays up to
  100,000 elements; `tests.json` is about 8 MB.
- **`838` statement updated**: real constraints were added
  (`1 <= nums.length <= 10^5`, `-10^4 <= nums[i], target <= 10^4`), replacing the old
  "input assumption" note.
- **`838` starter/solution cleaned up**: starter reformatted; the placeholder
  `user_solution.cpp` no longer returns `true`.

### Branding and docs

- Page `<title>` and header brand changed from **LocalCode** to **SRKCode** (the `LC`
  brand mark and version badge remain).
- `README_LOCALCODE.txt` gained a "RUN VS SUBMIT (v2.5)" section explaining
  `run_test_count` and the 2/3/4 rules.

## Fixed since v2.4

| v2.4 problem | Status in v2.5 |
| --- | --- |
| Run executed every visible test, so 205–256-case problems were slow | **Fixed** — Run uses only 2–4 sample tests (default 3) |
| `run_test_count` in `tests.json` was ignored | **Fixed** — parsed, clamped to 2–4, and limited to available visible tests |
| UI did not say whether results covered samples or the full suite | **Fixed** — header, verdict and result labels show the scope |
| An action with zero selected tests returned an empty/ambiguous result | **Fixed** — explicit `no test cases available` error |
| `838-linear-search` shipped without constraints and with only small inputs | **Improved** — constraints documented and suite expanded to 256 tests up to 100k elements |

## Still broken or carried over from v2.4

`engine.py` and `run.bat` are unchanged in v2.5.

1. **C++ `vector<...>` types still fail.** `engine.ctype()` accepts only `int`, `long`,
   `double`, `bool`, `string` and `T[]`; `vector<int>` raises `KeyError`.
   `695`, `702` and `838` declare `"types": {"nums": "vector<int>"}`, so C++ Run/Submit
   reports:

   ```text
   Runner failed: 'vector<int>'
   ```

2. **C++ standard headers are still emitted after user code.** `engine.py` writes
   `code + "\n" + CPP_HELP + main`. Consequences:
   - `695`, `702`, `838` starters fail with `'vector' has not been declared`.
   - The new `951-pattern-19` C++ solution fails with `'cout' was not declared in this
     scope` unless the user adds `#include <bits/stdc++.h>` at the top
     (verified). Python and JavaScript work for these problems.

3. **Markdown images are still not rendered.** `951-pattern-19/problem.md` uses remote
   `![...](https://static.takeuforward.org/...)` images, which appear as literal Markdown
   text. The bundled `attached-pattern-reference.png` is not referenced by an image tag,
   so it is never displayed either. The local PNG is also not embedded or served.

4. **Rich Markdown is still limited.** Headings, paragraphs, bold/italic, inline code,
   fenced code and simple bullets render. Links, images, ordered lists, blockquotes,
   horizontal rules and the click-to-zoom image modal do not.

5. **The full editor still needs the network on every launch.** CodeMirror is imported
   from `https://esm.sh`; offline users get the plain textarea without highlighting,
   autocomplete, folding or Tab indentation.

6. **`returns` is still not validated for C++**, even though the error text mentions it.

7. **`webui/package.json` is dead weight.** Its CodeMirror dependencies and esbuild script
   are unused at runtime.

8. **Version/branding strings disagree:** badge `2.4`, plain-text title `2.2`, window
   title `LocalCode`, in-page brand `SRKCode`, brand mark `LC`.

9. **The editor upgrade still replays unconditionally** after `cmReady`, discarding cursor
   position and undo history and potentially showing the fallback toast twice.

10. **`os.chdir(ROOT)` is process-wide.** Harmless today because the judge uses temporary
    directories and absolute problem paths, but fragile for future relative paths.

11. **Large test files.** `838` is about 8 MB with 256 tests and `951` about 2.7 MB with
    100 tests. Run is fast now, but **Submit** still launches the whole suite (and for C++
    one executable invocation per case), so it can take noticeably longer.

12. **`run_test_count` can display values below 2.** The backend clamps to 2–4 and then
    takes `min(..., visible_count)`, so a problem with one visible test shows
    `Run: 1 sample`, which contradicts the documented 2–4 range.

## Still open from earlier versions

- `returns` validation, string id sorting (`1000` before `695`), MSYS2 path coverage,
  `py`/`python` interpreter mismatch, ignored runner exit codes, no sandbox,
  top-level-only `unordered`, and `user_solution.*` scratch files.
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
  textarea fallback.

## Quick start

1. Extract the folder (do not run from inside a ZIP preview).
2. Double-click **`run.bat`**.
   - It locates Python (prefers `py -3`, then `python`).
   - If `node` is missing, it prints a warning and continues.
   - If `import webview` fails, it runs `pip install -r requirements.txt`.
   - It starts `app.py`.
3. Select a problem, choose a language, write code, then **Run** (samples) or **Submit**
   (all tests).

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
  app.py                  # pywebview shell, HTTP-served UI, Run/Submit sample logic
  engine.py               # judge: Python/JS runners, C++ codegen, compile & execute
  requirements.txt        # pywebview>=5.4,<7
  run.bat                 # Python check, optional Node warning, pywebview install, launch
  build_exe.bat           # placeholder (no EXE build)
  README.md               # this file
  README_LOCALCODE.txt    # plain-text 2.2 notes + v2.3/v2.4/v2.5 sections
  README_GCC_FIX.txt      # MSYS2 GCC runtime-DLL note
  webui/
    index.html            # app shell (SRKCode); loads src/main.js
    style.css             # dark theme, markdown styles, .fallback-editor
    src/main.js           # UI logic, markdown renderer, CDN CodeMirror loader/fallback
    package.json          # vestigial CodeMirror deps + unused esbuild script
    .gitignore            # node_modules/
  problems/
    001-two-sum/          # 4 tests (2 hidden); run_test_count 3 -> Run uses 2
    695-second-largest-element/   # 239 tests; C++ currently broken
    702-largest-element/          # 205 tests; C++ currently broken
    838-linear-search/            # 256 tests up to 100k elements; C++ broken
    951-pattern-19/               # 100 stdout tests; images not rendered
    984-pattern4/                 # 9 stdout tests; run_test_count 3
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
    images/               # optional (not rendered by the current UI)
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
| `output_mode`    | `"stdout"` → compare captured printed output; anything else compares the return value |
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

### C++ types accepted in v2.5

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

Because the headers come **after** your code, starters that use `vector`, `cout`, `string`
or similar without their own include do not compile. Add
`#include <bits/stdc++.h>` at the top of C++ solutions for now.

### Markdown in `problem.md`

Supported: headings (`#`, `##`, `###`), paragraphs, **bold**, *italic*, inline code,
fenced code blocks and simple `-`/`*` bullet lines. Links, images, blockquotes, ordered
lists and horizontal rules are **not** rendered. Raw HTML is escaped. This is why the new
`951-pattern-19` images are not visible.

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
- **C++** — compiles with `g++ -O2 -std=c++17` (120 s allowed), feeds each case's
  arguments on stdin and reads the result from `result.json`. In `stdout` mode, `cout` is
  captured and written as a JSON string.
- **JavaScript** — the file is wrapped with `new Function(...)`, `Solution` is
  instantiated per case, and `console.log` is captured.

**Run** executes the sample subset. **Submit** executes every test, including hidden ones.

Verdicts: `Accepted`, `Wrong Answer`, `Runtime Error`, `Time Limit Exceeded`,
`Execution Error` (setup/compile failure).

## Known issues and limitations (v2.5)

- **C++ is broken for `695`, `702`, `838`, and awkward for `951`** because of the missing
  vector types and the header ordering. Use Python/JavaScript, or add
  `#include <bits/stdc++.h>` yourself where possible.
- **Images in problem statements are not displayed**, including the new `951` references.
- **Full editor requires internet.** Without `esm.sh`, the textarea fallback is used.
- **Submit can be slow** on `838` (256 cases, up to 100k-element arrays) and `951`
  (100 cases), especially in C++.
- **Drafts are memory-only.** Closing the app loses unsaved drafts; only
  `user_solution.<ext>` is written to disk.
- **`user_solution.*` files pollute the problem folders.**
- **`run.bat` does not enforce `pywebview>=5.4`.** It only checks that `webview` imports.
- **`build_exe.bat` is a placeholder.** Use `run.bat` from the source folder.
- **No root `.gitignore`** for generated files.
- **Version/brand strings are inconsistent** (badge 2.4, title 2.2, `LocalCode` window vs
  `SRKCode` page).

## Troubleshooting

| Symptom | Cause / fix |
| --- | --- |
| Run shows only 2–4 cases | Expected: Run uses sample tests. Use Submit for the full suite. |
| Run says `no test cases available for this action` | The problem has no visible tests. Submit runs hidden tests. |
| Images in `951-pattern-19` show as Markdown text | Image rendering is not implemented in the Markdown renderer. Use the text pattern in the statement. |
| C++: `Runner failed: 'vector<int>'` | `ctype()` does not support `vector<int>`. Use `int[]` in `types` **and** add `#include <bits/stdc++.h>` to your code. |
| C++: `'vector' has not been declared` / `'cout' was not declared` | Headers are emitted after user code. Add the include at the top of your solution. |
| Editor is a plain textarea | CodeMirror could not be fetched from `esm.sh` (offline, proxy, DNS). The toast explains the reason. |
| "CodeMirror could not initialize; using the built-in editor..." | The `EditorView` constructor threw; the textarea is active and the toast/console has the error. |
| "LocalCode could not start" / webview initialization error | Install or repair the Microsoft Edge WebView2 Evergreen Runtime. |
| Window stays blank | Check that `webui/index.html` exists, then run `python app.py` in a terminal for the traceback. |
| `g++ was not found...` | Install MSYS2 UCRT64 GCC and add `C:\msys64\ucrt64\bin` to `PATH`. |
| `cc1plus.exe - Entry Point Not Found` / `libgcc_s_seh-1.dll` missing | MSYS2 runtime DLLs are not on the child-process `PATH`; only default `C:\msys64` locations are auto-added. See `README_GCC_FIX.txt`. |
| `Node.js not found...` warning at launch | Harmless for Python/C++. Install Node.js LTS only if you need JavaScript judging. |
| `tests.json needs a "types" map ... for C++` | Add `types` (and ideally `returns`) for that problem. |
| `Python 3 was not found.` | Python is not installed or `py`/`python` is not on `PATH`. |
| `LocalCode closed with an error.` | Run `python app.py` in a terminal to see the traceback. |
| EXE build fails | Expected: `build_exe.bat` is a placeholder. Use `run.bat`. |

## Version history (this branch)

- **v2.5** — restores Run-vs-Submit sample logic (`run_test_count`, default 3, clamp 2–4),
  adds scope labels and an empty-test guard, adds `951-pattern-19` (100 stdout tests),
  expands `838-linear-search` to 256 tests with documented constraints, and rebrands the
  page to **SRKCode**. C++ vector types/header ordering, Markdown images and other older
  issues remain.
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
