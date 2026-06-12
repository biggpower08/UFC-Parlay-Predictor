"use client";

import { useEffect, useMemo, useState } from "react";

const FIGHTERS = [
  { id: "blue", idle: "/sprites/crops/blue-idle.png", move: "/sprites/crops/blue-move.png", fight: "/sprites/crops/blue-fight.png" },
  { id: "purple", idle: "/sprites/crops/purple-idle.png", move: "/sprites/crops/purple-move.png", fight: "/sprites/crops/purple-fight.png" },
  { id: "orange", idle: "/sprites/crops/orange-idle.png", move: "/sprites/crops/orange-move.png", fight: "/sprites/crops/orange-fight.png" },
  { id: "green", idle: "/sprites/crops/green-idle.png", move: "/sprites/crops/green-move.png", fight: "/sprites/crops/green-fight.png" },
];

const SPARRING_STRIPS = [
  "/sprites/crops/sparring-blue-purple.png",
  "/sprites/crops/sparring-orange-green.png",
  "/sprites/crops/sparring-all.png",
];

const SEED_SEQUENCE = [7, 3, 2, 12, 5, 4, 17, 9, 14, 1, 11];

function buildRuntimeSequence() {
  const offset = Math.floor(Math.random() * SEED_SEQUENCE.length);
  const pool = SEED_SEQUENCE.map((value, index) => FIGHTERS[(value + offset + index) % FIGHTERS.length]);
  return pool
    .map((fighter) => ({ fighter, sort: Math.random() }))
    .sort((a, b) => a.sort - b.sort)
    .map(({ fighter }) => fighter);
}

export default function AmbientFighters() {
  const [sequence, setSequence] = useState([]);
  const [sparringStrip, setSparringStrip] = useState("");

  useEffect(() => {
    setSequence(buildRuntimeSequence());
    setSparringStrip(SPARRING_STRIPS[Math.floor(Math.random() * SPARRING_STRIPS.length)]);
  }, []);

  const fighters = useMemo(() => (sequence.length ? sequence : []), [sequence]);
  if (!fighters.length) return null;

  const duo = fighters.slice(0, 2);

  return (
    <div className="ambient-fighters" aria-hidden="true">
      <div className="ambient-lane ambient-lane-left">
        {fighters.slice(0, 4).map((fighter, index) => (
          <img
            alt=""
            className={`ambient-fighter ambient-fighter-${index + 1}`}
            key={`${fighter.id}-${index}`}
            src={index % 2 === 0 ? fighter.idle : fighter.move}
          />
        ))}
      </div>
      <div className="ambient-lane ambient-lane-right">
        {fighters.slice(4, 8).map((fighter, index) => (
          <img
            alt=""
            className={`ambient-fighter ambient-fighter-${index + 5}`}
            key={`${fighter.id}-side-${index}`}
            src={index % 2 === 0 ? fighter.move : fighter.fight}
          />
        ))}
      </div>
      <div className="ambient-sparring">
        <img alt="" className="ambient-duo ambient-duo-a" src={duo[0]?.fight || FIGHTERS[0].fight} />
        <img alt="" className="ambient-duo ambient-duo-b" src={duo[1]?.fight || FIGHTERS[1].fight} />
      </div>
      <img alt="" className="ambient-sparring-strip" src={sparringStrip} />
    </div>
  );
}
