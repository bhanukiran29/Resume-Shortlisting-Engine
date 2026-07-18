export function StatusBadge({ children, tone = "medium" }) {
  return <span className={`badge ${tone}`}>{children}</span>;
}

export function ConfidenceBadge({ value }) {
  const tone = value === "High" ? "high" : value === "Medium" ? "medium" : "low";
  return <span className={`badge ${tone}`}>{value}</span>;
}

export function ScoreBadge({ score }) {
  const color = score >= 80 ? "#818cf8" : score >= 60 ? "#60a5fa" : "#a1a1aa";
  return (
    <span className="score-pill" style={{ "--score-deg": `${Math.round(score * 3.6)}deg`, "--score-color": color }}>
      <span>{score}</span>
    </span>
  );
}
