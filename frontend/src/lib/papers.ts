import api from "./api";
import type { Paper, PaperListItem, QueryResult, RelatedPaper } from "@/types";

export async function getPapers(): Promise<PaperListItem[]> {
  const { data } = await api.get("/api/papers/");
  return data;
}

export async function getPaper(id: number): Promise<Paper> {
  const { data } = await api.get(`/api/papers/${id}`);
  return data;
}

export async function uploadPaper(
  file: File,
  title: string,
  authors?: string,
  abstract?: string
): Promise<Paper> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("title", title);
  if (authors) formData.append("authors", authors);
  if (abstract) formData.append("abstract", abstract);

  const { data } = await api.post("/api/papers/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function deletePaper(id: number): Promise<void> {
  await api.delete(`/api/papers/${id}`);
}

export async function summarizePaper(id: number): Promise<string> {
  const { data } = await api.get(`/api/papers/${id}/summary`);
  return data.summary;
}

export async function getRelatedPapers(id: number): Promise<RelatedPaper[]> {
  const { data } = await api.get(`/api/papers/${id}/related`);
  return data;
}

export async function askQuestion(
  paperId: number,
  query: string,
  k: number = 5
): Promise<QueryResult> {
  const { data } = await api.post(`/api/papers/${paperId}/ask`, { query, k });
  return data;
}

export async function globalAsk(query: string, k: number = 5): Promise<QueryResult> {
  const { data } = await api.post("/api/ask", { query, k });
  return data;
}
