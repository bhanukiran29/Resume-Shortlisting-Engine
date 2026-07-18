import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL;

export async function askAI(options) {
  const response = await axios.post(`${API_URL}/api/chat`, options);

  return response.data;
}

export async function askAIStream(options, callbacks) {
  const { onStart, onToken, onProviderSwitch, onError, onEnd } = callbacks;
  const { signal, ...reqBody } = options;

  try {
    const response = await fetch(`${API_URL}/api/chat/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(reqBody),
      signal,
    });

    if (!response.ok) {
      const errText = await response.text();
      throw new Error(`HTTP Error ${response.status}: ${errText}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split("\n\n");
        buffer = parts.pop() || "";

        for (const part of parts) {
          const lines = part.split("\n");
          let event = "message";
          let dataStr = "";

          for (const line of lines) {
            if (line.startsWith("event: ")) {
              event = line.slice(7).trim();
            } else if (line.startsWith("data: ")) {
              dataStr = line.slice(6).trim();
            }
          }

          if (!dataStr) continue;

          let data;
          try {
            data = JSON.parse(dataStr);
          } catch (e) {
            continue;
          }

          if (event === "start" && onStart) {
            onStart(data);
          } else if (event === "token" && onToken) {
            onToken(data.token);
          } else if (event === "provider-switch" && onProviderSwitch) {
            onProviderSwitch(data);
          } else if (event === "error" && onError) {
            onError(data.error);
          } else if (event === "end" && onEnd) {
            onEnd(data);
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  } catch (err) {
    if (err.name === "AbortError") {
      console.log("Fetch stream call aborted.");
    } else {
      if (onError) onError(err.message);
    }
  }
}
