function LanguageSelector() {
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
        style={{
          width: "220px",
          padding: "10px",
          borderRadius: "6px",
          fontSize: "16px",
        }}
      >
        <option>Python</option>
        <option>JavaScript</option>
        <option>Java</option>
        <option>C++</option>
      </select>
    </div>
  );
}

export default LanguageSelector;