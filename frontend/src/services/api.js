import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
  timeout: 60000, // AI reviews can take a while
});

/** Turn any axios error into a message that is safe to show to the user. */
export function errorMessage(error) {
  if (error.response) {
    const detail = error.response.data?.detail;

    if (typeof detail === "string") {
      return detail;
    }

    // FastAPI validation errors arrive as a list of { msg, loc, ... }.
    if (Array.isArray(detail) && detail.length > 0) {
      return detail.map((item) => item.msg).join("; ");
    }

    return `The server responded with an error (HTTP ${error.response.status}).`;
  }

  if (error.code === "ECONNABORTED" || error.code === "ETIMEDOUT") {
    return "The request timed out. Try reviewing a smaller piece of code.";
  }

  return `Cannot reach the backend at ${api.defaults.baseURL}. Is it running?`;
}

export default api;
