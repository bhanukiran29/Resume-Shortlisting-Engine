import { useCallback, useEffect, useMemo, useState } from "react";
import { uploadResumes } from "../services/uploadService";
import { fetchCandidatesFromUploads } from "../services/candidateService";
import { buildAnalytics } from "../services/analyticsService";
import { buildDashboardSummary } from "../services/dashboardService";
import { AppDataContext } from "./AppDataContextValue";

const STORAGE_KEY = "resume-shortlisting.uploadResults";

export function AppDataProvider({ children }) {
  const [uploadResults, setUploadResults] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
    } catch {
      return [];
    }
  });
  const [uploadQueue, setUploadQueue] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [lastError, setLastError] = useState(null);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(uploadResults));
  }, [uploadResults]);

  const candidates = useMemo(
    () => uploadResults.map((result, index) => fetchCandidatesFromUploads([result], index)).flat(),
    [uploadResults],
  );
  const dashboard = useMemo(() => buildDashboardSummary(candidates), [candidates]);
  const analytics = useMemo(() => buildAnalytics(candidates), [candidates]);

  const uploadFiles = useCallback(async (files) => {
    const selected = Array.from(files);
    if (!selected.length) return [];

    setLastError(null);
    setIsUploading(true);
    setUploadQueue(selected.map((file) => ({
      name: file.name,
      size: file.size,
      progress: 0,
      status: "Queued",
      error: null,
    })));

    try {
      const results = await uploadResumes(selected, (fileName, progress) => {
        setUploadQueue((queue) => queue.map((item) => (
          item.name === fileName ? { ...item, progress, status: progress >= 100 ? "Processing" : "Uploading" } : item
        )));
      });

      setUploadResults((current) => [...current, ...results]);
      setUploadQueue((queue) => queue.map((item) => ({ ...item, progress: 100, status: "Parsed" })));
      return results;
    } catch (error) {
      const message = error.response?.data?.detail || error.message || "Upload failed";
      setLastError(message);
      setUploadQueue((queue) => queue.map((item) => (
        item.status === "Parsed" ? item : { ...item, status: "Failed", error: message }
      )));
      return [];
    } finally {
      setIsUploading(false);
    }
  }, []);

  const clearUploads = useCallback(() => {
    setUploadResults([]);
    setUploadQueue([]);
    setLastError(null);
  }, []);

  const value = useMemo(() => ({
    analytics,
    candidates,
    clearUploads,
    dashboard,
    isUploading,
    lastError,
    uploadFiles,
    uploadQueue,
    uploadResults,
  }), [analytics, candidates, clearUploads, dashboard, isUploading, lastError, uploadFiles, uploadQueue, uploadResults]);

  return <AppDataContext.Provider value={value}>{children}</AppDataContext.Provider>;
}
