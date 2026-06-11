const PLANS = [
  {
    name: "Free",
    price: "$0",
    status: "Live",
    description: "Core matchup prediction tools for casual fight research.",
    features: [
      "3 free predictions",
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
    status: "Prepared",
    description: "Prediction-credit packs are planned for a later checkout launch.",
    features: [
      "5, 10, 15, or 20 prediction credits",
      "Full fight analysis",
      "Model-informed betting reads",
      "Advanced Elo trend cards",
      "Saved prediction history",
    ],
    cta: "Upgrade coming soon",
    disabled: true,
  },
  {
    name: "Pro",
    price: "Future",
    status: "Planned",
    description: "Expanded research workflow tools for deeper matchup analysis.",
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

const CREDIT_PACKS = [5, 10, 15, 20];

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
          <h1>Access options are being prepared.</h1>
          <p className="hero-copy">
            FightScope currently focuses on the free prediction experience. Paid prediction credits are planned, but checkout is not active yet.
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
          <p className="eyebrow">Prediction credits</p>
          <h2>Future credit packs</h2>
          <p className="helper-text">Each generated matchup is expected to use one prediction credit after the free allowance. Checkout will stay disabled until billing is ready.</p>
        </div>
        <div className="credit-pack-grid">
          {CREDIT_PACKS.map((count) => (
            <CreditPackCard key={count} count={count} />
          ))}
        </div>
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
        <PremiumFeatureCard title="Billing access" body="Billing will be introduced only after the credit flow is ready for users." />
        <PremiumFeatureCard title="Launch status" body="Checkout is intentionally disabled while the product experience is finalized." />
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

function CreditPackCard({ count }) {
  return (
    <article className="credit-pack-card">
      <span>{count} predictions</span>
      <h2>{count} credits</h2>
      <p>Use credits for future paid fight research and model-informed analysis.</p>
      <button type="button" disabled>Coming soon</button>
    </article>
  );
}
