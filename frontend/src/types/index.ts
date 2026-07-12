export interface User {
  id: number;
  name: string;
  email: string;
  created_at: string;
}

export interface Paper {
  id: number;
  title: string;
  authors: string | null;
  abstract: string | null;
  file_path: string | null;
  uploaded_at: string;
  uploaded_by: number;
}

export interface PaperListItem {
  id: number;
  title: string;
  authors: string | null;
  uploaded_at: string;
}

export interface Note {
  id: number;
  user_id: number;
  paper_id: number;
  content: string;
  created_at: string;
  updated_at: string | null;
}

export interface QueryResult {
  answer: string;
  sources: Source[];
}

export interface Source {
  paper_id: number;
  paper_title: string;
  excerpt: string;
  score: number;
}

export interface SearchResult {
  paper_id: number;
  paper_title: string;
  chunk_text: string;
  score: number;
}

export interface RelatedPaper {
  id: number;
  title: string;
  authors: string | null;
  similarity_score: number;
}
