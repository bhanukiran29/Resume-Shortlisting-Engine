import { useRef, useEffect } from "react";

export default function PromptInput({ prompt, setPrompt, onSubmit }) {
  const textareaRef = useRef(null);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = `${textarea.scrollHeight}px`;
    }
  }, [prompt]);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (onSubmit) {
        onSubmit();
      }
    }
  };

  return (
    <textarea
      ref={textareaRef}
      rows="1"
      placeholder="Ask anything... (Enter to send, Shift+Enter for new line)"
      value={prompt}
      onChange={(e) => setPrompt(e.target.value)}
      onKeyDown={handleKeyDown}
      style={{ overflowY: "hidden", minHeight: "45px" }}
    />
  );
}
