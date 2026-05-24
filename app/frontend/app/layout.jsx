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
      <body>{children}</body>
    </html>
  );
}
