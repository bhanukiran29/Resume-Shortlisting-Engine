import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";

export default function ResponseCard({ messages }) {
  const [copiedIndex, setCopiedIndex] = useState(null);
  const bottomRef = useRef(null);
  const lastScrollTime = useRef(0);

  // Throttled auto-scroll to bottom on new tokens to avoid browser jitter
  useEffect(() => {
    const scroll = () => {
      if (bottomRef.current) {
        bottomRef.current.scrollIntoView({ behavior: "smooth" });
      }
    };

    const now = Date.now();
    if (now - lastScrollTime.current > 150) {
      scroll();
      lastScrollTime.current = now;
    } else {
      const timer = setTimeout(scroll, 150);
      return () => clearTimeout(timer);
    }
  }, [messages]);

  if (!messages || messages.length === 0) return null;

  const handleCopy = async (text, index) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (err) {
      console.error("Failed to copy text: ", err);
    }
  };

  return (
    <div className="chat-history">
      {messages.map((msg, index) => {
        const isUser = msg.role === "user";
        return (
          <div 
            key={index} 
            className={`chat-message ${isUser ? "user-msg" : "assistant-msg"} ${msg.isError ? "error-msg" : ""}`}
          >
            <div className="message-header" style={{ alignItems: "flex-start" }}>
              <div className="sender-info" style={{ display: "flex", flexDirection: "column", textAlign: "left" }}>
                <span className="sender-icon" style={{ fontWeight: "bold", fontSize: "15px" }}>
                  {isUser ? "👤 You" : msg.isError ? "⚠️ Error" : "🤖 AI"}
                </span>
                {!isUser && msg.provider && (
                  <span className="provider-meta" style={{ fontSize: "10.5px", color: "#888", marginTop: "4px" }}>
                    {msg.provider === "fallback" ? (
                      `Smart Mode • Fallback exhausted • ${(msg.latency / 1000).toFixed(2)}s`
                    ) : (
                      `${msg.provider.toUpperCase()} • ${msg.model} • ${msg.latency < 1000 ? `${msg.latency}ms` : `${(msg.latency / 1000).toFixed(2)}s`}`
                    )}
                  </span>
                )}
              </div>
              {!isUser && !msg.isError && !msg.isStreaming && (
                <button 
                  className="copy-btn" 
                  style={{ padding: "4px 8px", fontSize: "12px" }}
                  onClick={() => handleCopy(msg.content, index)}
                >
                  {copiedIndex === index ? "✅ Copied!" : "📋 Copy"}
                </button>
              )}
            </div>
            <div className="message-content">
              {isUser ? (
                <p style={{ margin: 0, whiteSpace: "pre-wrap" }}>{msg.content}</p>
              ) : msg.isStreaming ? (
                msg.content === "" ? (
                  <span className="typing-indicator" style={{ fontStyle: "italic", color: "#888" }}>Thinking...</span>
                ) : (
                  <p style={{ margin: 0, whiteSpace: "pre-wrap" }}>{msg.content}</p>
                )
              ) : (
                <div className="markdown-content">
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
              )}
            </div>
          </div>
        );
      })}
      <div ref={bottomRef} />
    </div>
  );
}
