"use client";

import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/", label: "Home" },
  { href: "/analysis", label: "Analysis" },
  { href: "/stats", label: "Stats" },
  { href: "/odds", label: "Odds" },
];

export default function SiteNav() {
  const pathname = usePathname() || "/";

  return (
    <nav className="site-nav" aria-label="Primary">
      {LINKS.map((link) => {
        const active = link.href === "/" ? pathname === "/" : pathname.startsWith(link.href);
        return (
          <a className={active ? "active" : ""} href={link.href} key={link.href}>
            {link.label}
          </a>
        );
      })}
    </nav>
  );
}
