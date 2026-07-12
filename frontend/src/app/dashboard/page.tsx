"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Container, Typography, Box, Card, CardContent, CardActions,
  Button, Grid, Chip, CircularProgress,
} from "@mui/material";
import Navbar from "@/components/Navbar";
import { getPapers } from "@/lib/papers";
import { isAuthenticated } from "@/lib/auth";
import type { PaperListItem } from "@/types";

export default function DashboardPage() {
  const router = useRouter();
  const [papers, setPapers] = useState<PaperListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/login");
      return;
    }
    loadPapers();
  }, [router]);

  const loadPapers = async () => {
    try {
      const data = await getPapers();
      setPapers(data);
    } catch {
      setPapers([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 4 }}>
          <Typography variant="h4" fontWeight={600}>My Papers</Typography>
          <Button variant="contained" onClick={() => router.push("/upload")}>
            Upload Paper
          </Button>
        </Box>

        {loading ? (
          <Box sx={{ textAlign: "center", py: 8 }}>
            <CircularProgress />
          </Box>
        ) : papers.length === 0 ? (
          <Card sx={{ textAlign: "center", py: 8 }}>
            <CardContent>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No papers yet
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Upload your first research paper to get started
              </Typography>
              <Button variant="contained" onClick={() => router.push("/upload")}>
                Upload Paper
              </Button>
            </CardContent>
          </Card>
        ) : (
          <Grid container spacing={3}>
            {papers.map((paper) => (
              <Grid item xs={12} sm={6} md={4} key={paper.id}>
                <Card sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Typography variant="h6" fontWeight={600} gutterBottom noWrap>
                      {paper.title}
                    </Typography>
                    {paper.authors && (
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        {paper.authors}
                      </Typography>
                    )}
                    <Chip
                      label={new Date(paper.uploaded_at).toLocaleDateString()}
                      size="small"
                      variant="outlined"
                      sx={{ mt: 1 }}
                    />
                  </CardContent>
                  <CardActions>
                    <Button size="small" onClick={() => router.push(`/papers/${paper.id}`)}>
                      View
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Container>
    </>
  );
}
