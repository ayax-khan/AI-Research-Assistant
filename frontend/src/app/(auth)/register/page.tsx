"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Box, Card, CardContent, TextField, Button, Typography, Alert,
  Container,
} from "@mui/material";
import { register } from "@/lib/auth";

export default function RegisterPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      await register(name, email, password);
      router.push(`/verify-otp?email=${encodeURIComponent(email)}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Registration failed");
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ minHeight: "100vh", display: "flex", alignItems: "center" }}>
        <Card sx={{ width: "100%" }}>
          <CardContent sx={{ p: 4 }}>
            <Typography variant="h4" gutterBottom fontWeight={600}>
              Create Account
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Join AI Research Assistant
            </Typography>
            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
            <Box component="form" onSubmit={handleSubmit}>
              <TextField
                fullWidth label="Full Name" margin="normal"
                value={name} onChange={(e) => setName(e.target.value)}
                required
              />
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
                Create Account
              </Button>
            </Box>
            <Box sx={{ mt: 2, textAlign: "center" }}>
              <Typography variant="body2">
                Already have an account?{" "}
                <Button variant="text" onClick={() => router.push("/login")}>
                  Sign In
                </Button>
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
}
