export function buildDashboardSummary(candidates) {
  const total = candidates.length;
  const withSkills = candidates.filter((candidate) => candidate.skills.length > 0).length;
  const highConfidence = candidates.filter((candidate) => candidate.confidence === "High").length;
  const mediumConfidence = candidates.filter((candidate) => candidate.confidence === "Medium").length;
  const lowConfidence = candidates.filter((candidate) => candidate.confidence === "Low").length;
  const scored = candidates.map((candidate) => candidate.score).filter((score) => typeof score === "number");

  return {
    total,
    processed: total,
    parsedWithSkills: withSkills,
    highConfidence,
    mediumConfidence,
    lowConfidence,
    topScore: scored.length ? Math.max(...scored) : null,
    recentUploads: candidates.slice(-5).reverse(),
    pipelineHealth: total ? "Synchronous upload parsing complete" : "Awaiting uploads",
  };
}
