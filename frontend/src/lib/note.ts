import api from "./api";
import type { Note } from "@/types";

export async function getNotes(paperId: number): Promise<Note[]> {
  const { data } = await api.get(`/api/papers/${paperId}/notes`);
  return data;
}

export async function createNote(paperId: number, content: string): Promise<Note> {
  const { data } = await api.post(`/api/papers/${paperId}/notes`, { content });
  return data;
}

export async function updateNote(noteId: number, content: string): Promise<Note> {
  const { data } = await api.put(`/api/notes/${noteId}`, { content });
  return data;
}

export async function deleteNote(noteId: number): Promise<void> {
  await api.delete(`/api/notes/${noteId}`);
}
