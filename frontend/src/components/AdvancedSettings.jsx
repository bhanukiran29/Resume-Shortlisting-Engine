import { useState } from "react";

export default function AdvancedSettings({
  systemPrompt,
  setSystemPrompt,
  temperature,
  setTemperature,
  maxTokens,
  setMaxTokens,
}) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="advanced-settings-container" style={{ marginTop: "15px", textAlign: "left" }}>
      <button
        type="button"
        className="settings-toggle"
        onClick={() => setIsOpen(!isOpen)}
        style={{
          background: "none",
          border: "none",
          color: "#aaa",
          cursor: "pointer",
          fontSize: "14px",
          display: "flex",
          alignItems: "center",
          gap: "5px",
          padding: 0,
          width: "auto"
        }}
      >
        {isOpen ? "▼" : "▶"} Advanced Settings
      </button>
      {isOpen && (
        <div 
          className="settings-panel" 
          style={{
            background: "#1e1e1e",
            border: "1px solid #333",
            borderRadius: "6px",
            padding: "15px",
            marginTop: "10px"
          }}
        >
          <div style={{ marginBottom: "12px" }}>
            <label style={{ display: "block", fontSize: "14px", color: "#ccc", marginBottom: "5px" }}>
              System Prompt
            </label>
            <textarea
              rows="3"
              placeholder="You are a helpful assistant..."
              value={systemPrompt}
              onChange={(e) => setSystemPrompt(e.target.value)}
              style={{
                width: "100%",
                background: "#121212",
                border: "1px solid #444",
                borderRadius: "4px",
                color: "white",
                padding: "8px",
                fontSize: "14px",
                resize: "vertical",
                boxSizing: "border-box",
                marginTop: "5px"
              }}
            />
          </div>
          <div style={{ display: "flex", gap: "15px" }}>
            <div style={{ flex: 1 }}>
              <label style={{ display: "block", fontSize: "14px", color: "#ccc", marginBottom: "5px" }}>
                Temperature ({temperature})
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={temperature}
                onChange={(e) => setTemperature(parseFloat(e.target.value))}
                style={{ width: "100%", marginTop: "10px" }}
              />
            </div>
            <div style={{ flex: 1 }}>
              <label style={{ display: "block", fontSize: "14px", color: "#ccc", marginBottom: "5px" }}>
                Max Tokens
              </label>
              <input
                type="number"
                min="1"
                max="4096"
                value={maxTokens}
                onChange={(e) => setMaxTokens(parseInt(e.target.value) || 1000)}
                style={{
                  width: "100%",
                  background: "#121212",
                  border: "1px solid #444",
                  borderRadius: "4px",
                  color: "white",
                  padding: "8px",
                  fontSize: "14px",
                  boxSizing: "border-box",
                  marginTop: "5px"
                }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
