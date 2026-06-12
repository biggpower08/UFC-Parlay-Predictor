"use client";

import { useEffect, useMemo, useState } from "react";

const FIGHTERS = [
  { id: "blue", src: "/sprites/cyber-ninja-blue.png", alt: "" },
  { id: "purple", src: "/sprites/shadow-striker-purple.png", alt: "" },
  { id: "orange", src: "/sprites/cyber-monk-orange.png", alt: "" },
  { id: "green", src: "/sprites/neo-operative-green.png", alt: "" },
];

const SEED_SEQUENCE = [7, 3, 2, 12, 5, 4, 17, 9, 14, 1, 11];

function shuffledFighters(offset) {
  return SEED_SEQUENCE.map((value, index) => FIGHTERS[(value + offset + index) % FIGHTERS.length]);
}

export default function AmbientFighters() {
  const [offset, setOffset] = useState(0);

  useEffect(() => {
    setOffset(Math.floor(Math.random() * FIGHTERS.length));
  }, []);

  const sequence = useMemo(() => shuffledFighters(offset), [offset]);
  const duo = sequence.slice(0, 2);

  return (
    <div className="ambient-fighters" aria-hidden="true">
      <div className="ambient-lane ambient-lane-left">
        {sequence.slice(0, 4).map((fighter, index) => (
          <img
            alt={fighter.alt}
            className={`ambient-fighter ambient-fighter-${index + 1}`}
            key={`${fighter.id}-${index}`}
            src={fighter.src}
          />
        ))}
      </div>
      <div className="ambient-lane ambient-lane-right">
        {sequence.slice(4, 8).map((fighter, index) => (
          <img
            alt={fighter.alt}
            className={`ambient-fighter ambient-fighter-${index + 5}`}
            key={`${fighter.id}-side-${index}`}
            src={fighter.src}
          />
        ))}
      </div>
      <div className="ambient-sparring">
        <img alt="" className="ambient-duo ambient-duo-a" src={duo[0]?.src || FIGHTERS[0].src} />
        <img alt="" className="ambient-duo ambient-duo-b" src={duo[1]?.src || FIGHTERS[1].src} />
      </div>
      <img alt="" className="ambient-sparring-strip" src="/sprites/fighter-sparring-reference.png" />
    </div>
  );
}
