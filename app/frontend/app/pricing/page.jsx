const PLANS = [
  {
    name: "Free",
    price: "$0",
    status: "Live",
    description: "Core matchup prediction tools for casual fight research.",
    features: [
      "Winner prediction",
      "Confidence meter",
      "Compact analyst summary",
      "Basic matchup stats",
      "Model status visibility",
    ],
    cta: "Current access",
    disabled: true,
  },
  {
    name: "Premium",
    price: "Coming soon",
    status: "Stripe-ready",
    description: "Deeper fight intelligence once subscriptions launch.",
    features: [
      "Saved predictions",
      "Advanced Elo trends",
      "Full betting-read dashboard",
      "Premium prop-style reads",
      "Shareable matchup reports",
    ],
    cta: "Upgrade coming soon",
    disabled: true,
  },
  {
    name: "Pro",
    price: "Future",
    status: "Planned",
    description: "Research workflow tools for heavier analysis use.",
    features: [
      "Historical model performance",
      "Line movement research",
      "Exportable reports",
      "Expanded model diagnostics",
      "Higher usage limits",
    ],
    cta: "Pro coming soon",
    disabled: true,
  },
];

const COMPARISON_ROWS = [
  ["Winner predictions", "Included", "Included", "Included"],
  ["Full analysis page", "Limited", "Included", "Included"],
  ["Elo trend history", "Basic", "Advanced", "Advanced"],
  ["Prop-style reads", "Model-informed", "Premium reads", "Expanded reads"],
  ["Saved predictions", "Not included", "Included", "Included"],
  ["Billing", "Not required", "Coming soon", "Coming soon"],
];

export default function PricingPage() {
  return (
    <main className="app-shell">
      <header className="topbar pricing-hero">
        <div>
          <p className="eyebrow">Pricing</p>
          <h1>Free now. Premium tools coming soon.</h1>
          <p className="hero-copy">
            The app is being prepared for subscriptions, but real Stripe checkout is not active yet. Upgrade buttons are disabled until billing launches.
          </p>
        </div>
      </header>

      <section className="pricing-grid">
        {PLANS.map((plan) => (
          <article className="pricing-card" key={plan.name}>
            <div className="pricing-card-top">
              <span>{plan.status}</span>
              <h2>{plan.name}</h2>
              <strong>{plan.price}</strong>
              <p>{plan.description}</p>
            </div>
            <ul>
              {plan.features.map((feature) => (
                <li key={feature}>{feature}</li>
              ))}
            </ul>
            <button type="button" disabled={plan.disabled}>
              {plan.cta}
            </button>
          </article>
        ))}
      </section>

      <section className="panel comparison-panel">
        <div>
          <p className="eyebrow">Plan comparison</p>
          <h2>Prepared for a future paywall</h2>
        </div>
        <div className="comparison-table">
          <div className="comparison-heading">
            <b>Feature</b>
            <b>Free</b>
            <b>Premium</b>
            <b>Pro</b>
          </div>
          {COMPARISON_ROWS.map(([feature, free, premium, pro]) => (
            <div className="comparison-row" key={feature}>
              <span>{feature}</span>
              <span>{free}</span>
              <span>{premium}</span>
              <span>{pro}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="premium-placeholder-grid">
        <PremiumFeatureCard title="Billing placeholder" body="Billing will be available after subscriptions launch." />
        <PremiumFeatureCard title="Stripe status" body="Stripe environment variables are documented only and are not required for startup." />
        <PremiumFeatureCard title="Responsible rollout" body="Premium betting reads will stay model-informed and will not show fake sportsbook lines." />
      </section>
    </main>
  );
}

function PremiumFeatureCard({ title, body }) {
  return (
    <article className="premium-feature-card">
      <span>Coming soon</span>
      <h2>{title}</h2>
      <p>{body}</p>
    </article>
  );
}
