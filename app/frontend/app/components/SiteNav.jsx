"use client";

import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/", label: "Home" },
  { href: "/models", label: "Models" },
  { href: "/analysis", label: "Analysis" },
  { href: "/stats", label: "Stats" },
  { href: "/odds", label: "Odds" },
];

export default function SiteNav() {
  const pathname = usePathname() || "/";

  return (
    <nav className="site-nav" aria-label="Primary">
      <a className="brand-link" href="/" aria-label="FightScope home">
        <strong>FightScope</strong>
      </a>
      <div className="site-nav-links">
        {LINKS.map((link) => {
          const active = link.href === "/" ? pathname === "/" : pathname.startsWith(link.href);
          return (
            <a className={active ? "active" : ""} href={link.href} key={link.href}>
              {link.label}
            </a>
          );
        })}
      </div>
    </nav>
  );
}
