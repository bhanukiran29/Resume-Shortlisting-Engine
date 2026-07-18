export default function PageHeader({ kicker, title, description, actions }) {
  return (
    <header className="page-header">
      <div>
        {kicker ? <p className="page-kicker">{kicker}</p> : null}
        <h2 className="page-title">{title}</h2>
        {description ? <p className="page-copy">{description}</p> : null}
      </div>
      {actions ? <div className="topbar__actions">{actions}</div> : null}
    </header>
  );
}
