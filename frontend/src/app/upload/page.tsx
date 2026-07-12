"use client";
import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  Container, Typography, Box, Card, CardContent, TextField, Button,
  Alert, LinearProgress, Paper,
} from "@mui/material";
import { useDropzone } from "react-dropzone";
import Navbar from "@/components/Navbar";
import { uploadPaper } from "@/lib/papers";
import { isAuthenticated } from "@/lib/auth";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";

export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [authors, setAuthors] = useState("");
  const [abstract, setAbstract] = useState("");
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isAuthenticated()) router.push("/login");
  }, [router]);

  const onDrop = useCallback((accepted: File[]) => {
    if (accepted.length > 0) {
      setFile(accepted[0]);
      if (!title) {
        setTitle(accepted[0].name.replace(".pdf", ""));
      }
    }
  }, [title]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    maxFiles: 1,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !title) return;
    setUploading(true);
    setError("");
    try {
      const paper = await uploadPaper(file, title, authors || undefined, abstract || undefined);
      router.push(`/papers/${paper.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <>
      <Navbar />
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Typography variant="h4" fontWeight={600} gutterBottom>
          Upload Paper
        </Typography>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        <form onSubmit={handleSubmit}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Paper
                {...getRootProps()}
                sx={{
                  p: 6,
                  textAlign: "center",
                  border: "2px dashed",
                  borderColor: isDragActive ? "primary.main" : "divider",
                  bgcolor: isDragActive ? "action.hover" : "background.paper",
                  cursor: "pointer",
                  mb: 2,
                }}
              >
                <input {...getInputProps()} />
                <CloudUploadIcon sx={{ fontSize: 48, color: "text.secondary", mb: 2 }} />
                {file ? (
                  <Typography variant="body1">{file.name}</Typography>
                ) : isDragActive ? (
                  <Typography variant="body1">Drop PDF here</Typography>
                ) : (
                  <Typography variant="body1" color="text.secondary">
                    Drag & drop a PDF here, or click to select
                  </Typography>
                )}
              </Paper>
              <TextField
                fullWidth label="Title" margin="normal" required
                value={title} onChange={(e) => setTitle(e.target.value)}
              />
              <TextField
                fullWidth label="Authors" margin="normal"
                value={authors} onChange={(e) => setAuthors(e.target.value)}
                placeholder="e.g. John Doe, Jane Smith"
              />
              <TextField
                fullWidth label="Abstract" margin="normal" multiline rows={4}
                value={abstract} onChange={(e) => setAbstract(e.target.value)}
              />
            </CardContent>
          </Card>
          {uploading && <LinearProgress sx={{ mb: 2 }} />}
          <Button
            type="submit" variant="contained" size="large" fullWidth
            disabled={!file || !title || uploading}
          >
            {uploading ? "Uploading & Processing..." : "Upload Paper"}
          </Button>
        </form>
      </Container>
    </>
  );
}
