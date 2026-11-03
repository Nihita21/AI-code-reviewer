import { useEffect, useRef } from "react";
import Editor from "@monaco-editor/react";

const THEME = "paper";

// A light editor theme that belongs to the lavender / pink palette.
function definePaperTheme(monaco) {
  monaco.editor.defineTheme(THEME, {
    base: "vs",
    inherit: true,
    rules: [
      { token: "comment", foreground: "8c7fa6", fontStyle: "italic" },
      { token: "keyword", foreground: "b8287f" },
      { token: "string", foreground: "5a3fa0" },
      { token: "number", foreground: "8f6400" },
      { token: "type", foreground: "2b6a8f" },
    ],
    colors: {
      "editor.background": "#ffffff",
      "editor.foreground": "#241b33",
      "editorLineNumber.foreground": "#a89bc0",
      "editorLineNumber.activeForeground": "#b8287f",
      "editorCursor.foreground": "#b8287f",
      "editor.selectionBackground": "#e6d9fa",
      "editor.lineHighlightBackground": "#f6f1fa",
      "editorGutter.background": "#ffffff",
      "editorIndentGuide.background1": "#eee6f8",
    },
  });
}

function CodeEditor({ language, code, setCode, issues, activeLine, hoverLine, onReady, onRun }) {
  const editorRef = useRef(null);
  const monacoRef = useRef(null);
  const issueMarks = useRef(null);
  const activeMark = useRef(null);
  const hoverMark = useRef(null);
  const runRef = useRef(onRun);

  useEffect(() => {
    runRef.current = onRun;
  }, [onRun]);

  // Highlight every issue line, with the details on hover.
  const showIssues = (list) => {
    const editor = editorRef.current;
    const monaco = monacoRef.current;
    const model = editor?.getModel();

    if (!monaco || !model) {
      return;
    }

    issueMarks.current?.clear();
    issueMarks.current = editor.createDecorationsCollection(
      list.map((issue) => {
        const line = Math.min(Math.max(1, issue.line), model.getLineCount());

        return {
          range: new monaco.Range(line, 1, line, 1),
          options: {
            isWholeLine: true,
            className: `issue-line--${issue.severity}`,
            linesDecorationsClassName: `issue-gutter issue-gutter--${issue.severity}`,
            hoverMessage: { value: `**${issue.title}**\n\n${issue.suggestion}` },
          },
        };
      }),
    );
  };

  // The line the user jumped to from a note.
  const showActiveLine = (line) => {
    const editor = editorRef.current;
    const monaco = monacoRef.current;

    if (!monaco || !editor) {
      return;
    }

    activeMark.current?.clear();
    activeMark.current = line
      ? editor.createDecorationsCollection([
          {
            range: new monaco.Range(line, 1, line, 1),
            options: { isWholeLine: true, className: "active-line" },
          },
        ])
      : null;
  };

  const showHoverLine = (line) => {
    const editor = editorRef.current;
    const monaco = monacoRef.current;

    if (!monaco || !editor) {
      return;
    }

    hoverMark.current?.clear();
    hoverMark.current = line
      ? editor.createDecorationsCollection([
          {
            range: new monaco.Range(line, 1, line, 1),
            options: { isWholeLine: true, className: "hover-line" },
          },
        ])
      : null;
  };

  useEffect(() => {
    showIssues(issues);
  }, [issues]);

  useEffect(() => {
    showActiveLine(activeLine);
  }, [activeLine]);

  useEffect(() => {
    showHoverLine(hoverLine);
  }, [hoverLine]);

  const handleMount = (editor, monaco) => {
    editorRef.current = editor;
    monacoRef.current = monaco;
    onReady?.(editor);

    // Ctrl/Cmd + Enter runs the review without leaving the keyboard.
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
      runRef.current?.();
    });

    // The code font loads from the web; re-measure once it is ready.
    document.fonts?.ready.then(() => monaco.editor.remeasureFonts());

    showIssues(issues);
    showActiveLine(activeLine);
  };

  const handleChange = (value) => {
    setCode(value || "");
    // The notes refer to line numbers, which shift as soon as the user edits.
    showIssues([]);
    showActiveLine(null);
    showHoverLine(null);
  };

  return (
    <Editor
      height="100%"
      language={language}
      value={code}
      onChange={handleChange}
      onMount={handleMount}
      beforeMount={definePaperTheme}
      theme={THEME}
      loading={<div className="editor-loading">Loading editor…</div>}
      options={{
        minimap: { enabled: false },
        fontSize: 14,
        fontFamily: "'JetBrains Mono', ui-monospace, Menlo, Consolas, monospace",
        lineHeight: 22,
        padding: { top: 16, bottom: 16 },
        scrollBeyondLastLine: false,
        automaticLayout: true,
        renderLineHighlight: "none",
        lineDecorationsWidth: 10,
      }}
    />
  );
}

export default CodeEditor;
