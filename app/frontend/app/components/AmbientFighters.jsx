"use client";

import { useEffect, useMemo, useState } from "react";

const MANIFEST_URL = "/sprites/sprite-actions.json";
const PLACEMENTS = ["lower-left", "lower-right", "top-skim", "center-cross"];
const FALLBACK_DELAY_MS = 4200;

function weightedPick(items) {
  const total = items.reduce((sum, item) => sum + Math.max(1, item.weight || 1), 0);
  let target = Math.random() * total;
  for (const item of items) {
    target -= Math.max(1, item.weight || 1);
    if (target <= 0) return item;
  }
  return items[0];
}

function pickPlacement(action, placementMode) {
  if (placementMode !== "random") return placementMode;
  const choices = action.recommendedPlacement?.length ? action.recommendedPlacement : PLACEMENTS;
  return choices[Math.floor(Math.random() * choices.length)] || "lower-left";
}

function getMove(manifest, characterId, moveName) {
  return manifest?.characters?.[characterId]?.moves?.[moveName] || null;
}

function getMoveFrame(move, index) {
  if (!move?.frames?.length) return null;
  return move.frames[Math.min(index, move.frames.length - 1)];
}

function buildEncounter(manifest, placementMode) {
  const actions = (manifest?.actions || []).filter((action) => {
    if (action.sequenceCharacter && action.sequenceMove) {
      return Boolean(getMove(manifest, action.sequenceCharacter, action.sequenceMove)?.frames?.length);
    }
    return Boolean(action.attackerMove && action.defenderMove);
  });
  if (!actions.length) return null;

  const action = weightedPick(actions);
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
    placement: pickPlacement(action, placementMode),
    durationMs: action.totalDuration || 1120,
    delayMs: FALLBACK_DELAY_MS + Math.floor(Math.random() * 3600),
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
  const [cycle, setCycle] = useState(0);
  const [frameIndex, setFrameIndex] = useState(0);

  useEffect(() => {
    setMounted(true);
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
    if (!mounted || !enabled || !manifest) return undefined;
    const next = buildEncounter(manifest, placementMode);
    if (!next) return undefined;
    setEncounter(next);
    const timer = window.setTimeout(() => setCycle((value) => value + 1), next.durationMs + next.delayMs);
    return () => window.clearTimeout(timer);
  }, [mounted, enabled, manifest, placementMode, cycle]);

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
        encounter?.placement,
        encounter?.isSequence ? "sequence-mode" : "paired-mode",
        encounter?.action?.category,
        encounter?.flip ? "flip" : "",
        intensity,
      ]
        .filter(Boolean)
        .join(" "),
    [encounter, intensity],
  );

  if (!mounted || !enabled || !encounter) return null;

  const sequenceFrame = getMoveFrame(encounter.sequenceMove, frameIndex);
  const attackerFrame = getMoveFrame(encounter.attackerMove, frameIndex);
  const defenderFrame = getMoveFrame(encounter.defenderMove, frameIndex);

  return (
    <div className={className} data-reduced-motion={reducedMotionMode} aria-hidden="true">
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
