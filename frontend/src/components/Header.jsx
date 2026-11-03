import "./Header.css";

function Header({
  languages,
  language,
  onLanguageChange,
  aiEnabled,
  aiModel,
  aiActive,
  onAiChange,
  onReview,
  loading,
  blocked,
  shortcut,
}) {
  return (
    <header className="header">
      <h1 className="wordmark">
        <span className="wordmark__cursor" aria-hidden="true" />
        Code Reviewer
      </h1>

      <div className="header__controls">
        <label className="control">
          <span className="control__label">Language</span>
          <select
            className="control__select"
            value={language}
            onChange={(event) => onLanguageChange(event.target.value)}
          >
            {languages.map((item) => (
              <option
                key={item.id}
                value={item.id}
                // Only Python has built-in analysis; everything else needs the AI.
                disabled={!item.static_analysis && !aiEnabled}
              >
                {item.label}
                {item.static_analysis ? "" : " (AI only)"}
              </option>
            ))}
          </select>
        </label>

        <label
          className={`control control--check${aiEnabled ? "" : " control--off"}`}
          title={
            aiEnabled
              ? `Model: ${aiModel}`
              : "Set OPENAI_API_KEY on the backend to enable AI review"
          }
        >
          <input
            type="checkbox"
            checked={aiActive}
            disabled={!aiEnabled}
            onChange={(event) => onAiChange(event.target.checked)}
          />
          <span className="control__label">AI review</span>
        </label>

        <button type="button" className="run" onClick={onReview} disabled={loading || blocked}>
          {loading ? "Reviewing…" : "Review code"}
          {!loading && <kbd className="run__key">{shortcut}</kbd>}
        </button>
      </div>
    </header>
  );
}

export default Header;
