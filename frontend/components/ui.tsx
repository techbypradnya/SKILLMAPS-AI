export function ConfidenceBar({ value }: { value: number }) {
  const color = value >= 80 ? "#7CE0B8" : value >= 60 ? "#4E9C82" : value >= 40 ? "#E8A45C" : value >= 20 ? "#E8735C" : "#3A4256";
  return (
    <div className="confidence-bar">
      <div className="confidence-bar-fill" style={{ width: `${Math.max(2, value)}%`, backgroundColor: color }} />
    </div>
  );
}

const STATUS_STYLES: Record<string, string> = {
  unknown: "bg-ink-softer text-muted",
  beginner: "bg-signal-coral/15 text-signal-coral",
  developing: "bg-signal-amber/15 text-signal-amber",
  proficient: "bg-capability-dim/20 text-capability-dim",
  strong: "bg-capability/20 text-capability",
};

const STATUS_LABELS: Record<string, string> = {
  unknown: "Unknown",
  beginner: "Beginner",
  developing: "Developing",
  proficient: "Proficient",
  strong: "Strong",
};

export function StatusPill({ status }: { status: string }) {
  return (
    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_STYLES[status] || STATUS_STYLES.unknown}`}>
      {STATUS_LABELS[status] || status}
    </span>
  );
}

export function EmptyState({ title, body, action }: { title: string; body: string; action?: React.ReactNode }) {
  return (
    <div className="card flex flex-col items-start gap-3 p-8">
      <p className="font-display text-xl text-ivory">{title}</p>
      <p className="max-w-md text-sm text-muted">{body}</p>
      {action}
    </div>
  );
}

export function Spinner() {
  return (
    <div className="flex items-center gap-2 text-sm text-muted">
      <span className="h-3 w-3 animate-pulse rounded-full bg-capability" />
      Loading…
    </div>
  );
}
