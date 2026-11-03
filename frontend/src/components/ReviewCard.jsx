import "./ReviewCard.css";

const SOURCE_LABELS = {
  ast: "Syntax checks",
  ruff: "Ruff",
  bandit: "Bandit",
  radon: "Radon",
  ai: "AI",
};

function scoreTone(score) {
  if (score >= 80) return "good";
  if (score >= 50) return "fair";
  return "poor";
}

function Metric({ label, value }) {
  return (
    <div className="metric">
      <div className="metricValue">{value}</div>
      <div className="metricLabel">{label}</div>
    </div>
  );
}

function ReviewCard({ review, onSelectLine }) {
  if (!review) {
    return null;
  }

  const { score, summary, ai_summary: aiSummary, issues, metrics, warnings } = review;

  return (
    <section className="reviewCard">
      <div className="reviewHeader">
        <div className={`scoreBadge ${scoreTone(score)}`} aria-label={`Score ${score} out of 100`}>
          <span className="scoreValue">{score}</span>
          <span className="scoreMax">/100</span>
        </div>

        <div>
          <h2 className="reviewTitle">Review result</h2>
          <p className="reviewSummary">{summary}</p>
        </div>
      </div>

      {aiSummary && (
        <div className="aiSummary">
          <h3>AI assessment</h3>
          <p>{aiSummary}</p>
        </div>
      )}

      {metrics && (
        <div className="metrics">
          <Metric label="Lines of code" value={metrics.lines_of_code} />
          <Metric label="Functions" value={metrics.functions} />
          <Metric label="Avg. complexity" value={metrics.average_complexity} />
          <Metric label="Max complexity" value={metrics.max_complexity} />
          <Metric label="Maintainability" value={metrics.maintainability_index} />
        </div>
      )}

      {warnings?.length > 0 && (
        <ul className="warnings">
          {warnings.map((warning) => (
            <li key={warning}>{warning}</li>
          ))}
        </ul>
      )}

      <h3 className="sectionTitle">Issues ({issues.length})</h3>

      {issues.length === 0 ? (
        <p className="emptyState">No issues found. Nice work!</p>
      ) : (
        <ul className="issueList">
          {issues.map((issue, index) => (
            <li key={`${issue.source}-${issue.line}-${index}`} className="issue">
              <div className="issueTop">
                <span className={`severity ${issue.severity}`}>{issue.severity}</span>
                <span className="issueTitle">{issue.title}</span>
              </div>

              <p className="issueSuggestion">{issue.suggestion}</p>

              <div className="issueMeta">
                <button
                  type="button"
                  className="lineLink"
                  onClick={() => onSelectLine?.(issue.line)}
                >
                  Line {issue.line}
                </button>
                <span className="sourceTag">{SOURCE_LABELS[issue.source] ?? issue.source}</span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export default ReviewCard;
