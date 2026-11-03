function LanguageSelector({ languages, language, setLanguage, aiAvailable }) {
  return (
    <div>
      <label
        htmlFor="language"
        style={{
          display: "block",
          marginBottom: "8px",
          fontWeight: "bold",
        }}
      >
        Language
      </label>

      <select
        id="language"
        value={language}
        onChange={(e) => setLanguage(e.target.value)}
        style={{
          width: "220px",
          padding: "10px",
          borderRadius: "6px",
          fontSize: "16px",
        }}
      >
        {languages.map((item) => (
          <option
            key={item.id}
            value={item.id}
            // Only Python has static analysis; other languages need the AI.
            disabled={!item.static_analysis && !aiAvailable}
          >
            {item.label}
            {item.static_analysis ? "" : " (AI only)"}
          </option>
        ))}
      </select>
    </div>
  );
}

export default LanguageSelector;
