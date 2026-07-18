import { useState } from "react";
import { askAIStream } from "./services/api";
import Header from "./components/Header";
import ProviderSelector from "./components/ProviderSelector";
import AdvancedSettings from "./components/AdvancedSettings";
import PromptInput from "./components/PromptInput";
import AskButton from "./components/AskButton";
import ResponseCard from "./components/ResponseCard";
import "./App.css";

function App() {
  const [provider, setProvider] = useState("smart");
  const [prompt, setPrompt] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [abortController, setAbortController] = useState(null);
  const [latencies, setLatencies] = useState({});

  // Advanced settings state
  const [systemPrompt, setSystemPrompt] = useState("");
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(1000);

  async function handleAskAI() {
    if (!prompt.trim()) return;

    const userMessage = { role: "user", content: prompt };
    const updatedMessages = [...messages, userMessage];

    // Optimistically update message log with user prompt & empty assistant bubble
    setMessages([
      ...updatedMessages,
      {
        role: "assistant",
        content: "",
        provider: provider === "smart" ? "smart" : provider,
        model: "N/A",
        latency: 0,
        isStreaming: true,
      },
    ]);
    
    setPrompt("");
    setLoading(true);
    setIsStreaming(true);

    const controller = new AbortController();
    setAbortController(controller);

    await askAIStream(
      {
        provider,
        messages: updatedMessages,
        systemPrompt,
        temperature,
        maxTokens,
        signal: controller.signal,
      },
      {
        onStart: (data) => {
          setMessages((prev) => {
            const updated = [...prev];
            const last = { ...updated[updated.length - 1] };
            last.provider = data.provider;
            last.model = data.model;
            last.latency = data.ttfb; // Track TTFB latency
            updated[updated.length - 1] = last;
            return updated;
          });
        },
        onToken: (token) => {
          setMessages((prev) => {
            const updated = [...prev];
            const last = { ...updated[updated.length - 1] };
            last.content += token;
            updated[updated.length - 1] = last;
            return updated;
          });
        },
        onProviderSwitch: (data) => {
          setMessages((prev) => {
            const updated = [...prev];
            const last = { ...updated[updated.length - 1] };
            last.content += `🔄 Switched from ${data.from.toUpperCase()} to ${data.to.toUpperCase()} automatically (Reason: ${data.reason})\n\n`;
            last.provider = data.to;
            updated[updated.length - 1] = last;
            return updated;
          });
        },
        onError: (errorMsg) => {
          setMessages((prev) => {
            const updated = [...prev];
            const last = { ...updated[updated.length - 1] };
            last.content = `${errorMsg}`;
            last.isError = true;
            last.isStreaming = false;
            updated[updated.length - 1] = last;
            return updated;
          });
          setIsStreaming(false);
          setLoading(false);
          setAbortController(null);
        },
        onEnd: (data) => {
          setMessages((prev) => {
            const updated = [...prev];
            const last = { ...updated[updated.length - 1] };
            last.latency = data.totalTime;
            last.isStreaming = false;
            updated[updated.length - 1] = last;
            return updated;
          });

          if (data.actualProvider && data.actualProvider !== "smart" && data.actualProvider !== "fallback") {
            const duration = (data.totalTime / 1000).toFixed(1);
            setLatencies((prev) => ({
              ...prev,
              [data.actualProvider]: duration,
            }));
          }

          setIsStreaming(false);
          setLoading(false);
          setAbortController(null);
        },
      }
    );
  }

  function handleStopStreaming() {
    if (abortController) {
      abortController.abort();
      setMessages((prev) => {
        const updated = [...prev];
        const last = { ...updated[updated.length - 1] };
        last.isStreaming = false;
        last.content += "\n\n⏹️ Generation stopped by user.";
        updated[updated.length - 1] = last;
        return updated;
      });
      setIsStreaming(false);
      setLoading(false);
      setAbortController(null);
    }
  }

  function handleClearChat() {
    setMessages([]);
  }

  return (
    <div className="container">
      <Header />

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ flex: 1 }}>
          <ProviderSelector
            provider={provider}
            setProvider={setProvider}
            latencies={latencies}
          />
        </div>
        {messages.length > 0 && (
          <button
            onClick={handleClearChat}
            className="clear-btn"
            style={{
              width: "auto",
              marginTop: "15px",
              marginLeft: "15px",
              padding: "12px 20px",
              background: "#442222",
              color: "#ff8888",
              border: "1px solid #663333",
              borderRadius: "4px",
              cursor: "pointer"
            }}
          >
            🧹 Clear Chat
          </button>
        )}
      </div>

      <AdvancedSettings
        systemPrompt={systemPrompt}
        setSystemPrompt={setSystemPrompt}
        temperature={temperature}
        setTemperature={setTemperature}
        maxTokens={maxTokens}
        setMaxTokens={setMaxTokens}
      />

      <PromptInput
        prompt={prompt}
        setPrompt={setPrompt}
        onSubmit={handleAskAI}
      />

      <div style={{ display: "flex", gap: "10px", marginTop: "15px" }}>
        <div style={{ flex: 1 }}>
          <AskButton
            loading={loading}
            onClick={handleAskAI}
          />
        </div>
        {isStreaming && (
          <button
            onClick={handleStopStreaming}
            className="stop-btn"
            style={{
              width: "auto",
              padding: "12px 20px",
              background: "#552222",
              color: "#ffaaaa",
              border: "1px solid #773333",
              borderRadius: "4px",
              cursor: "pointer"
            }}
          >
            ⏹️ Stop
          </button>
        )}
      </div>

      <ResponseCard
        messages={messages}
      />
    </div>
  );
}

export default App;