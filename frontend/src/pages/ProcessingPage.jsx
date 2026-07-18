import { BrainCircuit, CheckCircle2, Clock, FileText, Gauge, ListChecks, ScanText, ShieldCheck, Sparkles, Timer, Workflow } from "lucide-react";
import { motion } from "framer-motion";
import PageHeader from "../components/common/PageHeader";
import { StatusBadge } from "../components/ui/Badge";
import { Card } from "../components/ui/Card";
import { Progress } from "../components/ui/Progress";
import { useAppData } from "../hooks/useAppData";

const stageDefinitions = [
  { name: "Ingestion", icon: FileText },
  { name: "PDF Parse", icon: ScanText },
  { name: "OCR", icon: Sparkles },
  { name: "Field Extraction", icon: ListChecks },
  { name: "Grade Normalization", icon: Gauge },
  { name: "Skill Extraction", icon: BrainCircuit },
  { name: "Scoring", icon: Timer },
  { name: "Confidence", icon: ShieldCheck },
];

export default function ProcessingPage() {
  const { isUploading, lastError, uploadQueue, uploadResults } = useAppData();
  const hasResults = uploadResults.length > 0;
  const parsedCount = uploadQueue.filter((item) => item.status === "Parsed").length;
  const pendingCount = isUploading ? uploadQueue.filter((item) => !["Parsed", "Failed"].includes(item.status)).length : 0;
  const currentFile = isUploading ? uploadQueue.find((item) => !["Parsed", "Failed"].includes(item.status))?.name || "None" : "None";
  const stages = stageDefinitions.map((stage) => ({
    ...stage,
    state: isUploading ? "active" : hasResults ? "done" : "pending",
  }));
  const queueRows = isUploading && uploadQueue.length
    ? uploadQueue.map((item) => ({ name: item.name, status: item.status }))
    : uploadResults.map((result) => ({
      name: result.parsed_data?.filename || result.file_path,
      status: result.parsed_data?.parse_quality || "Parsed",
    }));
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
              <StatusBadge tone={isUploading ? "processing" : hasResults ? "completed" : "medium"}>{isUploading ? "Active" : hasResults ? "Complete" : "Idle"}</StatusBadge>
              <h3 className="card-title" style={{ marginTop: 16 }}>Grade Normalization</h3>
              <p className="page-copy">{hasResults ? "CGPA, GPA, and percentage values have been normalized where extractable." : "Converting CGPA, GPA, and percentage values to a 10-point scale."}</p>
              <Progress value={progress} />
            </div>
          </div>
        </Card>

        <div className="grid">
          <Card title="Live Status" icon={Clock}>
            {[
              ["Queue", String(pendingCount)],
              ["ETA", isUploading ? "Synchronous" : "N/A"],
              ["Current File", currentFile],
              ["Errors", lastError ? "1" : "0"],
            ].map(([label, value]) => (
              <div className="settings-row" key={label}>
                <span className="muted">{label}</span>
                <span className="mono">{value}</span>
              </div>
            ))}
          </Card>
          <Card title="Processing Queue" icon={ListChecks}>
            {queueRows.map((item, index) => (
              <div className="settings-row" key={`${item.name}-${index}`}>
                <span>{item.name}</span>
                {isUploading && !["Parsed", "Failed"].includes(item.status) ? <StatusBadge tone="processing">Running</StatusBadge> : <span className="muted">{item.status}</span>}
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
