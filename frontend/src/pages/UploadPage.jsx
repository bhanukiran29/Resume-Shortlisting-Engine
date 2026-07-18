import { AlertCircle, CheckCircle2, Clock, File, FileText, Folder, ListOrdered, PieChart, Play, UploadCloud, X } from "lucide-react";
import { useRef, useState } from "react";
import PageHeader from "../components/common/PageHeader";
import { Card } from "../components/ui/Card";
import { Progress } from "../components/ui/Progress";
import { useAppData } from "../hooks/useAppData";

export default function UploadPage() {
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef(null);
  const { clearUploads, isUploading, lastError, uploadFiles, uploadQueue, uploadResults } = useAppData();

  const handleFiles = (files) => {
    uploadFiles(files);
  };

  return (
    <>
      <PageHeader
        description="Drop resumes or portfolios here to begin parsing. The engine extracts deterministic fields and prepares candidates for matching."
        title="Upload Candidates"
      />
      <div className="grid split-grid">
        <section
          className={`dropzone ${dragging ? "dragging" : ""}`}
          onDragEnter={() => setDragging(true)}
          onDragLeave={() => setDragging(false)}
          onDragOver={(event) => event.preventDefault()}
          onDrop={(event) => {
            event.preventDefault();
            setDragging(false);
            handleFiles(event.dataTransfer.files);
          }}
        >
          <div className="upload-illustration">
            <UploadCloud size={72} />
          </div>
          <h3 className="page-title" style={{ marginTop: 28 }}>Drag & drop files here</h3>
          <p className="page-copy" style={{ marginBottom: 28 }}>
            Upload resumes, portfolios, or cover letters. Supported formats are PDF, DOCX, and TXT.
          </p>
          <div className="topbar__actions" style={{ justifyContent: "center", marginBottom: 26 }}>
            {["PDF", "DOCX", "TXT"].map((type) => (
              <span className="badge" key={type}>{type}</span>
            ))}
          </div>
          <input hidden multiple ref={inputRef} type="file" accept=".pdf,.docx,.doc,.txt" onChange={(event) => handleFiles(event.target.files)} />
          <button className="button primary" onClick={() => inputRef.current?.click()} type="button">
            Browse Files
          </button>
          <p className="muted" style={{ marginTop: 18 }}>Maximum 500 files per batch upload. Max 10MB each.</p>
        </section>

        <div className="grid">
          <Card title="Upload Queue" icon={ListOrdered}>
            {lastError ? <p className="page-copy" style={{ color: "var(--error)", marginBottom: 14 }}>{lastError}</p> : null}
            {uploadQueue.length ? (
              <div className="grid" style={{ gap: 12 }}>
              {uploadQueue.map((item) => {
                const Icon = item.status === "Parsed" ? CheckCircle2 : item.status === "Failed" ? AlertCircle : item.status === "Queued" ? Clock : FileText;
                return (
                  <div className="card" key={item.name} style={{ padding: 16, borderColor: item.tone === "error" ? "rgba(251,113,133,.35)" : undefined }}>
                    <div style={{ display: "flex", gap: 12, justifyContent: "space-between" }}>
                      <div style={{ display: "flex", gap: 12, minWidth: 0 }}>
                        <Icon color={item.status === "Failed" ? "#fb7185" : item.status === "Parsed" ? "#34d399" : "#c7c4d7"} size={20} />
                        <div style={{ minWidth: 0 }}>
                          <div className="mono" style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{item.name}</div>
                          <div className="muted">{Math.round(item.size / 1024)} KB · {item.status}</div>
                        </div>
                      </div>
                      <button className="icon-button" type="button"><X size={16} /></button>
                    </div>
                    <div style={{ marginTop: 12 }}><Progress value={item.progress} /></div>
                  </div>
                );
              })}
              </div>
            ) : <p className="page-copy">No files queued. Select resumes to call the backend upload parser.</p>}
          </Card>

          <Card title="Processing Summary" icon={PieChart}>
            <div className="grid two">
              <div className="card" style={{ padding: 16 }}><span className="label">Processed</span><div className="page-title" style={{ color: "#34d399" }}>{uploadResults.length}</div></div>
              <div className="card" style={{ padding: 16 }}><span className="label">Errors</span><div className="page-title" style={{ color: "#fb7185" }}>{lastError ? 1 : 0}</div></div>
            </div>
          </Card>

          <Card title="Recent Uploads" icon={Folder}>
            {(uploadResults.length ? uploadResults.slice(-3).reverse().map((result) => result.parsed_data?.filename || result.file_path) : ["No backend uploads yet"]).map((item) => (
              <div className="settings-row" key={item}>
                <span>{item}<br /><span className="muted">{uploadResults.length ? "Parsed by backend" : "Upload resumes to populate this list"}</span></span>
                <File size={18} color="var(--primary)" />
              </div>
            ))}
          </Card>
        </div>
      </div>

      <div className="card" style={{ position: "sticky", bottom: 0, marginTop: 24, padding: 18, backdropFilter: "blur(16px)" }}>
        <div className="settings-row">
          <div style={{ flex: 1 }}>
            <div className="settings-row" style={{ paddingTop: 0 }}>
              <span className="label">Batch Progress</span>
              <span className="mono">{uploadQueue.filter((item) => item.status === "Parsed").length} / {uploadQueue.length || 0} Files</span>
            </div>
            <Progress value={uploadQueue.length ? Math.round((uploadQueue.filter((item) => item.status === "Parsed").length / uploadQueue.length) * 100) : 0} />
          </div>
          <button className="button secondary" onClick={clearUploads} type="button">Clear</button>
          <button className="button primary" disabled={isUploading} type="button"><Play size={16} /> {isUploading ? "Processing" : "Synchronous Processing"}</button>
        </div>
      </div>
    </>
  );
}
