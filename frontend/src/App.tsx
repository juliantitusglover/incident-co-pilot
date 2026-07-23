import "./App.css";

function App() {
  return (
    <main className="app-shell">
      <section className="intro" aria-labelledby="app-title">
        <p className="eyebrow">Minimal web UI scaffold</p>
        <h1 id="app-title">Incident Co-Pilot</h1>
        <p className="summary">
          Backend API expected at <code>http://localhost:8000</code>.
        </p>
        <p className="next-step">
          Incident list, create, detail, timeline, and report screens will be
          added in later M12 PRs.
        </p>
      </section>
    </main>
  );
}

export default App;
