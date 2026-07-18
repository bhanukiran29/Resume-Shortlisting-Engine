export const PROVIDERS = {
  smart: {
    name: "Smart (Groq → OpenRouter → Gemini)",
    model: "Auto-Fallback",
    supportsVision: false,
  },
  groq: {
    name: "Groq",
    model: "llama-3.3-70b-versatile",
    supportsVision: false,
  },
  openrouter: {
    name: "OpenRouter",
    model: "openai/gpt-oss-20b:free",
    supportsVision: false,
  },
  gemini: {
    name: "Gemini",
    model: "gemini-2.0-flash",
    supportsVision: true,
  },
};
