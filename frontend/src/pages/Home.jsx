import { useState } from "react";
import api from "../services/api";
import Navbar from "../components/Navbar";
import LanguageSelector from "../components/LanguageSelector";
import CodeEditor from "../components/CodeEditor";
import ReviewButton from "../components/ReviewButton";
import ReviewCard from "../components/ReviewCard";

function Home() {
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState("python");
  const handleReview = async () => {
    try {
      const response = await api.post("/review", {
        language,
        code,
      });

      console.log(response.data);
    } catch (error) {
      console.error(error);
    }
  };
  return (
    <>
      <Navbar />

      <div
        style={{
          maxWidth: "1200px",
          margin: "40px auto",
          padding: "20px",
        }}
      >
        <LanguageSelector />

        <CodeEditor
          language={language}
          code={code}
          setCode={setCode}
        />

        <ReviewButton onClick={handleReview} />

        <ReviewCard />
      </div>
    </>
  );
}

export default Home;