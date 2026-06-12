"use client";

import { useEffect, useMemo, useRef, useState } from "react";

const MANIFEST_URL = "/sprites/sprite-actions.json";
const PLACEMENTS = [
  { name: "bottom-left", x: 8, y: 78, scale: 0.88 },
  { name: "bottom-right", x: 74, y: 78, scale: 0.88 },
  { name: "left-mid", x: 4, y: 48, scale: 0.78 },
  { name: "right-mid", x: 78, y: 48, scale: 0.78 },
  { name: "upper-right", x: 70, y: 20, scale: 0.7 },
  { name: "lower-center", x: 42, y: 82, scale: 0.82 },
];
const INITIAL_DELAY_RANGE = [800, 3500];
const EVENT_DELAY_RANGE = [3500, 11000];
const LONG_PAUSE_RANGE = [12000, 18000];
const LONG_PAUSE_CHANCE = 0.12;

function weightedPick(items) {
  const total = items.reduce((sum, item) => sum + Math.max(1, item.weight || 1), 0);
  let target = Math.random() * total;
  for (const item of items) {
    target -= Math.max(1, item.weight || 1);
    if (target <= 0) return item;
  }
  return items[0];
}

function randomBetween([min, max]) {
  return min + Math.floor(Math.random() * (max - min + 1));
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function createEventDelay() {
  return Math.random() < LONG_PAUSE_CHANCE ? randomBetween(LONG_PAUSE_RANGE) : randomBetween(EVENT_DELAY_RANGE);
}

function pickPlacement(placementMode, recentPlacements) {
  const safePlacements = placementMode === "random"
    ? PLACEMENTS
    : PLACEMENTS.filter((placement) => placement.name === placementMode);
  const pool = safePlacements.length ? safePlacements : PLACEMENTS;
  const filtered = pool.filter((placement) => !recentPlacements.includes(placement.name));
  const placement = weightedPick((filtered.length ? filtered : pool).map((item) => ({ ...item, weight: 1 })));
  return {
    ...placement,
    x: clamp(placement.x + (Math.random() * 8 - 4), 2, 82),
    y: clamp(placement.y + (Math.random() * 8 - 4), 14, 84),
    scale: placement.scale * (0.92 + Math.random() * 0.16),
  };
}

function getMove(manifest, characterId, moveName) {
  return manifest?.characters?.[characterId]?.moves?.[moveName] || null;
}

function getMoveFrame(move, index) {
  if (!move?.frames?.length) return null;
  return move.frames[Math.min(index, move.frames.length - 1)];
}

function remember(list, value, max = 5) {
  return [value, ...list.filter((item) => item !== value)].slice(0, max);
}

function buildEncounter(manifest, placementMode, recentActions, recentPlacements) {
  const actions = (manifest?.actions || []).filter((action) => {
    if (action.enabled === false) return false;
    if (action.sequenceCharacter && action.sequenceMove) {
      return Boolean(getMove(manifest, action.sequenceCharacter, action.sequenceMove)?.frames?.length);
    }
    return Boolean(action.attackerMove && action.defenderMove);
  });
  if (!actions.length) return null;

  const actionPool = actions.filter((action) => !recentActions.includes(action.id));
  const action = weightedPick(actionPool.length ? actionPool : actions);
  const isSequence = Boolean(action.sequenceCharacter && action.sequenceMove);
  const sequenceMove = isSequence ? getMove(manifest, action.sequenceCharacter, action.sequenceMove) : null;
  const characterIds = Object.keys(manifest.characters || {}).filter((id) => id !== action.sequenceCharacter);
  const attackerId = characterIds[Math.floor(Math.random() * characterIds.length)];
  const defenderId = characterIds.find((id) => id !== attackerId) || characterIds[0];
  const attackerMove = getMove(manifest, attackerId, action.attackerMove);
  const defenderMove = getMove(manifest, defenderId, action.defenderMove);
  const frameCount = isSequence
    ? sequenceMove.frames.length
    : Math.max(attackerMove?.frames?.length || 0, defenderMove?.frames?.length || 0);

  return {
    id: `${action.id}-${Date.now()}-${Math.random().toString(36).slice(2)}`,
    action,
    attackerMove,
    defenderMove,
    sequenceMove,
    isSequence,
    frameCount,
    placement: pickPlacement(placementMode, recentPlacements),
    durationMs: action.totalDuration || 1120,
    flip: Math.random() > 0.5,
  };
}

export default function AmbientFighters({
  enabled = true,
  intensity = "normal",
  placementMode = "random",
  reducedMotionMode = "hide",
}) {
  const [mounted, setMounted] = useState(false);
  const [manifest, setManifest] = useState(null);
  const [encounter, setEncounter] = useState(null);
  const [frameIndex, setFrameIndex] = useState(0);
  const [canAnimate, setCanAnimate] = useState(false);
  const recentActions = useRef([]);
  const recentPlacements = useRef([]);

  useEffect(() => {
    setMounted(true);
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const narrowScreen = window.matchMedia("(max-width: 640px)").matches;
    setCanAnimate(!reducedMotion && !narrowScreen);
  }, []);

  useEffect(() => {
    if (!mounted || !enabled) return undefined;
    let cancelled = false;
    fetch(MANIFEST_URL, { cache: "force-cache" })
      .then((response) => (response.ok ? response.json() : null))
      .then((data) => {
        if (!cancelled && data?.characters && data?.actions) setManifest(data);
      })
      .catch(() => {
        if (!cancelled) setManifest(null);
      });
    return () => {
      cancelled = true;
    };
  }, [mounted, enabled]);

  useEffect(() => {
    if (!mounted || !enabled || !canAnimate || !manifest) return undefined;
    let cancelled = false;
    let showTimer;
    let hideTimer;

    const scheduleNext = (delayMs) => {
      showTimer = window.setTimeout(() => {
        if (cancelled) return;
        const next = buildEncounter(manifest, placementMode, recentActions.current, recentPlacements.current);
        if (!next) return;
        recentActions.current = remember(recentActions.current, next.action.id);
        recentPlacements.current = remember(recentPlacements.current, next.placement.name, 3);
        setEncounter(next);
        hideTimer = window.setTimeout(() => {
          if (cancelled) return;
          setEncounter(null);
          scheduleNext(createEventDelay());
        }, next.durationMs);
      }, delayMs);
    };

    scheduleNext(randomBetween(INITIAL_DELAY_RANGE));
    return () => {
      cancelled = true;
      window.clearTimeout(showTimer);
      window.clearTimeout(hideTimer);
    };
  }, [mounted, enabled, canAnimate, manifest, placementMode]);

  useEffect(() => {
    if (!encounter?.frameCount) return undefined;
    setFrameIndex(0);
    const timers = [];
    const durations = encounter.sequenceMove?.frameDurations || encounter.attackerMove?.frameDurations || [];
    let elapsed = 0;
    for (let index = 1; index < encounter.frameCount; index += 1) {
      elapsed += durations[index - 1] || Math.max(90, Math.floor(encounter.durationMs / encounter.frameCount));
      timers.push(window.setTimeout(() => setFrameIndex(index), elapsed));
    }
    return () => timers.forEach((timer) => window.clearTimeout(timer));
  }, [encounter]);

  const className = useMemo(
    () =>
      [
        "ambient-fighters",
        encounter?.isSequence ? "sequence-mode" : "paired-mode",
        encounter?.action?.category,
        encounter?.flip ? "flip" : "",
        intensity,
      ]
        .filter(Boolean)
        .join(" "),
    [encounter, intensity],
  );

  if (!mounted || !enabled || !canAnimate || !encounter) return null;

  const sequenceFrame = getMoveFrame(encounter.sequenceMove, frameIndex);
  const attackerFrame = getMoveFrame(encounter.attackerMove, frameIndex);
  const defenderFrame = getMoveFrame(encounter.defenderMove, frameIndex);

  return (
    <div
      className={className}
      data-reduced-motion={reducedMotionMode}
      style={{
        "--sprite-x": `${encounter.placement.x}vw`,
        "--sprite-y": `${encounter.placement.y}vh`,
        "--sprite-scale": encounter.placement.scale,
        "--sprite-duration": `${encounter.durationMs}ms`,
      }}
      aria-hidden="true"
    >
      <div className="ambient-action-stage">
        {encounter.isSequence && sequenceFrame ? (
          <img alt="" className="ambient-sequence-frame" src={sequenceFrame} />
        ) : (
          <>
            {attackerFrame ? <img alt="" className="ambient-combatant ambient-attacker" src={attackerFrame} /> : null}
            {defenderFrame ? <img alt="" className="ambient-combatant ambient-defender" src={defenderFrame} /> : null}
          </>
        )}
        <span className="ambient-impact" />
        <span className="ambient-motion-line" />
        <span className="ambient-dust ambient-dust-a" />
        <span className="ambient-dust ambient-dust-b" />
      </div>
    </div>
  );
}
