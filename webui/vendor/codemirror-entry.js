// Source for the locally bundled CodeMirror build.
// Rebuild with: npm run build:editor  (from the webui folder)
import { basicSetup, EditorView } from "codemirror";
import { keymap } from "@codemirror/view";
import { indentUnit, indentOnInput } from "@codemirror/language";
import { indentWithTab } from "@codemirror/commands";
import { python } from "@codemirror/lang-python";
import { cpp } from "@codemirror/lang-cpp";
import { javascript } from "@codemirror/lang-javascript";
import { oneDark } from "@codemirror/theme-one-dark";

window.LocalCodeCodeMirror = {
  cm: {
    basicSetup, EditorView, keymap, indentUnit, indentOnInput, indentWithTab,
    python, cpp, javascript, oneDark
  }
};
