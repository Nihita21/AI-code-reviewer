import Navbar from "../components/Navbar";
import LanguageSelector from "../components/LanguageSelector";
import CodeEditor from "../components/CodeEditor";

function Home() {
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

        <CodeEditor />
      </div>
    </>
  );
}

export default Home;