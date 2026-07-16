import { COLORS } from "../styles/colors";

function ReviewCard() {
  return (
    <div
      style={{
        background: COLORS.surface,
        padding: "25px",
        borderRadius: "18px",
        marginTop: "35px",
        border: `1px solid ${COLORS.border}`,
      }}
    >
      <h2 style={{ color: COLORS.textPrimary }}>
        Overall Score: 95/100
      </h2>

      <h3 style={{ marginTop: "20px" , color: COLORS.textSecondary }}>Summary</h3>

      <p style={{ color: COLORS.textTertiary }}>
        Your code is clean and readable. Minor improvements are suggested.
      </p>

      <h3 style={{ marginTop: "25px" , color: COLORS.textSecondary }}>Issues</h3>

      <ul style={{ color: COLORS.textTertiary }}>
        <li>Missing docstring</li>
        <li>Add type hints</li>
      </ul>

      <h3 style={{ marginTop: "25px" , color: COLORS.textSecondary }}>Suggestions</h3>

      <ul style={{ color: COLORS.textTertiary }}>
        <li>Use descriptive variable names</li>
        <li>Handle exceptions properly</li>
      </ul>
    </div>
  );
}

export default ReviewCard;