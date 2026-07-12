"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  Container, Typography, Box, Card, CardContent, Button, Grid,
  TextField, CircularProgress, Divider, Chip, List, ListItem,
  ListItemText, Alert, IconButton,
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";
import ReactMarkdown from "react-markdown";
import Navbar from "@/components/Navbar";
import { getPaper, summarizePaper, getRelatedPapers, askQuestion, deletePaper } from "@/lib/papers";
import { getNotes, createNote, updateNote, deleteNote } from "@/lib/note";
import { isAuthenticated } from "@/lib/auth";
import type { Paper, RelatedPaper, Note, QueryResult } from "@/types";

export default function PaperDetailPage() {
  const params = useParams();
  const router = useRouter();
  const paperId = Number(params.id);

  const [paper, setPaper] = useState<Paper | null>(null);
  const [summary, setSummary] = useState("");
  const [relatedPapers, setRelatedPapers] = useState<RelatedPaper[]>([]);
  const [notes, setNotes] = useState<Note[]>([]);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<QueryResult | null>(null);
  const [newNote, setNewNote] = useState("");
  const [editingNote, setEditingNote] = useState<Note | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated()) { router.push("/login"); return; }
    loadData();
  }, [paperId]);

  const loadData = async () => {
    try {
      const [p, n] = await Promise.all([getPaper(paperId), getNotes(paperId)]);
      setPaper(p);
      setNotes(n);
    } catch {
      router.push("/dashboard");
    } finally {
      setLoading(false);
    }
  };

  const handleSummarize = async () => {
    try {
      const s = await summarizePaper(paperId);
      setSummary(s);
    } catch { }
  };

  const handleRelated = async () => {
    try {
      const r = await getRelatedPapers(paperId);
      setRelatedPapers(r);
    } catch { }
  };

  const handleAsk = async () => {
    if (!question.trim()) return;
    try {
      const result = await askQuestion(paperId, question);
      setAnswer(result);
    } catch { }
  };

  const handleAddNote = async () => {
    if (!newNote.trim()) return;
    try {
      const note = await createNote(paperId, newNote);
      setNotes([note, ...notes]);
      setNewNote("");
    } catch { }
  };

  const handleUpdateNote = async (note: Note) => {
    try {
      const updated = await updateNote(note.id, note.content);
      setNotes(notes.map((n) => (n.id === updated.id ? updated : n)));
      setEditingNote(null);
    } catch { }
  };

  const handleDeleteNote = async (noteId: number) => {
    try {
      await deleteNote(noteId);
      setNotes(notes.filter((n) => n.id !== noteId));
    } catch { }
  };

  const handleDeletePaper = async () => {
    if (!confirm("Delete this paper?")) return;
    try {
      await deletePaper(paperId);
      router.push("/dashboard");
    } catch { }
  };

  if (loading) {
    return (
      <>
        <Navbar />
        <Box sx={{ textAlign: "center", py: 8 }}><CircularProgress /></Box>
      </>
    );
  }

  if (!paper) return null;

  return (
    <>
      <Navbar />
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "start", mb: 3 }}>
          <Box>
            <Typography variant="h4" fontWeight={600}>{paper.title}</Typography>
            {paper.authors && (
              <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
                {paper.authors}
              </Typography>
            )}
            <Chip label={new Date(paper.uploaded_at).toLocaleDateString()} size="small" sx={{ mt: 1 }} />
          </Box>
          <Button color="error" startIcon={<DeleteIcon />} onClick={handleDeletePaper}>
            Delete
          </Button>
        </Box>

        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom fontWeight={600}>Abstract</Typography>
                <Typography variant="body2">
                  {paper.abstract || "No abstract available."}
                </Typography>
              </CardContent>
            </Card>

            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom fontWeight={600}>Summary</Typography>
                {summary ? (
                  <Typography variant="body2">{summary}</Typography>
                ) : (
                  <Button variant="outlined" onClick={handleSummarize}>
                    Generate Summary
                  </Button>
                )}
              </CardContent>
            </Card>

            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom fontWeight={600}>Ask a Question</Typography>
                <Box sx={{ display: "flex", gap: 1, mb: 2 }}>
                  <TextField
                    fullWidth size="small" placeholder="Ask about this paper..."
                    value={question} onChange={(e) => setQuestion(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleAsk()}
                  />
                  <Button variant="contained" onClick={handleAsk} disabled={!question.trim()}>
                    Ask
                  </Button>
                </Box>
                {answer && (
                  <Box sx={{ bgcolor: "grey.50", p: 2, borderRadius: 2 }}>
                    <Box sx={{ "& p": { mb: 1 }, "& ul": { pl: 2, mb: 1 }, "& li": { mb: 0.5 } }}>
                      <ReactMarkdown>{answer.answer}</ReactMarkdown>
                    </Box>
                    {answer.sources.length > 0 && (
                      <>
                        <Divider sx={{ my: 1 }} />
                        <Typography variant="caption" fontWeight={600}>Sources:</Typography>
                        {answer.sources.map((s, i) => (
                          <Typography key={i} variant="caption" display="block" color="text.secondary">
                            {s.paper_title} (score: {s.score.toFixed(2)})
                          </Typography>
                        ))}
                      </>
                    )}
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom fontWeight={600}>Related Papers</Typography>
                {relatedPapers.length > 0 ? (
                  <List dense>
                    {relatedPapers.map((rp) => (
                      <ListItem key={rp.id} disablePadding>
                        <ListItemText
                          primary={rp.title}
                          secondary={`${rp.authors || ""} (${(rp.similarity_score * 100).toFixed(0)}% match)`}
                          primaryTypographyProps={{ variant: "body2", noWrap: true }}
                        />
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Button variant="outlined" size="small" onClick={handleRelated}>
                    Find Related
                  </Button>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom fontWeight={600}>Notes</Typography>
                <Box sx={{ display: "flex", gap: 1, mb: 2 }}>
                  <TextField
                    fullWidth size="small" placeholder="Add a note..."
                    value={newNote} onChange={(e) => setNewNote(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleAddNote()}
                  />
                  <Button variant="contained" size="small" onClick={handleAddNote} disabled={!newNote.trim()}>
                    Add
                  </Button>
                </Box>
                {notes.length > 0 ? (
                  <List dense>
                    {notes.map((note) => (
                      <ListItem
                        key={note.id}
                        secondaryAction={
                          <Box>
                            <IconButton size="small" onClick={() => setEditingNote(note)}>
                              <EditIcon fontSize="small" />
                            </IconButton>
                            <IconButton size="small" onClick={() => handleDeleteNote(note.id)}>
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </Box>
                        }
                      >
                        {editingNote?.id === note.id ? (
                          <Box sx={{ width: "100%" }}>
                            <TextField
                              fullWidth size="small" value={editingNote.content}
                              onChange={(e) => setEditingNote({ ...editingNote, content: e.target.value })}
                              onKeyDown={(e) => e.key === "Enter" && handleUpdateNote(editingNote)}
                            />
                          </Box>
                        ) : (
                          <ListItemText
                            primary={note.content}
                            secondary={new Date(note.created_at).toLocaleDateString()}
                            primaryTypographyProps={{ variant: "body2" }}
                          />
                        )}
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Typography variant="body2" color="text.secondary">No notes yet</Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>
    </>
  );
}
