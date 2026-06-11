import "./globals.css";
import SiteNav from "./components/SiteNav";

export const metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || "https://mma-ai.onrender.com"),
  title: {
    default: "FightScope",
    template: "%s | FightScope",
  },
  description:
    "Compare UFC and MMA fighters with prediction signals, confidence scores, Elo ratings, matchup stats, fight analysis, and model-informed prop reads.",
  manifest: "/manifest.json",
  openGraph: {
    title: "FightScope",
    description:
      "UFC and MMA matchup analysis with winner predictions, confidence scores, fighter stats, Elo ratings, and model-informed betting reads.",
    type: "website",
    url: "/",
  },
  twitter: {
    card: "summary",
    title: "FightScope",
    description:
      "Compare UFC and MMA fighters with prediction signals, confidence scores, Elo ratings, matchup stats, fight analysis, and model-informed prop reads.",
  },
  appleWebApp: {
    capable: true,
    title: "FightScope",
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
              name: "FightScope",
              applicationCategory: "SportsApplication",
              description:
                "UFC and MMA matchup analysis with winner predictions, confidence scores, fighter stats, Elo ratings, and model-informed betting reads.",
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
