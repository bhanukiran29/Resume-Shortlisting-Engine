export default function AskButton({ loading, onClick }) {
  return (
    <button onClick={onClick} disabled={loading} className="ask-btn">
      {loading ? (
        <span className="spinner-container">
          <span className="spinner"></span> Generating response...
        </span>
      ) : (
        "Ask AI"
      )}
    </button>
  );
}
