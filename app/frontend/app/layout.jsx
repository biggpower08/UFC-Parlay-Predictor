import "./globals.css";
import SiteNav from "./components/SiteNav";

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
        <SiteNav />
        {children}
      </body>
    </html>
  );
}
