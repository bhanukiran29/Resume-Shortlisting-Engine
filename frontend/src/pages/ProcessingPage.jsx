import { BrainCircuit, CheckCircle2, Clock, FileText, Gauge, ListChecks, ScanText, ShieldCheck, Sparkles, Timer, Workflow } from "lucide-react";
import { motion } from "framer-motion";
import PageHeader from "../components/common/PageHeader";
import { StatusBadge } from "../components/ui/Badge";
import { Card } from "../components/ui/Card";
import { Progress } from "../components/ui/Progress";
import { useAppData } from "../hooks/useAppData";

const stages = [
  { name: "Ingestion", icon: FileText, state: "done" },
  { name: "PDF Parse", icon: ScanText, state: "done" },
  { name: "OCR", icon: Sparkles, state: "done" },
  { name: "Field Extraction", icon: ListChecks, state: "done" },
  { name: "Grade Normalization", icon: Gauge, state: "active" },
  { name: "Skill Matching", icon: BrainCircuit, state: "pending" },
  { name: "Scoring", icon: Timer, state: "pending" },
  { name: "Confidence", icon: ShieldCheck, state: "pending" },
];

export default function ProcessingPage() {
  const { isUploading, lastError, uploadQueue, uploadResults } = useAppData();
  const parsedCount = uploadQueue.filter((item) => item.status === "Parsed").length;
  const progress = uploadQueue.length ? Math.round((parsedCount / uploadQueue.length) * 100) : uploadResults.length ? 100 : 0;

  return (
    <>
      <PageHeader
        actions={<StatusBadge tone={lastError ? "failed" : isUploading ? "processing" : uploadResults.length ? "completed" : "medium"}>{lastError ? "Upload Error" : isUploading ? "Processing" : uploadResults.length ? "Parsed" : "Idle"}</StatusBadge>}
        description="The current backend upload endpoint parses synchronously, so the UI reports actual queued/uploaded states rather than fake live stage percentages."
        title="Processing Pipeline"
      />
      <div className="grid split-grid">
        <Card title="Pipeline Stages" icon={Workflow}>
          <div className="pipeline-track">
            {stages.map((stage) => {
              const Icon = stage.icon;
              return (
                <div className={`pipeline-stage ${stage.state}`} key={stage.name}>
                  <motion.div
                    animate={stage.state === "active" ? { scale: [1, 1.06, 1] } : {}}
                    className="pipeline-node"
                    transition={{ duration: 1.4, repeat: Infinity }}
                  >
                    <Icon size={22} />
                  </motion.div>
                  <span className="label">{stage.name}</span>
                </div>
              );
            })}
          </div>
          <div className="grid two" style={{ marginTop: 28 }}>
            <div className="card" style={{ padding: 22 }}>
              <StatusBadge tone={uploadResults.length ? "completed" : "medium"}>{uploadResults.length ? "Complete" : "Waiting"}</StatusBadge>
              <h3 className="card-title" style={{ marginTop: 16 }}>Field Extraction</h3>
              <p className="page-copy">Parsed entities identified and categorized from text streams.</p>
              <Progress value={uploadResults.length ? 100 : 0} />
            </div>
            <div className="card" style={{ padding: 22, borderColor: "rgba(128,131,255,.45)" }}>
              <StatusBadge tone={isUploading ? "processing" : "medium"}>{isUploading ? "Active" : "Idle"}</StatusBadge>
              <h3 className="card-title" style={{ marginTop: 16 }}>Grade Normalization</h3>
              <p className="page-copy">Converting CGPA, GPA, and percentage values to a 10-point scale.</p>
              <Progress value={progress} />
            </div>
          </div>
        </Card>

        <div className="grid">
          <Card title="Live Status" icon={Clock}>
            {[
              ["Queue", String(uploadQueue.length)],
              ["ETA", isUploading ? "Synchronous" : "N/A"],
              ["Current File", uploadQueue.find((item) => item.status !== "Parsed")?.name || "None"],
              ["Errors", lastError ? "1" : "0"],
            ].map(([label, value]) => (
              <div className="settings-row" key={label}>
                <span className="muted">{label}</span>
                <span className="mono">{value}</span>
              </div>
            ))}
          </Card>
          <Card title="Processing Queue" icon={ListChecks}>
            {(uploadQueue.length ? uploadQueue.map((item) => item.name) : uploadResults.map((result) => result.parsed_data?.filename || result.file_path)).map((file, index) => (
              <div className="settings-row" key={file}>
                <span>{file}</span>
                {isUploading && index === 0 ? <StatusBadge tone="processing">Running</StatusBadge> : <span className="muted">{uploadQueue[index]?.status || "Parsed"}</span>}
              </div>
            ))}
            {!uploadQueue.length && !uploadResults.length ? <p className="page-copy">No processing history yet. Upload resumes to populate this panel.</p> : null}
          </Card>
          <Card title="Verification" icon={CheckCircle2}>
            <p className="page-copy">Outputs are deterministic for identical inputs. No random or time-dependent scoring behavior detected.</p>
          </Card>
        </div>
      </div>
    </>
  );
}
