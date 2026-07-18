import { Download, Eye, FileCog, Moon, Shield, SlidersHorizontal } from "lucide-react";
import PageHeader from "../components/common/PageHeader";
import { Card } from "../components/ui/Card";
import { getSettingsSupport } from "../services/settingsService";

function Toggle({ on = false }) {
  return <span aria-hidden="true" className={`toggle ${on ? "on" : ""}`} />;
}

export default function SettingsPage() {
  const support = getSettingsSupport();

  return (
    <>
      <PageHeader
        description="Manage deterministic parsing thresholds, export preferences, and workspace appearance."
        actions={!support.support ? <span className="badge low">Backend settings unavailable</span> : null}
        title="Settings"
      />
      <div className="grid two">
        <Card title="Document Parsing (OCR)" icon={FileCog}>
          <label className="settings-row">
            <span>OCR Engine<br /><span className="muted">Used only when text yield is low.</span></span>
            <select className="select" disabled style={{ maxWidth: 280 }}>
              <option>RecruitAI Advanced (Recommended)</option>
              <option>Tesseract Standard</option>
            </select>
          </label>
          <div className="settings-row">
            <span>Aggressive OCR Mode<br /><span className="muted">Retry scanned documents at high DPI.</span></span>
            <Toggle on />
          </div>
          <div className="settings-row">
            <span>Multi-column Warning<br /><span className="muted">Flag resumes with column risk.</span></span>
            <Toggle on />
          </div>
        </Card>

        <Card title="Confidence Thresholds" icon={SlidersHorizontal}>
          {[
            ["High Confidence", 70],
            ["Medium Confidence", 40],
            ["Auto-Reject Threshold", 50],
          ].map(([label, value]) => (
            <label className="settings-row" key={label}>
              <span>{label}</span>
              <input aria-label={label} disabled max="100" min="0" type="range" value={value} readOnly />
              <span className="mono">{value}</span>
            </label>
          ))}
        </Card>

        <Card title="Appearance" icon={Moon}>
          <div className="settings-row"><span>Theme</span><span className="badge medium">Dark</span></div>
          <div className="settings-row"><span>Density</span><span className="badge">Compact</span></div>
          <div className="settings-row"><span>Reduced Motion</span><Toggle /></div>
        </Card>

        <Card title="Export Preferences" icon={Download}>
          <div className="settings-row"><span>Attach generated summaries to CSV exports.</span><Toggle on /></div>
          <div className="settings-row"><span>Redact PII from candidate profiles on export.</span><Toggle /></div>
          <div className="settings-row"><span>Include parse quality warnings.</span><Toggle on /></div>
        </Card>

        <Card className="span-2" title="Advanced Settings" icon={Shield}>
          <p className="page-copy">TODO: Connect these controls when backend settings/configuration endpoints are exposed. Current reason: {support.reason}</p>
          <div className="grid three">
            <div className="card" style={{ padding: 18 }}><Eye size={20} /><h3>Audit Mode</h3><p className="muted">Preserve every deterministic extraction reason.</p></div>
            <div className="card" style={{ padding: 18 }}><Shield size={20} /><h3>Validation Lock</h3><p className="muted">Prevent scoring weights from changing during a batch.</p></div>
            <div className="card" style={{ padding: 18 }}><FileCog size={20} /><h3>Schema Checks</h3><p className="muted">Validate JD JSON before matching.</p></div>
          </div>
        </Card>
      </div>
    </>
  );
}
