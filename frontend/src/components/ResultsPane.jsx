import ScoreSummary from "./ScoreSummary";
import IssueList from "./IssueList";
import "./ResultsPane.css";

// Code lines with the problem lines highlighted, and a review note pointing at one of them.
const ART_ROWS = [
  { width: 170, indent: 0 },
  { width: 230, indent: 0 },
  { width: 120, indent: 24, flagged: true },
  { width: 190, indent: 24 },
  { width: 150, indent: 24, flagged: true },
  { width: 90, indent: 0 },
  { width: 200, indent: 0 },
];

function Illustration() {
  return (
    <svg
      className="art"
      viewBox="0 0 440 196"
      role="img"
      aria-label="Lines of code with two problem lines highlighted in pink and a review note beside them"
    >
      <rect x="6" y="6" width="428" height="184" rx="6" fill="#241b33" />
      <rect x="2" y="2" width="428" height="184" rx="6" fill="#ffffff" stroke="#241b33" strokeWidth="2" />

      {ART_ROWS.map((row, index) => {
        const y = 20 + index * 22;

        return (
          <g key={index}>
            {row.flagged && <rect x="30" y={y - 5} width="262" height="18" fill="#f58fcb" opacity="0.7" />}
            <rect x="14" y={y} width="10" height="8" rx="2" fill="#cdb8f5" />
            <rect x={36 + row.indent} y={y} width={row.width} height="8" rx="2" fill="#241b33" opacity="0.82" />
          </g>
        );
      })}

      <rect x="304" y="62" width="120" height="62" rx="4" fill="#241b33" transform="translate(4 4)" />
      <rect x="304" y="62" width="120" height="62" rx="4" fill="#ece3fb" stroke="#241b33" strokeWidth="2" />
      <rect x="314" y="72" width="8" height="8" fill="#c0243f" />
      <rect x="328" y="72" width="50" height="8" rx="2" fill="#241b33" />
      <rect x="314" y="90" width="98" height="6" rx="2" fill="#62577a" />
      <rect x="314" y="102" width="70" height="6" rx="2" fill="#62577a" />
    </svg>
  );
}

function EmptyState({ aiEnabled, aiActive, aiModel, onLoadExample }) {
  let aiStatus = "Off: set OPENAI_API_KEY on the backend";
  if (aiActive) aiStatus = `On: ${aiModel}`;
  else if (aiEnabled) aiStatus = "Off: switched off above";

  const checks = [
    ["Syntax checks", "Unused imports, mutable default arguments, empty except blocks", "On"],
    ["Ruff", "Bugs, undefined names and style problems", "On"],
    ["Bandit", "Security problems such as eval and hard-coded passwords", "On"],
    ["Radon", "How complex and how maintainable the code is", "On"],
    ["AI review", "A written assessment. The only check for JavaScript, Java and C++", aiStatus],
  ];

  return (
    <div className="state">
      <Illustration />
      <p className="state__lead">Paste code on the left, then press Review.</p>
      <p className="state__text">
        Python gets four built-in checks. Each problem comes back tied to the line it is on.
      </p>

      <dl className="checks">
        {checks.map(([name, what, status]) => (
          <div className="checks__row" key={name}>
            <dt>{name}</dt>
            <dd className="checks__what">{what}</dd>
            <dd className={`checks__status${status === "On" || status.startsWith("On:") ? " checks__status--on" : ""}`}>
              {status}
            </dd>
          </div>
        ))}
      </dl>

      <button type="button" className="button" onClick={onLoadExample}>
        Load an example
      </button>
    </div>
  );
}

function LoadingState({ aiActive }) {
  return (
    <div className="state">
      <p className="state__lead">Reviewing your code…</p>
      <p className="state__text">
        {aiActive
          ? "Running the analyzers, then asking the AI for a second opinion. This can take a few seconds."
          : "Running the analyzers."}
      </p>
      <div className="segments segments--busy" aria-hidden="true">
        {Array.from({ length: 10 }, (_, index) => (
          <span key={index} className="segment" style={{ "--i": index }} />
        ))}
      </div>
    </div>
  );
}

function ErrorState({ message, onRetry }) {
  return (
    <div className="state" role="alert">
      <p className="state__lead state__lead--error">The review didn’t run.</p>
      <p className="state__text">{message}</p>
      <button type="button" className="button" onClick={onRetry}>
        Try again
      </button>
    </div>
  );
}

function ResultsPane({
  review,
  run,
  sourceCode,
  loading,
  error,
  stale,
  aiEnabled,
  aiActive,
  aiModel,
  onSelectLine,
  onPreviewLine,
  onRerun,
  onLoadExample,
}) {
  let content;

  if (loading) {
    content = <LoadingState aiActive={aiActive} />;
  } else if (error) {
    content = <ErrorState message={error} onRetry={onRerun} />;
  } else if (review) {
    content = (
      <div key={run} className="review">
        {stale && (
          <p className="stale">
            You edited the code after this review, so the line numbers below may no longer match.{" "}
            <button type="button" className="stale__action" onClick={onRerun}>
              Review again
            </button>
          </p>
        )}
        <ScoreSummary review={review} />
        <IssueList
          issues={review.issues}
          sourceCode={sourceCode}
          onSelectLine={onSelectLine}
          onPreviewLine={onPreviewLine}
        />
      </div>
    );
  } else {
    content = (
      <EmptyState
        aiEnabled={aiEnabled}
        aiActive={aiActive}
        aiModel={aiModel}
        onLoadExample={onLoadExample}
      />
    );
  }

  return (
    <section className="results" aria-label="Review results" aria-live="polite" aria-busy={loading}>
      <div className="results__inner">{content}</div>
    </section>
  );
}

export default ResultsPane;
