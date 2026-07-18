import { useState } from "react";
import api from "../services/api";

import Navbar from "../components/Navbar";
import LanguageSelector from "../components/LanguageSelector";
import CodeEditor from "../components/CodeEditor";
import ReviewButton from "../components/ReviewButton";
import ReviewCard from "../components/ReviewCard";

import "../App.css";

function Home() {
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState("python");
  const [review, setReview] = useState(null);

  const handleReview = async () => {
    try {
      const response = await api.post("/review", {
        language,
        code,
      });

      setReview(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <>
      <Navbar />

      <div className="page">
        <div className="section">
          <LanguageSelector
            language={language}
            setLanguage={setLanguage}
          />
        </div>

        <div className="section">
          <CodeEditor
            language={language}
            code={code}
            setCode={setCode}
          />
        </div>

        <div className="section">
          <ReviewButton onClick={handleReview} />
        </div>

        <div className="section">
          <ReviewCard review={review} />
        </div>
      </div>
    </>
  );
}

export default Home;