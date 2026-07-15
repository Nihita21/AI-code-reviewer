import Navbar from "../components/Navbar";

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
        <h2>Welcome to AI Code Reviewer 🚀</h2>
        <p>Let's start building!</p>
      </div>
    </>
  );
}

export default Home;