"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Container, Typography, Box, Card, CardContent, Button, Grid,
  CircularProgress,
} from "@mui/material";
import Navbar from "@/components/Navbar";
import { getPapers } from "@/lib/papers";
import { getNotes } from "@/lib/note";
import { isAuthenticated } from "@/lib/auth";
import type { Note } from "@/types";

export default function NotesPage() {
  const router = useRouter();
  const [allNotes, setAllNotes] = useState<{ paperId: number; paperTitle: string; notes: Note[] }[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated()) { router.push("/login"); return; }
    loadAllNotes();
  }, [router]);

  const loadAllNotes = async () => {
    try {
      const papers = await getPapers();
      const notesData = await Promise.all(
        papers.map(async (p) => {
          const notes = await getNotes(p.id);
          return { paperId: p.id, paperTitle: p.title, notes };
        })
      );
      setAllNotes(notesData.filter((n) => n.notes.length > 0));
    } catch { }
    finally { setLoading(false); }
  };

  return (
    <>
      <Navbar />
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography variant="h4" fontWeight={600} gutterBottom>All Notes</Typography>

        {loading ? (
          <Box sx={{ textAlign: "center", py: 8 }}><CircularProgress /></Box>
        ) : allNotes.length === 0 ? (
          <Card sx={{ textAlign: "center", py: 8 }}>
            <CardContent>
              <Typography variant="h6" color="text.secondary">No notes yet</Typography>
              <Typography variant="body2" color="text.secondary">
                Add notes when viewing a paper
              </Typography>
            </CardContent>
          </Card>
        ) : (
          allNotes.map((group) => (
            <Card key={group.paperId} sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  {group.paperTitle}
                </Typography>
                {group.notes.map((note) => (
                  <Box key={note.id} sx={{ mb: 1, p: 2, bgcolor: "grey.50", borderRadius: 1 }}>
                    <Typography variant="body2">{note.content}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {new Date(note.created_at).toLocaleString()}
                    </Typography>
                  </Box>
                ))}
              </CardContent>
            </Card>
          ))
        )}
      </Container>
    </>
  );
}
