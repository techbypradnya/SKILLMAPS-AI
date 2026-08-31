"use client";

import { useMemo, useState } from "react";

export type SkillNode = {
  id: string;
  key: string;
  name: string;
  category?: string | null;
  confidence: number;
  status: string;
  evidence: { source: string; detail: string; points: number }[];
};

export type SkillEdge = { source: string; target: string; relation_type: string };

const STATUS_COLOR: Record<string, string> = {
  unknown: "#3A4256",
  beginner: "#E8735C",
  developing: "#E8A45C",
  proficient: "#4E9C82",
  strong: "#7CE0B8",
};

function statusFor(node: SkillNode) {
  return STATUS_COLOR[node.status] || STATUS_COLOR.unknown;
}

export default function SkillGraphViz({
  nodes,
  edges,
  onSelect,
}: {
  nodes: SkillNode[];
  edges: SkillEdge[];
  onSelect?: (node: SkillNode) => void;
}) {
  const [selectedKey, setSelectedKey] = useState<string | null>(null);

  const { positions, width, height } = useMemo(() => layout(nodes, edges), [nodes, edges]);

  const byKey = useMemo(() => Object.fromEntries(nodes.map((n) => [n.key, n])), [nodes]);

  return (
    <div className="card overflow-x-auto p-4">
      <svg viewBox={`0 0 ${width} ${height}`} width="100%" height={Math.min(height, 620)} role="img" aria-label="Skill prerequisite graph">
        <defs>
          <marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
            <path d="M0,0 L8,4 L0,8 Z" fill="#3A4256" />
          </marker>
        </defs>
        {edges.map((e, i) => {
          const s = positions[e.source];
          const t = positions[e.target];
          if (!s || !t) return null;
          const midX = (s.x + t.x) / 2;
          return (
            <path
              key={i}
              d={`M ${s.x} ${s.y} C ${midX} ${s.y}, ${midX} ${t.y}, ${t.x} ${t.y}`}
              fill="none"
              stroke="#3A4256"
              strokeWidth={1.5}
              markerEnd="url(#arrow)"
              opacity={0.55}
            />
          );
        })}
        {nodes.map((n) => {
          const p = positions[n.key];
          if (!p) return null;
          const isSelected = selectedKey === n.key;
          return (
            <g
              key={n.key}
              transform={`translate(${p.x}, ${p.y})`}
              className="cursor-pointer"
              onClick={() => {
                setSelectedKey(n.key);
                onSelect?.(n);
              }}
            >
              <circle
                r={isSelected ? 26 : 22}
                fill="#171E2E"
                stroke={statusFor(n)}
                strokeWidth={isSelected ? 3 : 2}
              />
              <circle r={4} cy={-2} fill={statusFor(n)} opacity={n.confidence / 100 + 0.15} />
              <text textAnchor="middle" y={38} fontSize="10.5" fill="#E7E9EE" className="select-none">
                {n.name.length > 16 ? n.name.slice(0, 15) + "…" : n.name}
              </text>
              <text textAnchor="middle" y={49} fontSize="9" fill="#8A93A6" className="select-none">
                {Math.round(n.confidence)}%
              </text>
            </g>
          );
        })}
      </svg>
      <div className="mt-3 flex flex-wrap gap-4 text-xs text-muted">
        {Object.entries({ Strong: "strong", Proficient: "proficient", Developing: "developing", Beginner: "beginner", Unknown: "unknown" }).map(
          ([label, key]) => (
            <span key={key} className="flex items-center gap-1.5">
              <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ backgroundColor: STATUS_COLOR[key] }} />
              {label}
            </span>
          )
        )}
      </div>
    </div>
  );
}

function layout(nodes: SkillNode[], edges: SkillEdge[]) {
  // depth(node) = 0 if it has no prerequisites (no outgoing REQUIRES edges),
  // else 1 + max(depth(prereq)) — foundational skills render on the left,
  // advanced skills on the right.
  const outgoing: Record<string, string[]> = {};
  edges.forEach((e) => {
    outgoing[e.source] = outgoing[e.source] || [];
    outgoing[e.source].push(e.target);
  });

  const depthCache: Record<string, number> = {};
  const nodeKeys = new Set(nodes.map((n) => n.key));

  function depthOf(key: string, seen: Set<string> = new Set()): number {
    if (depthCache[key] !== undefined) return depthCache[key];
    if (seen.has(key)) return 0; // guard against cycles
    seen.add(key);
    const targets = (outgoing[key] || []).filter((t) => nodeKeys.has(t));
    const d = targets.length === 0 ? 0 : 1 + Math.max(...targets.map((t) => depthOf(t, seen)));
    depthCache[key] = d;
    return d;
  }

  const columns: Record<number, string[]> = {};
  nodes.forEach((n) => {
    const d = depthOf(n.key);
    columns[d] = columns[d] || [];
    columns[d].push(n.key);
  });

  const colWidth = 150;
  const rowHeight = 90;
  const positions: Record<string, { x: number; y: number }> = {};
  const maxDepth = Math.max(0, ...Object.keys(columns).map(Number));
  const maxRows = Math.max(1, ...Object.values(columns).map((c) => c.length));

  Object.entries(columns).forEach(([depthStr, keys]) => {
    const depth = Number(depthStr);
    const x = 60 + depth * colWidth;
    const totalHeight = keys.length * rowHeight;
    const startY = Math.max(60, (maxRows * rowHeight - totalHeight) / 2 + 60);
    keys.forEach((key, i) => {
      positions[key] = { x, y: startY + i * rowHeight };
    });
  });

  return {
    positions,
    width: 60 + (maxDepth + 1) * colWidth + 60,
    height: Math.max(300, maxRows * rowHeight + 100),
  };
}
