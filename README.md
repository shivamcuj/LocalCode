# LocalCode 2.6

LocalCode is a **Windows desktop, offline-first LeetCode-style practice judge**. Pick a
problem, write a solution in Python, C++ or JavaScript, and run it against local test
files. There is no account, no server and no cloud judging.

Version 2.6 is a **problem-statement rendering release**. Rich Markdown is back, images in
`problem.md` now render, and local images work without an internet connection because the
Python side reads them and hands the WebView a base64 `data:` URL. Clicking an image opens
a zoom preview.

> The page title and header brand are **LocalCode** again and the badge reads **2.6**.
> `README_LOCALCODE.txt` still has the "LOCALCODE WINDOWS 2.2" title even though it now
> contains a "RICH MARKDOWN + IMAGE PREVIEW (v2.6)" section.

## What's new in v2.6

### Rich Markdown

`markdownToHtml()` in `webui/src/main.js` was rewritten as an async block parser with an
inline tokenizer (`renderInline`). It now supports:

- Headings `#` through `######` (levels 1–6).
- Paragraphs with proper joining across wrapped lines.
- **Bold**, *italic* and `inline code`.
- Fenced code blocks with an optional language, emitted as
  `<pre><code class="language-…">` (the old renderer dropped the language).
- Unordered lists with `-`, `*` or `+`, and ordered lists with `1.` / `1)` — emitted as
  real `<ul>` / `<ol>` with `<li>` items. Consecutive items now stay in one list instead
  of becoming one `div` per bullet.
- Blockquotes (`>`), horizontal rules (`---`, `___`, `***`), and HTTP(S) links that open
  in a new tab with `rel="noopener noreferrer"`.
- Raw HTML in `problem.md` is **escaped**, not executed — only tags built by the renderer
  reach the page.

### Inline images

- **Remote images work.** `![alt](https://…)` is rendered as a `<figure class="md-image">`
  with the image, alt text and a caption. This is what the two
  `static.takeuforward.org` images in `951-pattern-19` needed.
- **Local images work offline.** A relative target such as
  `![Example](images/example1.png)` is sent to the new Python API, which returns the file
  as a base64 data URL. No web server, no network, and the image travels with the problem
  folder.
- **Missing images degrade gracefully.** If the file cannot be resolved, the statement
  shows `Image unavailable: …` inside `.md-image-missing` instead of a broken icon. If an
  image element fails later while loading, an `error` handler swaps the figure for the
  same placeholder.
- **Images are constrained** by `max-width: 100%` and `max-height: 420px` inside the
  statement, and are `loading="lazy"`.

### Click-to-zoom image preview

- Any rendered statement image is clickable (`cursor: zoom-in`).
- A full-screen `#imagePreview` overlay shows the enlarged image with a close button
  (`×`).
- The preview closes on the close button, a backdrop click, or **Escape**.

### New Python API: `resolve_image`

`app.py` gained:

```python
def resolve_image(self, index, image_path):
    """Return a safe local problem image as a data URL for the WebView."""
```

It validates, in order:

1. The problem index is an integer inside `self.problems`.
2. The path is non-empty, is relative, and does not start with `/` or `\`.
3. The first path segment contains no `:` — so `C:/…`, `https://…`, `data:…`,
   `file:…` and `javascript:…` are rejected. Only local relative paths are accepted.
4. The resolved path stays inside the selected problem folder — `../` escapes are
   rejected via a `resolve()` + `parents` check.
5. The target exists and is a file.
6. `mimetypes` says the file is an `image/*` type.

It then base64-encodes the file and returns `{"ok": true, "src": "data:image/png;base64,…"}`.
Failures return `{"ok": false, "error": "…"}`, which the UI turns into the missing-image
placeholder.

### Branding

- `<title>` and the header brand are **LocalCode** again (v2.5 had changed them to
  `SRKCode`).
- The version badge is **2.6**.
- `style.css` gained the rich-Markdown rules, `.md-image`, `.md-image-missing` and the
  `.image-preview` modal styles.

## Fixed since v2.5

| v2.5 problem | Status in v2.6 |
| --- | --- |
| `951-pattern-19` remote images showed as literal Markdown text | **Fixed** — `![alt](https://…)` now renders |
| Local images were never embedded or served, so they could not display | **Fixed** — `resolve_image` returns a data URL |
| Markdown links were not rendered | **Fixed** — HTTP(S) links render with `target="_blank"` |
| Ordered lists rendered as plain paragraphs | **Fixed** — real `<ol>` output |
| Blockquotes and horizontal rules were unsupported | **Fixed** — `<blockquote>` and `<hr>` |
| The click-to-zoom image modal was missing | **Fixed** — `#imagePreview` with button, backdrop and Escape |
| Fenced code blocks lost their language | **Fixed** — `class="language-…"` is emitted |
| Page title/brand said `SRKCode` while the rest of the app said LocalCode | **Fixed** — both are LocalCode now |
| Badge still said `2.4` | **Fixed** — badge says `2.6` |
| Raw HTML handling was line-based and could mis-parse inline Markdown | **Improved** — one tokenizer escapes everything it did not create |

Verified directly:

- `resolve_image(4, "attached-pattern-reference.png")` returns a ~39 KB
  `data:image/png;base64,…` URL.
- Missing files, `../001-two-sum/problem.md`, `images/../../001-two-sum/problem.md`,
  `C:/Windows/win.ini`, `https://example.com/a.png` and an out-of-range index are all
  rejected with distinct errors.
- A Node harness confirmed the renderer output for headings, bold/italic, inline code,
  links, `ul`/`ol`, blockquote, `hr`, fenced code with language, a remote image, a local
  data-URL image, a missing image and escaped `<script>`.

## Still broken or carried over from v2.5

`engine.py` and `run.bat` are unchanged in v2.6.

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
   - `951-pattern-19`'s C++ solution fails with `'cout' was not declared in this scope`
     unless `#include <bits/stdc++.h>` is added at the top (re-verified: it passes with
     the include).

   Python and JavaScript work for these problems.

3. **`951`'s bundled PNG still does not appear.** `attached-pattern-reference.png` is
   only mentioned as `inline code` in the statement, and inline code is not an image.
   Add a line such as
   `![Pattern reference](attached-pattern-reference.png)` to display it. (The renderer and
   API can serve the file — this is a content issue, not a code bug.)

4. **Markdown image URLs are parsed with `[^)]+`.** A target containing `)` or an optional
   title (`![a](pic.png "caption")`) will not match, and falls back to escaped text.
   Links have the same limitation.

5. **No image limits or caching.** `resolve_image` reads and base64-encodes the file on
   every render, with no size cap, no MIME allow-list beyond `image/*`, and no cache. A
   very large PNG would inflate the DOM and memory.

6. **Remote images are still fetched by the WebView.** HTTP(S) images bypass
   `resolve_image` and load directly, so a `problem.md` can contact an external host
   (offline users see the missing-image placeholder). Only *local* paths are restricted.

7. **`returns` is still not validated for C++**, even though the error text mentions it.

8. **The full editor still needs the network on every launch.** CodeMirror is imported
   from `https://esm.sh`; offline users get the plain textarea without highlighting,
   autocomplete, folding or Tab indentation.

9. **`webui/package.json` is dead weight.** Its CodeMirror dependencies and esbuild script
   are unused at runtime.

10. **`README_LOCALCODE.txt` title still says 2.2.** Its body now has v2.3, v2.4, v2.5 and
    v2.6 sections.

11. **The editor upgrade still replays unconditionally** after `cmReady`, discarding cursor
    position and undo history and potentially showing the fallback toast twice.

12. **`os.chdir(ROOT)` is process-wide.** Harmless today because the judge uses temporary
    directories and absolute problem paths, but fragile for future relative paths.

13. **Large test files.** `838-linear-search` is about 8 MB (256 tests, arrays up to
    100,000 elements) and `951-pattern-19` about 2.7 MB (100 tests). Run uses samples, but
    **Submit** still runs the whole suite (one C++ process per case), so it can take a
    while.

14. **`run_test_count` can display values below 2.** The backend clamps to 2–4 and then
    takes `min(…, visible_count)`, so a problem with one visible test shows
    `Run: 1 sample`, which contradicts the documented 2–4 range.

15. **`__pycache__/` is untracked noise.** Importing `app.py` during testing created it and
    there is still no root `.gitignore`.

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
  textarea fallback. (Problem images can still work offline when they are local files.)

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
  README_LOCALCODE.txt    # plain-text 2.2 notes + v2.3–v2.6 sections
  README_GCC_FIX.txt      # MSYS2 GCC runtime-DLL note
  webui/
    index.html            # app shell (LocalCode); image-preview modal
    style.css             # dark theme, rich-Markdown, image and preview styles
    src/main.js           # UI logic, Markdown renderer, image resolution, CDN loader
    package.json          # vestigial CodeMirror deps + unused esbuild script
    .gitignore            # node_modules/
  problems/
    001-two-sum/          # 4 tests (2 hidden); run_test_count 3 -> Run uses 2
    695-second-largest-element/   # 239 tests; C++ currently broken
    702-largest-element/          # 205 tests; C++ currently broken
    838-linear-search/            # 256 tests up to 100k elements; C++ broken
    951-pattern-19/               # 100 stdout tests; remote + local images
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

### C++ types accepted in v2.6

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

Supported in v2.6:

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
- **C++** — compiles with `g++ -O2 -std=c++17` (120 s allowed), feeds each case's
  arguments on stdin and reads the result from `result.json`. In `stdout` mode, `cout` is
  captured and written as a JSON string.
- **JavaScript** — the file is wrapped with `new Function(...)`, `Solution` is
  instantiated per case, and `console.log` is captured.

**Run** executes the sample subset. **Submit** executes every test, including hidden ones.

Verdicts: `Accepted`, `Wrong Answer`, `Runtime Error`, `Time Limit Exceeded`,
`Execution Error` (setup/compile failure).

## Known issues and limitations (v2.6)

- **C++ is broken for `695`, `702`, `838`, and awkward for `951`** because of the missing
  vector types and the header ordering. Use Python/JavaScript, or add
  `#include <bits/stdc++.h>` yourself where possible.
- **`951`'s bundled PNG is not shown** until the statement uses a Markdown image tag.
- **Markdown image/link URLs cannot contain `)` or titles.**
- **Local images are re-read and base64-encoded on every statement load**; there is no
  size limit or cache.
- **Remote images are fetched by the WebView**, so a statement can contact an external
  host.
- **Full editor requires internet.** Without `esm.sh`, the textarea fallback is used.
- **Submit can be slow** on `838` (256 cases, up to 100k-element arrays) and `951`
  (100 cases), especially in C++.
- **Drafts are memory-only.** Closing the app loses unsaved drafts; only
  `user_solution.<ext>` is written to disk.
- **`user_solution.*` files pollute the problem folders.**
- **`run.bat` does not enforce `pywebview>=5.4`.** It only checks that `webview` imports.
- **`build_exe.bat` is a placeholder.** Use `run.bat` from the source folder.
- **No root `.gitignore`** for generated files.
- **Plain-text title still says 2.2.**

## Troubleshooting

| Symptom | Cause / fix |
| --- | --- |
| An image in the statement shows `Image unavailable: …` | The file is missing, is outside the problem folder, or is not an `image/*` type. Check the path is relative to that problem folder. |
| A remote image does not load | No internet, or the host is blocked. Remote images are fetched by the WebView. |
| `951`'s reference PNG is not displayed | It is only mentioned as inline code. Add `![Pattern reference](attached-pattern-reference.png)` to `problem.md`. |
| `![a](pic.png "caption")` shows as text | Image URLs with titles or `)` are not parsed. Use a plain path. |
| Run shows only 2–4 cases | Expected: Run uses sample tests. Use Submit for the full suite. |
| Run says `no test cases available for this action` | The problem has no visible tests. Submit runs hidden tests. |
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

- **v2.6** — restores rich Markdown (headings 1–6, lists, blockquotes, rules, links,
  fenced-code languages), renders remote and local images, adds the
  `resolve_image` Python API with path/MIME validation and base64 data URLs, adds a
  click-to-zoom image modal, degrades missing images gracefully, and puts the
  **LocalCode** brand back with a **2.6** badge. C++ vector types and header ordering
  remain broken.
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
