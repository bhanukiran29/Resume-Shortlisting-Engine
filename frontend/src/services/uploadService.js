import { httpClient } from "./httpClient";

export async function uploadResume(file, onUploadProgress) {
  const formData = new FormData();
  formData.append("file", file);
  return httpClient.post("/api/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress,
  });
}

export async function uploadResumes(files, onFileProgress) {
  const results = [];
  for (const file of files) {
    const response = await uploadResume(file, (event) => {
      if (!event.total) return;
      onFileProgress?.(file.name, Math.round((event.loaded / event.total) * 100));
    });
    results.push(response.data);
  }
  return results;
}
