import "./globals.css";
import SiteNav from "./components/SiteNav";

export const metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || "https://mma-ai.onrender.com"),
  title: {
    default: "UFC MMA AI Predictor",
    template: "%s | UFC MMA AI Predictor",
  },
  description:
    "Compare UFC and MMA fighters with AI-powered predictions, confidence scores, Elo ratings, matchup stats, fight analysis, and model-informed prop reads.",
  manifest: "/manifest.json",
  openGraph: {
    title: "UFC MMA AI Predictor",
    description:
      "AI-powered UFC and MMA matchup analysis with winner predictions, confidence scores, fighter stats, Elo ratings, and model-informed betting reads.",
    type: "website",
    url: "/",
  },
  twitter: {
    card: "summary",
    title: "UFC MMA AI Predictor",
    description:
      "Compare UFC and MMA fighters with AI-powered predictions, confidence scores, Elo ratings, matchup stats, fight analysis, and model-informed prop reads.",
  },
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
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "WebApplication",
              name: "UFC MMA AI Predictor",
              applicationCategory: "SportsApplication",
              description:
                "AI-powered UFC and MMA matchup analysis with winner predictions, confidence scores, fighter stats, Elo ratings, and model-informed betting reads.",
              offers: {
                "@type": "Offer",
                price: "0",
                priceCurrency: "USD",
              },
            }),
          }}
        />
        <SiteNav />
        {children}
      </body>
    </html>
  );
}
