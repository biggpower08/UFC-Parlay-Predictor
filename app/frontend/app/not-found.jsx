export default function NotFound() {
  return (
    <main className="app-shell">
      <section className="panel empty-page">
        <p className="eyebrow">FightScope</p>
        <h1>Page not found</h1>
        <p>This route is not part of the current matchup workspace. Return home to start a new fight read.</p>
        <a className="analysis-link" href="/">Go to Home</a>
      </section>
    </main>
  );
}
