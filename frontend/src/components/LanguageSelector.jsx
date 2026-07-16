function LanguageSelector({ language, setLanguage }) {
  return (
    <div style={{ marginBottom: "20px" }}>
      <label
        style={{
          display: "block",
          marginBottom: "8px",
          fontWeight: "bold",
        }}
      >
        Language
      </label>

      <select
        value={language}
        onChange={(e) => setLanguage(e.target.value)}
        style={{
          width: "220px",
          padding: "10px",
          borderRadius: "6px",
          fontSize: "16px",
        }}
      >
        <option value="python">Python</option>
        <option value="javascript">JavaScript</option>
        <option value="java">Java</option>
        <option value="cpp">C++</option>
      </select>
    </div>
  );
}

export default LanguageSelector;