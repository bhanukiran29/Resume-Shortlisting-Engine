import { ArrowRight, Download, FileText, Gauge, Star, UploadCloud, Users, Workflow } from "lucide-react";
import { Bar, BarChart, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis } from "recharts";
import PageHeader from "../components/common/PageHeader";
import { ConfidenceBadge, StatusBadge } from "../components/ui/Badge";
import { Card, StatCard } from "../components/ui/Card";
import { useAppData } from "../hooks/useAppData";

const statIcons = [FileText, Workflow, Users, Star];

export default function DashboardPage() {
  const { analytics, candidates, dashboard } = useAppData();
  const stats = [
    { label: "Total Resumes", value: String(dashboard.total), delta: dashboard.total ? "Uploaded" : "Empty" },
    { label: "Processed", value: String(dashboard.processed), delta: dashboard.pipelineHealth },
    { label: "High Confidence", value: String(dashboard.highConfidence), delta: "Backend result" },
    { label: "Top Score", value: dashboard.topScore ?? "N/A", delta: "If supplied" },
  ];
  const scoreDistribution = analytics.scoreDistribution;
  const confidenceDistribution = analytics.confidenceDistribution.length
    ? analytics.confidenceDistribution
    : [{ name: "Unavailable", value: candidates.length }];

  return (
    <>
      <PageHeader
        actions={<StatusBadge tone="completed">Engine Online</StatusBadge>}
        description="Real-time processing metrics and deterministic pipeline health."
        title="Engine Overview"
      />

      <div className="grid stats" style={{ marginBottom: 24 }}>
        {stats.map((stat, index) => (
          <StatCard icon={statIcons[index]} key={stat.label} {...stat} />
        ))}
      </div>

      <div className="grid dashboard">
        <Card className="span-2" glass title="Pipeline Health">
          <div className="pipeline-track" style={{ gridTemplateColumns: "repeat(4, minmax(100px, 1fr))" }}>
            {["Ingestion", "Parsing", "Scoring", "Export"].map((stage, index) => (
              <div className={`pipeline-stage ${index < 3 ? "done" : ""}`} key={stage}>
                <div className="pipeline-node">
                  <Gauge size={20} />
                </div>
                <span className="label">{stage}</span>
              </div>
            ))}
          </div>
          <div className="card" style={{ marginTop: 18, padding: 14, textAlign: "center" }}>
            <span className="muted">{dashboard.pipelineHealth}. Live progress is not exposed by the current backend.</span>
          </div>
        </Card>

        <Card glass title="Quick Actions">
          <div className="grid" style={{ gap: 12 }}>
            {[
              [UploadCloud, "Upload Resumes", "Start new batch"],
              [Gauge, "Configure JD", "Update criteria"],
              [Download, "Export Report", "Download CSV"],
            ].map(([Icon, title, text]) => (
              <button className="nav-item" key={title} type="button">
                <Icon size={20} />
                <span>
                  <strong>{title}</strong>
                  <br />
                  <span className="muted">{text}</span>
                </span>
              </button>
            ))}
          </div>
        </Card>

        <Card glass title="Score Distribution">
          <div className="chart-box">
            {scoreDistribution.some((item) => item.count > 0) ? <ResponsiveContainer>
              <BarChart data={scoreDistribution}>
                <XAxis axisLine={false} dataKey="range" tick={{ fill: "#c7c4d7", fontSize: 12 }} tickLine={false} />
                <Tooltip cursor={{ fill: "rgba(128,131,255,.08)" }} contentStyle={{ background: "#18181b", border: "1px solid #333535" }} />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {scoreDistribution.map((entry, index) => (
                    <Cell fill={index === 3 ? "#8083ff" : `rgba(128,131,255,${0.25 + index * 0.12})`} key={entry.range} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer> : <p className="page-copy">Scores are unavailable because the current backend upload response does not include scored candidate reports.</p>}
          </div>
        </Card>

        <Card className="span-3" glass title="Recent Uploads" action={<button className="button ghost" type="button">View All <ArrowRight size={16} /></button>}>
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Batch ID</th>
                  <th>Role Target</th>
                  <th>Count</th>
                  <th>Date</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {dashboard.recentUploads.length ? dashboard.recentUploads.map((upload, index) => (
                  <tr key={upload.id}>
                    <td className="mono">#{index + 1}</td>
                    <td>{upload.fileName}</td>
                    <td className="mono">{upload.skills.length}</td>
                    <td className="muted">Current session</td>
                    <td>
                      <StatusBadge tone="completed">Parsed</StatusBadge>
                    </td>
                  </tr>
                )) : (
                  <tr>
                    <td colSpan="5">No backend uploads yet. Upload resumes to populate dashboard metrics.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </Card>

        <Card glass title="Confidence Overview">
          <div className="chart-box" style={{ height: 220 }}>
            <ResponsiveContainer>
              <PieChart>
                <Pie data={confidenceDistribution} dataKey="value" innerRadius={54} outerRadius={84} paddingAngle={4}>
                  <Cell fill="#8083ff" />
                  <Cell fill="#64748b" />
                  <Cell fill="#fb7185" />
                </Pie>
                <Tooltip contentStyle={{ background: "#18181b", border: "1px solid #333535" }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid" style={{ gap: 8 }}>
            {confidenceDistribution.map((item) => (
              <div className="settings-row" key={item.name}>
                <ConfidenceBadge value={item.name === "Unavailable" ? "Low" : item.name} />
                <span className="mono">{item.value}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </>
  );
}
