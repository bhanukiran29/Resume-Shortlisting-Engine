import { zodResolver } from "@hookform/resolvers/zod";
import { Clipboard, Download, FileText, Plus, SlidersHorizontal } from "lucide-react";
import { useMemo } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import PageHeader from "../components/common/PageHeader";
import { Card } from "../components/ui/Card";

const schema = z.object({
  title: z.string().min(1),
  slots: z.coerce.number().min(1),
  minCgpa: z.coerce.number().min(0).max(10),
  experience: z.coerce.number().min(0),
});

const requiredSkills = ["React", "TypeScript", "GraphQL", "Tailwind CSS"];
const preferredSkills = ["Design Systems", "TanStack Table", "Recharts", "Framer Motion"];

export default function JobDescriptionPage() {
  const { register, watch, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
    defaultValues: { title: "Senior Frontend Engineer", slots: 5, minCgpa: 8, experience: 3 },
  });
  // eslint-disable-next-line react-hooks/incompatible-library
  const values = watch();
  const config = useMemo(() => ({
    job_id: "frontend-senior",
    title: values.title,
    slot_count: Number(values.slots),
    required_skills: requiredSkills,
    preferred_skills: preferredSkills,
    min_cgpa: Number(values.minCgpa),
    experience_years: Number(values.experience),
    weights: { skills: 85, practical: 50, education: 20 },
  }), [values]);

  return (
    <>
      <PageHeader
        description="Define the deterministic job profile and review the generated JSON before running a batch."
        title="Job Profile"
      />
      <div className="grid two">
        <Card title="Configuration Panel" icon={FileText}>
          <div className="grid two">
            <label>Role Title<input className="input" {...register("title")} /></label>
            <label>Slots<input className="input" type="number" {...register("slots")} /></label>
            <label>Minimum CGPA<input className="input" step="0.1" type="number" {...register("minCgpa")} /></label>
            <label>Experience<input className="input" type="number" {...register("experience")} /></label>
          </div>
          {Object.keys(errors).length ? <p className="page-copy" style={{ color: "var(--error)" }}>Please correct invalid fields.</p> : null}
          <div style={{ marginTop: 24 }}>
            <div className="settings-row"><strong>Required Skills</strong><button className="button ghost" type="button"><Plus size={16} /> Add</button></div>
            <div className="topbar__actions" style={{ flexWrap: "wrap", marginTop: 12 }}>{requiredSkills.map((skill) => <span className="badge medium" key={skill}>{skill}</span>)}</div>
          </div>
          <div style={{ marginTop: 24 }}>
            <div className="settings-row"><strong>Preferred Skills</strong><button className="button ghost" type="button"><Plus size={16} /> Add</button></div>
            <div className="topbar__actions" style={{ flexWrap: "wrap", marginTop: 12 }}>{preferredSkills.map((skill) => <span className="badge" key={skill}>{skill}</span>)}</div>
          </div>
          <Card title="Weight Sliders" icon={SlidersHorizontal} className="" >
            <p className="page-copy" style={{ marginTop: 0 }}>Weight editing is disabled because the current backend exposes no JD/settings update endpoint.</p>
            {[
              ["Skill Match", 85],
              ["Practical Signals", 50],
              ["Education / CGPA", 20],
            ].map(([label, value]) => (
              <label className="settings-row" key={label}>
                <span>{label}</span>
                <input aria-label={label} disabled max="100" min="0" type="range" value={value} readOnly />
              </label>
            ))}
          </Card>
        </Card>

        <Card title="Live JSON Preview" icon={Clipboard} action={<button className="icon-button" type="button"><Download size={16} /></button>}>
          <pre className="json-viewer">{JSON.stringify(config, null, 2)}</pre>
          <div className="topbar__actions" style={{ marginTop: 18 }}>
            <button className="button secondary" type="button">Reset</button>
            <button className="button primary" disabled title="Backend JD save endpoint is not available" type="button">Save Disabled</button>
          </div>
        </Card>
      </div>
    </>
  );
}
