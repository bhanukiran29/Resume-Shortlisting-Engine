export function normalizeUploadToCandidate(uploadResult, index = 0) {
  const parsed = uploadResult?.parsed_data ?? {};
  const contact = parsed.contact_info ?? {};
  const skills = Array.isArray(parsed.skills) ? parsed.skills : [];
  const education = Array.isArray(parsed.education) ? parsed.education : [];
  const rawScore = parsed.score ?? parsed.overall_score;
  const score = typeof rawScore === "number" && Number.isFinite(rawScore)
    ? Math.min(100, Math.max(0, rawScore))
    : null;

  return {
    id: uploadResult?.file_path || parsed.filename || `candidate-${index}`,
    fileName: parsed.filename || uploadResult?.file_path?.split(/[\\/]/).pop() || "Uploaded resume",
    name: contact.name || parsed.name || parsed.filename?.replace(/\.[^.]+$/, "").replace(/[_-]+/g, " ") || "Unidentified Candidate",
    role: parsed.job_title || "Uploaded Resume",
    email: contact.email || parsed.email || "Not extracted",
    phone: contact.phone || parsed.phone || "Not extracted",
    college: parsed.college || education[0] || "Not extracted",
    degree: parsed.degree || education[1] || "Not extracted",
    cgpa: parsed.normalized_cgpa ?? parsed.cgpa ?? null,
    skills,
    score,
    confidence: parsed.confidence ?? "Unavailable",
    status: parsed.allocation && parsed.allocation !== "Unscored" ? parsed.allocation : typeof score === "number" ? "Scored" : parsed.parse_quality || "Parsed",
    raw: uploadResult,
  };
}

export function fetchCandidatesFromUploads(uploadResults) {
  return uploadResults.map((result, index) => normalizeUploadToCandidate(result, index));
}
