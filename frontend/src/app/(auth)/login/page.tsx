"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Box, Card, CardContent, TextField, Button, Typography, Alert,
  Container,
} from "@mui/material";
import { login } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      await login(email, password);
      router.push("/dashboard");
    } catch {
      setError("Invalid email or password");
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ minHeight: "100vh", display: "flex", alignItems: "center" }}>
        <Card sx={{ width: "100%" }}>
          <CardContent sx={{ p: 4 }}>
            <Typography variant="h4" gutterBottom fontWeight={600}>
              Sign In
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Welcome back to AI Research Assistant
            </Typography>
            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
            <Box component="form" onSubmit={handleSubmit}>
              <TextField
                fullWidth label="Email" type="email" margin="normal"
                value={email} onChange={(e) => setEmail(e.target.value)}
                required
              />
              <TextField
                fullWidth label="Password" type="password" margin="normal"
                value={password} onChange={(e) => setPassword(e.target.value)}
                required
              />
              <Button type="submit" variant="contained" fullWidth size="large" sx={{ mt: 3 }}>
                Sign In
              </Button>
            </Box>
            <Box sx={{ mt: 2, textAlign: "center" }}>
              <Typography variant="body2">
                Don't have an account?{" "}
                <Button variant="text" onClick={() => router.push("/register")}>
                  Register
                </Button>
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
}
