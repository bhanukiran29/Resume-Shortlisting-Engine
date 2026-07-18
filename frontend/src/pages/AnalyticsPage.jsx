import { Award, BarChart3, Building2, FileBarChart, Gauge, PieChart as PieIcon } from "lucide-react";
import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis } from "recharts";
import PageHeader from "../components/common/PageHeader";
import { Card, StatCard } from "../components/ui/Card";
import { useAppData } from "../hooks/useAppData";

export default function AnalyticsPage() {
  const { analytics, candidates } = useAppData();
  const scoreDistribution = analytics.scoreDistribution;
  const topSkills = analytics.topSkills;
  const topColleges = analytics.topColleges;
  const hasScores = scoreDistribution.some((item) => item.count > 0);

  return (
    <>
      <PageHeader
        description="Executive-level analytics for score, confidence, skills, and source institutions."
        title="Batch Analytics"
      />
      <div className="grid stats" style={{ marginBottom: 24 }}>
        <StatCard icon={Gauge} label="Average Score" value={analytics.averageScore ?? "N/A"} delta="If backend supplies scores" />
        <StatCard icon={Award} label="Average Confidence" value={analytics.averageConfidence ?? "N/A"} delta="If backend supplies confidence" />
        <StatCard icon={FileBarChart} label="Parsed Files" value={String(candidates.length)} delta="Uploaded" />
        <StatCard icon={Building2} label="Top Colleges" value={String(topColleges.length)} delta="Extracted" />
      </div>
      <div className="grid two">
        <Card title="Score Distribution" icon={BarChart3}>
          <div className="chart-box">
            {hasScores ? <ResponsiveContainer>
              <BarChart data={scoreDistribution}>
                <CartesianGrid stroke="#27272a" vertical={false} />
                <XAxis axisLine={false} dataKey="range" tick={{ fill: "#c7c4d7" }} tickLine={false} />
                <YAxis axisLine={false} tick={{ fill: "#c7c4d7" }} tickLine={false} />
                <Tooltip contentStyle={{ background: "#18181b", border: "1px solid #333535" }} />
                <Bar dataKey="count" fill="#8083ff" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer> : <p className="page-copy">The current backend upload endpoint does not return scores, so score distribution is unavailable.</p>}
          </div>
        </Card>
        <Card title="CGPA vs. Assessment" icon={Gauge}>
          <div className="chart-box">
            {hasScores ? <ResponsiveContainer>
              <ScatterChart>
                <CartesianGrid stroke="#27272a" />
                <XAxis dataKey="cgpa" domain={[6, 10]} tick={{ fill: "#c7c4d7" }} type="number" />
                <YAxis dataKey="score" domain={[40, 100]} tick={{ fill: "#c7c4d7" }} type="number" />
                <Tooltip contentStyle={{ background: "#18181b", border: "1px solid #333535" }} />
                <Scatter data={candidates.filter((candidate) => typeof candidate.score === "number" && typeof candidate.cgpa === "number").map((candidate) => ({ cgpa: candidate.cgpa, score: candidate.score }))} fill="#8083ff" />
              </ScatterChart>
            </ResponsiveContainer> : <p className="page-copy">CGPA-to-score analysis requires backend responses that include both normalized CGPA and score.</p>}
          </div>
        </Card>
        <Card title="Skill Prevalence" icon={BarChart3}>
          {topSkills.length ? topSkills.map((item) => (
            <div className="settings-row" key={item.skill}>
              <span>{item.skill}</span>
              <div style={{ width: "55%" }}>
                <div className="progress-track">
                  <div className="progress-fill" style={{ width: `${item.count / 1.4}%` }} />
                </div>
              </div>
              <span className="mono">{item.count}</span>
            </div>
          )) : <p className="page-copy">No skills extracted yet. Upload resumes to compute prevalence.</p>}
        </Card>
        <Card title="Origin Institutions" icon={PieIcon}>
          <div className="chart-box" style={{ height: 230 }}>
            <ResponsiveContainer>
              <PieChart>
                <Pie data={topColleges} dataKey="count" nameKey="college" innerRadius={58} outerRadius={92} paddingAngle={3}>
                  {topColleges.map((item, index) => (
                    <Cell fill={["#8083ff", "#60a5fa", "#34d399", "#ffb783"][index]} key={item.college} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: "#18181b", border: "1px solid #333535" }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          {topColleges.length ? topColleges.map((item) => <div className="settings-row" key={item.college}><span>{item.college}</span><span className="mono">{item.count}</span></div>) : <p className="page-copy">No institution data returned by backend uploads yet.</p>}
        </Card>
      </div>
    </>
  );
}
