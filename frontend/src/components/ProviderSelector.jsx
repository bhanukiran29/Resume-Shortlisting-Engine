import { PROVIDERS } from "../utils/providerConfig";

export default function ProviderSelector({ provider, setProvider, latencies = {} }) {
  return (
    <select
      value={provider}
      onChange={(e) => setProvider(e.target.value)}
    >
      {Object.entries(PROVIDERS).map(([key, value]) => {
        const latency = latencies[key];
        const displayLatency = latency ? ` (⚡ ${latency}s)` : "";
        return (
          <option key={key} value={key}>
            {value.name}{displayLatency}
          </option>
        );
      })}
    </select>
  );
}
