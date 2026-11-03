import { useCallback, useEffect, useRef, useState } from "react";
import api, { errorMessage } from "../services/api";
import { SAMPLE_CODE } from "../sample";
import Header from "../components/Header";
import EditorPane from "../components/EditorPane";
import ResultsPane from "../components/ResultsPane";
import "./Home.css";

// Used until the backend tells us what it supports.
const DEFAULT_CAPABILITIES = {
  ai_enabled: false,
  ai_model: null,
  languages: [{ id: "python", label: "Python", static_analysis: true, ai_review: false }],
};

const NO_ISSUES = []; // stable reference so the editor does not re-apply markers on every render
const SHORTCUT = /Mac|iPhone|iPad/i.test(navigator.userAgent) ? "⌘ Enter" : "Ctrl Enter";

function Home() {
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState("python");
  const [capabilities, setCapabilities] = useState(DEFAULT_CAPABILITIES);
  const [useAI, setUseAI] = useState(true);
  const [review, setReview] = useState(null);
  const [reviewedCode, setReviewedCode] = useState("");
  const [run, setRun] = useState(0);
  const [activeLine, setActiveLine] = useState(null);
  const [hoverLine, setHoverLine] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const editorRef = useRef(null);

  useEffect(() => {
    let cancelled = false;

    api
      .get("/capabilities")
      .then(({ data }) => {
        if (!cancelled) setCapabilities(data);
      })
      .catch((err) => {
        if (!cancelled) setError(errorMessage(err));
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const changeCode = (value) => {
    setCode(value);
    setActiveLine(null);
  };

  const aiActive = capabilities.ai_enabled && useAI;
  const selected = capabilities.languages.find((item) => item.id === language);
  // Languages without static analysis can only be reviewed by the AI.
  const needsAI = Boolean(selected && !selected.static_analysis && !aiActive);
  const stale = review !== null && code !== reviewedCode;

  const handleReview = useCallback(async () => {
    if (loading || needsAI) {
      return;
    }

    if (!code.trim()) {
      setError("Paste or type some code to review first.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const { data } = await api.post("/review", { language, code, use_ai: aiActive });

      setReview(data);
      setReviewedCode(code);
      setRun((count) => count + 1);
    } catch (err) {
      setReview(null);
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [loading, needsAI, code, language, aiActive]);

  const loadExample = () => {
    setLanguage("python");
    setCode(SAMPLE_CODE);
    setActiveLine(null);
    setReview(null);
    setError("");
  };

  const goToLine = (line) => {
    const editor = editorRef.current;

    if (!editor) {
      return;
    }

    setActiveLine(line);
    editor.revealLineInCenter(line);
    editor.setPosition({ lineNumber: line, column: 1 });
    editor.focus();
  };

  return (
    <div className="app">
      <Header
        languages={capabilities.languages}
        language={language}
        onLanguageChange={setLanguage}
        aiEnabled={capabilities.ai_enabled}
        aiModel={capabilities.ai_model}
        aiActive={aiActive}
        onAiChange={setUseAI}
        onReview={handleReview}
        loading={loading}
        blocked={needsAI}
        shortcut={SHORTCUT}
      />

      <main className="workspace">
        <EditorPane
          code={code}
          setCode={changeCode}
          language={language}
          issues={review?.issues ?? NO_ISSUES}
          activeLine={activeLine}
          hoverLine={hoverLine}
          onReady={(editor) => {
            editorRef.current = editor;
          }}
          onRun={handleReview}
          onLoadExample={loadExample}
          notice={
            needsAI
              ? `${selected.label} is reviewed by the AI only. Turn on AI review to continue.`
              : ""
          }
        />

        <ResultsPane
          review={review}
          run={run}
          sourceCode={reviewedCode}
          loading={loading}
          error={error}
          stale={stale}
          aiEnabled={capabilities.ai_enabled}
          aiActive={aiActive}
          aiModel={capabilities.ai_model}
          onSelectLine={goToLine}
          onPreviewLine={setHoverLine}
          onRerun={handleReview}
          onLoadExample={loadExample}
        />
      </main>
    </div>
  );
}

export default Home;
