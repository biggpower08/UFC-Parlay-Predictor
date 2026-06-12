"use client";

import { useEffect, useMemo, useState } from "react";

const DEFAULT_FIGHTERS = [
  { id: "blue", stance: "/sprites/crops/blue-stance.png", move: "/sprites/crops/blue-move.png", fight: "/sprites/crops/blue-fight.png" },
  { id: "purple", stance: "/sprites/crops/purple-stance.png", move: "/sprites/crops/purple-move.png", fight: "/sprites/crops/purple-fight.png" },
  { id: "orange", stance: "/sprites/crops/orange-stance.png", move: "/sprites/crops/orange-move.png", fight: "/sprites/crops/orange-fight.png" },
  { id: "green", stance: "/sprites/crops/green-stance.png", move: "/sprites/crops/green-move.png", fight: "/sprites/crops/green-fight.png" },
];

const SPARRING_STRIPS = [
  "/sprites/crops/sparring-blue-purple.png",
  "/sprites/crops/sparring-orange-green.png",
  "/sprites/crops/sparring-all.png",
];

const SEED_SEQUENCE = [7, 3, 2, 12, 5, 4, 17, 9, 14, 1, 11];
const PLACEMENTS = ["lower-left", "lower-right", "top-skim", "center-cross"];
const ACTIONS = ["jab-combo", "round-kick", "clinch-throw", "sweep-entry"];

function createSequence(fighters) {
  const offset = Math.floor(Math.random() * SEED_SEQUENCE.length);
  const seeded = SEED_SEQUENCE.map((value, index) => fighters[(value + offset + index) % fighters.length]);
  return seeded
    .map((fighter) => ({ fighter, sort: Math.random() }))
    .sort((a, b) => a.sort - b.sort)
    .map(({ fighter }) => fighter);
}

function createEncounter(fighters) {
  const sequence = createSequence(fighters);
  const attacker = sequence[0];
  const defender = sequence.find((fighter) => fighter.id !== attacker.id) || sequence[1] || fighters[1];
  return {
    attacker,
    defender,
    placement: PLACEMENTS[Math.floor(Math.random() * PLACEMENTS.length)],
    action: ACTIONS[Math.floor(Math.random() * ACTIONS.length)],
    strip: SPARRING_STRIPS[Math.floor(Math.random() * SPARRING_STRIPS.length)],
    durationMs: 900 + Math.floor(Math.random() * 850),
    delayMs: 2200 + Math.floor(Math.random() * 5200),
    flip: Math.random() > 0.5,
  };
}

export default function AmbientFighters({
  fighters = DEFAULT_FIGHTERS,
  enabled = true,
  intensity = "normal",
  placementMode = "random",
  reducedMotionMode = "hide",
}) {
  const [mounted, setMounted] = useState(false);
  const [encounter, setEncounter] = useState(null);
  const [cycle, setCycle] = useState(0);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted || !enabled || fighters.length < 2) return undefined;
    const next = createEncounter(fighters);
    setEncounter(next);
    const timer = window.setTimeout(() => setCycle((value) => value + 1), next.durationMs + next.delayMs);
    return () => window.clearTimeout(timer);
  }, [mounted, enabled, fighters, cycle]);

  const className = useMemo(() => {
    const placement = placementMode === "random" ? encounter?.placement : placementMode;
    return ["ambient-fighters", placement, encounter?.action, encounter?.flip ? "flip" : "", intensity]
      .filter(Boolean)
      .join(" ");
  }, [encounter, intensity, placementMode]);

  if (!mounted || !enabled || !encounter) return null;

  return (
    <div className={className} data-reduced-motion={reducedMotionMode} aria-hidden="true">
      <div className="ambient-action-stage">
        <img alt="" className="ambient-combatant ambient-attacker stance-frame" src={encounter.attacker.stance} />
        <img alt="" className="ambient-combatant ambient-attacker move-frame" src={encounter.attacker.move} />
        <img alt="" className="ambient-combatant ambient-attacker fight-frame" src={encounter.attacker.fight} />
        <img alt="" className="ambient-combatant ambient-defender stance-frame" src={encounter.defender.stance} />
        <img alt="" className="ambient-combatant ambient-defender fight-frame" src={encounter.defender.fight} />
        <img alt="" className="ambient-strip-action" src={encounter.strip} />
        <span className="ambient-impact" />
        <span className="ambient-slash" />
        <span className="ambient-dust ambient-dust-a" />
        <span className="ambient-dust ambient-dust-b" />
      </div>
    </div>
  );
}
