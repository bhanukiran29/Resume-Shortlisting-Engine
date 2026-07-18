export function buildAnalytics(candidates) {
  const skillCounts = new Map();
  const collegeCounts = new Map();
  const confidenceCounts = new Map();
  const scored = [];

  candidates.forEach((candidate) => {
    candidate.skills.forEach((skill) => skillCounts.set(skill, (skillCounts.get(skill) || 0) + 1));
    if (candidate.college && candidate.college !== "Not extracted") {
      collegeCounts.set(candidate.college, (collegeCounts.get(candidate.college) || 0) + 1);
    }
    confidenceCounts.set(candidate.confidence, (confidenceCounts.get(candidate.confidence) || 0) + 1);
    if (typeof candidate.score === "number") scored.push(candidate.score);
  });

  return {
    averageScore: scored.length ? Math.round(scored.reduce((sum, score) => sum + score, 0) / scored.length) : null,
    averageConfidence: null,
    scoreDistribution: [
      { range: "<60", count: scored.filter((score) => score < 60).length },
      { range: "60s", count: scored.filter((score) => score >= 60 && score < 70).length },
      { range: "70s", count: scored.filter((score) => score >= 70 && score < 80).length },
      { range: "80s", count: scored.filter((score) => score >= 80 && score < 90).length },
      { range: "90+", count: scored.filter((score) => score >= 90).length },
    ],
    confidenceDistribution: Array.from(confidenceCounts, ([name, value]) => ({ name, value })),
    topSkills: Array.from(skillCounts, ([skill, count]) => ({ skill, count })).sort((a, b) => b.count - a.count).slice(0, 5),
    topColleges: Array.from(collegeCounts, ([college, count]) => ({ college, count })).sort((a, b) => b.count - a.count).slice(0, 5),
  };
}
