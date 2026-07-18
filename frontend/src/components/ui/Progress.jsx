export function Progress({ value }) {
  return (
    <div className="progress-track" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow={value}>
      <div className="progress-fill" style={{ width: `${value}%` }} />
    </div>
  );
}

export function SegmentedScore({ value }) {
  const filled = Math.round(value / 10);
  return (
    <div className="segmented-score" aria-label={`${value}% match`}>
      {Array.from({ length: 10 }, (_, index) => (
        <span className={`segment ${index < filled ? "filled" : ""}`} key={index} />
      ))}
    </div>
  );
}
