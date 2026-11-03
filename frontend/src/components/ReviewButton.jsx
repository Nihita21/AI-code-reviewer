import { COLORS } from "../styles/colors";

function ReviewButton({ onClick, loading = false, disabled = false }) {
  const inactive = loading || disabled;

  return (
    <button
      type="button"
      onClick={onClick}
      disabled={inactive}
      style={{
        backgroundColor: inactive ? COLORS.secondary : COLORS.primary,
        color: "#FFFFFF",
        border: "none",
        padding: "14px 28px",
        borderRadius: "12px",
        fontSize: "16px",
        fontWeight: "600",
        cursor: inactive ? "not-allowed" : "pointer",
        opacity: inactive ? 0.7 : 1,
        marginTop: "20px",
        transition: "0.3s",
      }}
    >
      {loading ? "Reviewing…" : "Review Code"}
    </button>
  );
}

export default ReviewButton;
