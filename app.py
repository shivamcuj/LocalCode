"""LocalCode desktop application powered by CodeMirror 6."""
import json
import os
import threading
from pathlib import Path

import webview
import engine

ROOT = Path(getattr(__import__("sys"), "_MEIPASS", Path(__file__).resolve().parent))
PROBLEMS_DIR = ROOT / "problems"
LANGS = engine.LANGS


class LocalCodeAPI:
    def __init__(self):
        self.window = None
        self.problems = []
        self.drafts = {}
        self.lock = threading.Lock()
        self.refresh_problems()

    def refresh_problems(self):
        found, errors = [], []
        if not PROBLEMS_DIR.is_dir():
            PROBLEMS_DIR.mkdir(parents=True, exist_ok=True)
        for folder in sorted(PROBLEMS_DIR.iterdir()):
            if not folder.is_dir():
                continue
            tests_file, statement_file = folder / "tests.json", folder / "problem.md"
            if not tests_file.is_file():
                continue
            if not statement_file.is_file():
                errors.append(f"{folder.name}: missing problem.md")
                continue
            try:
                meta = json.loads(tests_file.read_text(encoding="utf8"))
                missing = [k for k in ("id", "title", "method", "tests") if k not in meta]
                if missing:
                    errors.append(f"{folder.name}: tests.json missing {', '.join(missing)}")
                    continue
                if not isinstance(meta["tests"], list) or not meta["tests"]:
                    errors.append(f"{folder.name}: tests must be a non-empty array")
                    continue
                meta["dir"] = str(folder)
                found.append(meta)
            except Exception as exc:
                errors.append(f"{folder.name}: {exc}")
        self.problems = sorted(found, key=lambda m: str(m.get("id", "")))
        return errors

    def list_problems(self):
        errors = self.refresh_problems()
        return {
            "problems": [{"index": i, "id": p["id"], "title": p["title"],
                          "difficulty": p.get("difficulty", "")}
                         for i, p in enumerate(self.problems)],
            "warnings": errors,
        }

    def get_problem(self, index, language="python"):
        try:
            i = int(index)
            if i < 0 or i >= len(self.problems):
                raise IndexError("Problem selection is out of range")
            if language not in LANGS:
                raise ValueError("Unsupported language")
            meta = self.problems[i]
            key = (meta["dir"], language)
            if key in self.drafts:
                code = self.drafts[key]
            else:
                starter = Path(meta["dir"]) / LANGS[language][1]
                code = starter.read_text(encoding="utf8") if starter.is_file() else engine.DEFAULT[language]
            visible_count = sum(1 for t in meta["tests"] if not t.get("hidden"))
            return {
                "ok": True, "index": i, "id": meta["id"], "title": meta["title"],
                "difficulty": meta.get("difficulty", ""),
                "statement": (Path(meta["dir"]) / "problem.md").read_text(encoding="utf8"),
                "code": code, "language": language,
                "visible_count": visible_count, "total_count": len(meta["tests"]),
            }
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def save_draft(self, index, language, code):
        try:
            meta = self.problems[int(index)]
            if language not in LANGS:
                raise ValueError("Unsupported language")
            self.drafts[(meta["dir"], language)] = str(code)
            return {"ok": True}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def run_solution(self, index, language, code, submit=False):
        try:
            meta = self.problems[int(index)]
            if language not in LANGS:
                raise ValueError("Unsupported language")
            code = str(code)
            self.drafts[(meta["dir"], language)] = code
            ext = LANGS[language][2]
            (Path(meta["dir"]) / f"user_solution.{ext}").write_text(code, encoding="utf8")
            tests = [t for t in meta["tests"] if submit or not t.get("hidden")]
            out = engine.judge(language, code, meta, tests)
            if out.get("tle"):
                return {"ok": True, "verdict": "Time Limit Exceeded", "passed": 0,
                        "total": len(tests), "results": []}
            if "error" in out:
                return {"ok": False, "error": out["error"]}
            rows, passed, verdict = [], 0, "Accepted"
            for case_no, (test, result) in enumerate(zip(tests, out.get("results", [])), 1):
                expected = test.get("expected")
                actual = result.get("actual")
                if "error" in result:
                    ok = False
                    status = "Time Limit" if "Time Limit" in result["error"] else "Runtime Error"
                    verdict = "Runtime Error"
                else:
                    compare_actual, compare_expected = actual, expected
                    if meta.get("output_mode") == "stdout" and isinstance(actual, str) and isinstance(expected, str):
                        compare_actual = actual.rstrip("\r\n")
                        compare_expected = expected.rstrip("\r\n")
                    ok = engine.norm(compare_actual, meta.get("unordered")) == engine.norm(compare_expected, meta.get("unordered"))
                    status = "Passed" if ok else "Wrong Answer"
                    if not ok and verdict == "Accepted":
                        verdict = "Wrong Answer"
                if ok:
                    passed += 1
                rows.append({"case": case_no, "status": status, "input": test.get("input", {}),
                             "expected": expected, "actual": actual, "stdout": result.get("stdout", ""),
                             "error": result.get("error", ""), "ms": result.get("ms", 0)})
            if passed == len(tests) and len(rows) == len(tests):
                verdict = "Accepted"
            return {"ok": True, "verdict": verdict, "passed": passed, "total": len(tests),
                    "ms": round(sum(r.get("ms", 0) for r in rows), 2), "results": rows}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def open_problems_folder(self):
        try:
            os.startfile(str(PROBLEMS_DIR))
            return {"ok": True}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}


def main():
    api = LocalCodeAPI()
    page = (ROOT / "webui" / "index.html").resolve().as_uri()
    window = webview.create_window(
        "LocalCode", page, js_api=api, width=1450, height=900,
        min_size=(1050, 680), background_color="#17191f"
    )
    api.window = window
    try:
        webview.start(debug=False, http_server=False)
    except Exception as exc:
        from tkinter import messagebox
        messagebox.showerror(
            "LocalCode could not start",
            "The desktop webview could not be initialized.\n\n"
            "Install or repair Microsoft Edge WebView2 Runtime, then try again.\n\n"
            f"Details: {exc}"
        )


if __name__ == "__main__":
    main()
