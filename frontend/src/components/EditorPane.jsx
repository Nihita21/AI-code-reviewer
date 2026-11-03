import CodeEditor from "./CodeEditor";
import "./EditorPane.css";

function EditorPane({
  code,
  setCode,
  language,
  issues,
  activeLine,
  hoverLine,
  onReady,
  onRun,
  onLoadExample,
  notice,
}) {
  const lineCount = code ? code.split("\n").length : 0;

  return (
    <section className="editor-pane" aria-label="Code editor">
      <div className="editor-pane__bar">
        <span className="editor-pane__title">Your code</span>
        <span className="editor-pane__count">
          {lineCount === 1 ? "1 line" : `${lineCount} lines`}
        </span>
      </div>

      <div className="editor-pane__body">
        <CodeEditor
          language={language}
          code={code}
          setCode={setCode}
          issues={issues}
          activeLine={activeLine}
          hoverLine={hoverLine}
          onReady={onReady}
          onRun={onRun}
        />
      </div>

      <div className="editor-pane__foot">
        <span className={notice ? "editor-pane__notice" : undefined}>
          {notice || "Editing clears the highlights until you review again."}
        </span>
        <button type="button" className="editor-pane__example" onClick={onLoadExample}>
          Load an example
        </button>
      </div>
    </section>
  );
}

export default EditorPane;
