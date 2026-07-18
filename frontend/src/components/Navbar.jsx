import "./Navbar.css";

function Navbar() {
  return (
    <nav className="navbar">

      <div className="logo">

        <div className="logoIcon">
          {"</>"}
        </div>

        <div>

          <div className="logoTitle">
            AI Code Reviewer
          </div>

          <div className="logoSubtitle">
            Analyze • Improve • Learn
          </div>

        </div>

      </div>

      <div className="version">
        v0.1
      </div>

    </nav>
  );
}

export default Navbar;