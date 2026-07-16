import { useState } from "react";
import Navbar from "../components/Navbar";
import LanguageSelector from "../components/LanguageSelector";
import CodeEditor from "../components/CodeEditor";
import ReviewButton from "../components/ReviewButton";
import ReviewCard from "../components/ReviewCard";

function Home() {
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState("python");
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

        <ReviewButton />

        <ReviewCard />
      </div>
    </>
  );
}

export default Home;