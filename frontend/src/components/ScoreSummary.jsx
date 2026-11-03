const SEGMENTS = 10;

function scoreTone(score) {
  if (score >= 80) return "good";
  if (score >= 50) return "fair";
  return "poor";
}

function gradeWord(score) {
  if (score >= 90) return "Clean.";
  if (score >= 80) return "Solid.";
  if (score >= 50) return "Needs work.";
  return "Rough.";
}

const LEDGER = [
  ["lines_of_code", "Lines of code"],
  ["functions", "Functions"],
  ["average_complexity", "Average complexity"],
  ["max_complexity", "Highest complexity"],
  ["maintainability_index", "Maintainability (0-100)"],
];

function ScoreSummary({ review }) {
  const { score, summary, ai_summary: aiSummary, metrics, warnings } = review;
  const tone = scoreTone(score);
  const filled = Math.round((score / 100) * SEGMENTS);

  return (
    <>
      <section className="verdict" aria-label="Verdict">
        <div className="verdict__row">
          <p className={`stamp stamp--${tone}`}>
            <span className="visually-hidden">Score </span>
            {score}
            <span className="stamp__of">/100</span>
          </p>

          <div>
            <p className="verdict__word">{gradeWord(score)}</p>
            <p className="verdict__text">{summary}</p>
          </div>
        </div>

        <div className="segments" aria-hidden="true">
          {Array.from({ length: SEGMENTS }, (_, index) => (
            <span
              key={index}
              className={index < filled ? `segment segment--${tone}` : "segment"}
              style={{ "--i": index }}
            />
          ))}
        </div>
      </section>

      {aiSummary && (
        <p className="assessment">
          <strong>AI assessment.</strong> {aiSummary}
        </p>
      )}

      {metrics && (
        <dl className="ledger">
          {LEDGER.map(([key, label]) => (
            <div className="ledger__row" key={key}>
              <dt>{label}</dt>
              <dd>{metrics[key]}</dd>
            </div>
          ))}
        </dl>
      )}

      {warnings?.length > 0 && (
        <ul className="warnings">
          {warnings.map((warning) => (
            <li key={warning}>
              <strong>Heads up.</strong> {warning}
            </li>
          ))}
        </ul>
      )}
    </>
  );
}

export default ScoreSummary;
