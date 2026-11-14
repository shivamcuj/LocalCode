LOCALCODE WINDOWS 2.2 - CODEMIRROR 6
===================================

START
1. Extract the complete ZIP into a normal folder.
2. Make sure Python 3 and Node.js LTS are installed and available in PATH.
3. Double-click run.bat.
4. run.bat installs pywebview if needed and starts LocalCode. There is no npm build step and no missing dist/app.js dependency.
5. CodeMirror 6 modules are loaded from esm.sh when internet is available. If they cannot load, the application still opens with a built-in text editor so problem loading, Run, and Submit remain usable.

EDITOR FEATURES
- CodeMirror 6 editor with Python, C++, and JavaScript syntax highlighting.
- Line numbers, active-line highlight, bracket matching, auto-closing brackets/quotes.
- Automatic indentation and reindentation on input.
- Tab inserts a 4-space indent; Shift+Tab outdents selected lines.
- Autocomplete support (Ctrl+Space), search, code folding, undo/redo, and multiple selections.
- Separate saved drafts for every problem and language during the app session.

USAGE
- Select a problem from the top dropdown.
- Choose Python, C++, or JavaScript.
- Write your solution in the editor.
- Run checks visible tests. Submit checks all tests.
- Ctrl+Enter runs; Ctrl+Shift+Enter submits.
- Use Refresh to rescan the problems folder; Open problems folder opens it in Explorer.

ADD A PROBLEM
Create a folder inside problems/, for example:
  problems/1000-my-problem/
    problem.md
    tests.json
    starter.py
    starter.cpp
    starter.js

Required tests.json fields: id, title, method, tests. Each test has input and expected.
For C++ problems, include a types map (e.g. {"nums":"int[]"}) and returns for return-value problems.
For print-output problems, set "output_mode": "stdout". C++ output is captured from cout; Python from print(); JavaScript from console.log().

REQUIREMENTS
- Python 3
- Node.js LTS (used for JavaScript judging and the first-time editor build)
- MSYS2 UCRT64 GCC or compatible g++ for C++
- Microsoft Edge WebView2 Runtime for the desktop window (normally present on modern Windows; install the Evergreen Runtime if prompted)
- Internet connection for CodeMirror 6 editor features; offline fallback editor is available

MSYS2 GCC
The launcher adds no compiler directories globally. The judge automatically adds the standard C:\msys64\ucrt64\bin and C:\msys64\usr\bin directories to the compiler process PATH when they exist.


Troubleshooting update (v2.1):
- The editor waits for the pywebview JavaScript bridge and also checks for it if the ready event happened before the editor bundle finished loading.
- If the editor does not load, close LocalCode and run run.bat again. The launcher verifies that webui\dist\app.js was built.
- Starter code is loaded from the selected problem folder's starter.py, starter.cpp, or starter.js file.
- Run tests the visible cases; Submit tests all cases. Ctrl+Enter runs and Ctrl+Shift+Enter submits.


Startup fix notes (v2.3)
-----------------------
- The pywebview Window object is no longer attached to the JavaScript API object.
  This avoids recursive inspection of native Windows accessibility properties.
- The UI is served using pywebview's local HTTP server instead of file://.
- Problem statements and starter code load before optional CodeMirror CDN imports
  finish. If the network is unavailable, the fallback editor remains usable.


VERSION 2.4 FIX
- Corrected CodeMirror 6 indentOnInput extension registration.
- This resolves the "Unrecognized extension value in extension set" error that prevented problem loading.
- If CodeMirror initialization fails for another reason, the app now falls back to a basic editor instead of blocking problem loading.


RUN VS SUBMIT (v2.5)
-------------------
Run executes only the first 3 non-hidden sample tests by default. Submit executes
every test in tests.json, including tests marked hidden. You can configure the
Run sample count per problem with the optional top-level field:

    "run_test_count": 3

Allowed values are 2, 3, or 4. If fewer visible tests exist, Run uses all
available visible tests. Submit always uses the complete test suite.


RICH MARKDOWN + IMAGE PREVIEW (v2.6)
-----------------------------------
- Problem statements render Markdown headings, paragraphs, bold/italic text, inline code, fenced code blocks, lists, blockquotes, horizontal rules, and links.
- Markdown images written as ![description](https://...) are displayed inline where they appear in problem.md. Remote HTTP/HTTPS images need an internet connection.
- Local images are supported with relative paths, for example ![Example](images/example1.png). Put the image inside that problem's folder (usually an images/ subfolder). Local images are read through the Python API and embedded in the WebView, so they work offline.
- Click any rendered image to open a larger preview. Press Escape or click outside the image to close it.
- Local image paths are restricted to the selected problem folder; absolute paths and ../ traversal are rejected. Raw HTML in problem.md is escaped rather than executed.
- If a local image is mentioned only as inline code (for example `attached-pattern-reference.png`), it will not display automatically. Add a Markdown image line such as ![Pattern reference](attached-pattern-reference.png).
C++ tests.json type declarations support int, long, double, bool, string, int[], vector<int>, std::vector<int>, and nested vector forms such as vector<vector<int>>.
The C++ judge now places standard headers before submitted code, so vector-based starter signatures compile without requiring users to add includes.
