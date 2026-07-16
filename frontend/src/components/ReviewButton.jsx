import { COLORS } from "../styles/colors";

function ReviewButton() {
  return (
    <button
      style={{
        backgroundColor: COLORS.primary,
        color: COLORS.textWhite,
        border: "none",
        padding: "14px 28px",
        borderRadius: "12px",
        fontSize: "16px",
        fontWeight: "600",
        cursor: "pointer",
        marginTop: "20px",
        transition: "0.3s",
      }}
    >
      🌸 Review Code
    </button>
  );
}

export default ReviewButton;