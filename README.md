# LocalCode

LocalCode is a small **offline, LeetCode-style practice judge for Windows**. It is a
single-file Python/Tkinter desktop app: pick a problem, write a solution in Python, C++
or JavaScript, and run it locally. There is no server, login, or network access — the
tests ship with the app and your code is compiled/executed on your own machine.

The only Python dependency is the standard library (`tkinter`), plus `g++` for C++ and
`node` for JavaScript.

## What it does

- Scans the `problems` folder (next to `app.py` / the built `.exe`) for problem
  directories containing both `problem.md` and `tests.json`.
- Shows a problem dropdown, the statement (simple Markdown rendering), the difficulty
  colour, and an editor.
- Keeps a separate in-memory draft and starter file per problem **and** per language
  (`starter.py`, `starter.cpp`, `starter.js`).
- **Run** executes the visible tests; **Submit** executes every test, including ones
  marked `"hidden": true`.
- Result table shows pass/fail per case with input, expected output, actual output and
  per-case runtime; selecting a row shows stdout and the full error/traceback.
- Verdicts: `Accepted`, `Wrong Answer`, `Runtime Error`, `Time Limit Exceeded`,
  `Compile / Setup Error`.
- Compares results as JSON values. Top-level lists are order-insensitive when the
  problem sets `"unordered": true`.
- Supports "print the answer" problems via `"output_mode": "stdout"` (printed output is
  captured in all three languages and a trailing newline is ignored).
- Can load a different problem folder with **Open Folder**.
- `build_exe.bat` packages the app as `dist\LocalCode.exe` with PyInstaller.

It is **not** a sandbox. Submitted code runs with your user privileges and can read/write
files and use the network.

## Quick start (Windows)

1. Install Python 3 and make sure `py` or `python` works in a terminal.
2. Optional: install MSYS2 UCRT64 GCC for C++ and Node.js for JavaScript.
3. Double-click `run.bat` (or run `python app.py`).
4. Pick a problem, pick a language, write code, then **Run** or **Submit**.

`run.bat` prefers the `py -3` launcher and falls back to `python`. `app.py` itself looks
for `python` first, then `py`, then the current interpreter.

### Building an exe

```bat
build_exe.bat
```

This installs PyInstaller and creates `dist\LocalCode.exe`. Copy the `problems` folder
next to the exe — it is not bundled into the executable.

## Repository layout

```text
LocalCode/
  app.py                  # the whole application (UI + judge)
  run.bat                 # launch the app from source
  build_exe.bat           # PyInstaller one-file build
  README.md               # this file
  README_GCC_FIX.txt      # historical note about the MSYS2 GCC runtime-DLL fix
  problems/
    001-two-sum/          # return-value example
      problem.md
      tests.json
      starter.py
      starter.cpp
      starter.js
    984-pattern4/         # stdout ("print the answer") example
      problem.md
      tests.json
      starter.py
      starter.cpp
      starter.js
```

`user_solution.*` files are written into the problem folder on every Run/Submit and are
scratch artifacts, not problem data.

## Problem folder format

Each problem is a folder under `problems/`:

```text
problems/
  1000-my-problem/
    problem.md
    tests.json
    starter.py        # optional
    starter.cpp       # optional
    starter.js        # optional
```

### `tests.json`

Required fields:

| Field    | Meaning                                                        |
| -------- | -------------------------------------------------------------- |
| `id`     | Problem number/identifier (used for sorting and the dropdown)  |
| `title`  | Title shown in the dropdown                                    |
| `method` | Method name on the `Solution` class that the judge calls       |
| `tests`  | Non-empty array of `{ "input": {...}, "expected": ... }` cases |

Optional fields:

| Field         | Meaning                                                                   |
| ------------- | ------------------------------------------------------------------------- |
| `difficulty`  | `Easy`, `Medium` or `Hard` (controls the colour only)                     |
| `unordered`   | `true` → top-level list results are compared ignoring order               |
| `timeout`     | Per-case timeout in seconds (default `10`)                                |
| `output_mode` | `"stdout"` → compare captured printed output instead of the return value |
| `types`       | **Required for C++**: map of parameter name → type                        |
| `returns`     | **Required for C++** by the error message, but not actually validated     |

A test may also set `"hidden": true`; hidden cases are only run by **Submit**.

Example (`problems/001-two-sum/tests.json`):

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

### C++ type mapping

`types` values are mapped to C++ by `ctype()`:

| JSON type | C++ type        |
| --------- | --------------- |
| `int`     | `int`           |
| `long`    | `long long`     |
| `double`  | `double`        |
| `bool`    | `bool`          |
| `string`  | `string`        |
| `T[]`     | `vector<T>`     |

Anything else raises a `KeyError`, which surfaces as `Runner failed: ...`. Nested arrays
such as `int[][]` work because `T[]` is resolved recursively.

## How the judge works

All submissions run in a fresh temporary directory (never in the problem folder).

- **Python** — the solution file is `exec`'d in a namespace that pre-imports `typing`,
  `collections`, `math`, `heapq`, `itertools`, `functools` and `bisect`, then
  `Solution().<method>(**input)` is called per case. `stdout` is captured per case.
- **C++** — `g++ -O2 -std=c++17` compiles your code together with a generated
  `main.cpp` that contains a small JSON-ish reader/printer. Each test's arguments are
  fed on stdin and the result is read back from `result.json`. Compilation is allowed
  120 s.
- **JavaScript** — the file is wrapped with `new Function(...)`, `Solution` is
  instantiated per case, and `console.log` is captured.

Timeout handling (default 10 s per case) and missing-tool errors are reported in the UI
rather than crashing the app.

## Known errors and bugs (current code, v1.0)

These are real issues present in `app.py` as committed to this branch. Nothing here has
been fixed yet — this section documents them.

1. **Literal-backslash escape bug in the "skipped problems" warning** — `app.py:296`:
   ```python
   messagebox.showwarning("Some problems were skipped", "\\n".join(errors))
   ```
   `"\\n"` is a backslash followed by `n`, not a newline, so the warning dialog joins all
   messages with the visible text `\n`. Should be `"\n".join(errors)`.

2. **Literal-backslash escape bug in stdout comparison** — `app.py:364`:
   ```python
   actual_value.rstrip("\\r\\n"), expected_value.rstrip("\\r\\n")
   ```
   This strips the *characters* `\`, `r` and `n` from the end of the output instead of
   trailing CR/LF. Outputs ending in `r`, `n` or `\` can therefore be truncated and
   wrongly accepted (for example `"patterrn"` becomes `"patte"`). Should be
   `.rstrip("\r\n")`.

3. **`returns` is not validated** — `app.py:151` only checks for a `types` map, although
   its message and this README's format require both `types` and `returns` for C++.

4. **Problems are sorted as strings, not numbers** — `app.py:282` sorts by
   `str(id)`, so with ids 2, 10 and 100 the order is `10, 100, 2`. Zero-padded ids
   (as in the samples) avoid this.

5. **GCC DLL error is only mitigated for the default MSYS2 path** — if `cc1plus.exe`
   cannot find `libgcc_s_seh-1.dll`, or `g++` works in the MSYS2 terminal but not when
   launched from Explorer, `windows_compiler_env()` prepends `C:\msys64\ucrt64\bin` and
   `C:\msys64\usr\bin`. Installations elsewhere (MinGW-w64, `C:\msys64\mingw64`, another
   drive) are only found by `find_cpp_compiler()`; their runtime folders are not added to
   `PATH`, so the same DLL error can still occur. `README_GCC_FIX.txt` describes this fix.

6. **`run.bat` and `app.py` may choose different interpreters** — `run.bat` tries
   `py -3` first, while `app.py:8` resolves `python` first and only then `py`. If
   `python` is the Microsoft Store stub or another version, the app can run under a
   different interpreter than the one used to launch it.

7. **Runner exit codes are ignored** — `app.py:189-190` does not check the return code
   of the Python/JS runner. A crash before writing `out.json` is reported only as
   `Runner failed: ...`, hiding the real cause.

8. **Not a sandbox** — user code is executed directly (`exec`, compiled binary, Node.js)
   with full user permissions. There are no resource limits other than the per-case
   timeout.

9. **`unordered` only handles a top-level list** — nested structures and non-list
   results are compared exactly.

10. **Scratch files pollute the repo** — `app.py:349` writes `user_solution.<ext>` into
    the problem directory on every Run/Submit (there is already an untracked
    `problems/001-two-sum/user_solution.cpp`). These files are not needed to run the app.

11. **Cosmetic: highlighting is language-agnostic** — the same keyword regex
    (`KEYWORDS`) is used for Python, C++ and JavaScript, so some keywords are coloured
    in the wrong language and some language-specific keywords are not coloured at all.

### Environment errors you may see

| Message / symptom | Cause / fix |
| ----------------- | ----------- |
| `g++ was not found...` | No C++ compiler on `PATH`. Install MSYS2 UCRT64 GCC and add `C:\msys64\ucrt64\bin` to `PATH`. |
| `cc1plus.exe - Entry Point Not Found` / `libgcc_s_seh-1.dll` missing | MSYS2 runtime DLLs are not on the child-process `PATH`; see item 5 and `README_GCC_FIX.txt`. |
| `Node.js not found. Install it from nodejs.org...` | Node.js is not installed or not on `PATH`. |
| `tests.json needs a "types" map ... and "returns" for C++` | Add `types` (and `returns`) to that problem's `tests.json`. |
| `Some problems were skipped` warning on one line with `\n` | Bug 1 above. |
| A stdout-mode answer that ends in `r`, `n` or `\` is wrongly accepted | Bug 2 above. |
| `Python 3 was not found.` from `run.bat` | Python is not installed or `py`/`python` is not on `PATH`. |
| `LocalCode closed with an error.` | The app exited non-zero; run `python app.py` in a terminal to see the traceback. |
