import "./globals.css";

export const metadata = {
  title: "UFC Predictor",
  description: "Installable UFC prediction app",
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    title: "UFC Predictor",
    statusBarStyle: "black-translucent",
  },
};

export const viewport = {
  themeColor: "#071019",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <nav className="site-nav" aria-label="Primary">
          <a href="/">Prediction</a>
          <a href="/analysis">Analysis</a>
          <a href="/stats">Stats</a>
          <a href="/odds">Betting Odds</a>
        </nav>
        {children}
      </body>
    </html>
  );
}
