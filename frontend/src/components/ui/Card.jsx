export function Card({ title, icon: Icon, action, children, className = "", glass = false }) {
  return (
    <section className={`card ${glass ? "glass" : ""} ${className}`}>
      {title ? (
        <div className="card__header">
          <h3 className="card-title">
            {Icon ? <Icon size={18} /> : null}
            {title}
          </h3>
          {action}
        </div>
      ) : null}
      <div className={title ? "card__body" : ""}>{children}</div>
    </section>
  );
}

export function StatCard({ label, value, delta, icon: Icon }) {
  return (
    <section className="card glass stat-card">
      <div style={{ display: "flex", justifyContent: "space-between", position: "relative", zIndex: 1 }}>
        <span className="label">{label}</span>
        {Icon ? <Icon color="var(--primary)" size={24} /> : null}
      </div>
      <div className="stat-value">{value}</div>
      {delta ? <div className="badge completed">{delta}</div> : null}
    </section>
  );
}
