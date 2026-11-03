import { useState } from "react";

const SEVERITIES = ["high", "medium", "low"];
const SEVERITY_LABELS = { high: "High", medium: "Medium", low: "Low" };
const SOURCE_LABELS = {
  ast: "syntax checks",
  ruff: "Ruff",
  bandit: "Bandit",
  radon: "Radon",
  ai: "the AI",
};

function IssueList({ issues, sourceCode, onSelectLine, onPreviewLine }) {
  const [filter, setFilter] = useState("all");

  if (issues.length === 0) {
    return <p className="clean">No issues found. The analyzers had nothing to flag.</p>;
  }

  const lines = sourceCode.split("\n");
  const counts = Object.fromEntries(
    SEVERITIES.map((level) => [level, issues.filter((issue) => issue.severity === level).length]),
  );
  const visible = filter === "all" ? issues : issues.filter((issue) => issue.severity === filter);
  const tabs = [["all", "All", issues.length]].concat(
    SEVERITIES.filter((level) => counts[level] > 0).map((level) => [
      level,
      SEVERITY_LABELS[level],
      counts[level],
    ]),
  );

  return (
    <section aria-label="Notes on your code">
      <div className="notes__bar">
        <h2 className="notes__title">Notes on your code</h2>

        <div className="tabs" role="group" aria-label="Filter by severity">
          {tabs.map(([id, label, count]) => (
            <button
              key={id}
              type="button"
              className="tabs__item"
              aria-pressed={filter === id}
              onClick={() => setFilter(id)}
            >
              {label} <span className="tabs__count">{count}</span>
            </button>
          ))}
        </div>
      </div>

      <ol className="notes__list">
        {visible.map((issue, index) => {
          // Quote the line the note is about, like a review comment on a pull request.
          const excerpt = (lines[issue.line - 1] ?? "").trimEnd();

          return (
            <li
              key={`${issue.source}-${issue.line}-${index}`}
              className={`note note--${issue.severity}`}
              // Hovering a note previews its line in the editor.
              onMouseEnter={() => onPreviewLine(issue.line)}
              onMouseLeave={() => onPreviewLine(null)}
              onFocus={() => onPreviewLine(issue.line)}
              onBlur={() => onPreviewLine(null)}
            >
              <div className="note__head">
                <button
                  type="button"
                  className="line-ref"
                  onClick={() => onSelectLine(issue.line)}
                  aria-label={`Go to line ${issue.line}`}
                >
                  Line {issue.line}
                </button>
                <span className="severity">{SEVERITY_LABELS[issue.severity]}</span>
              </div>

              <div className="note__body">
                <h3 className="note__title">{issue.title}</h3>

                {excerpt.trim() !== "" && (
                  <pre className="excerpt">
                    <span className="excerpt__no" aria-hidden="true">
                      {issue.line}
                    </span>
                    <code>{excerpt}</code>
                  </pre>
                )}

                <p className="note__suggestion">{issue.suggestion}</p>
                <p className="note__source">Found by {SOURCE_LABELS[issue.source] ?? issue.source}</p>
              </div>
            </li>
          );
        })}
      </ol>
    </section>
  );
}

export default IssueList;
