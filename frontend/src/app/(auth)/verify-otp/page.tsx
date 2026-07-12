"use client";
import { Suspense, useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  Box, Card, CardContent, TextField, Button, Typography, Alert,
  Container, CircularProgress,
} from "@mui/material";
import { verifyOtp, resendOtp } from "@/lib/auth";

function VerifyOtpForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const email = searchParams.get("email") || "";
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!email) router.push("/register");
  }, [email, router]);

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await verifyOtp(email, code);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Verification failed");
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    setError("");
    setMessage("");
    setLoading(true);
    try {
      await resendOtp(email);
      setMessage("New OTP sent to your email");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to resend OTP");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ minHeight: "100vh", display: "flex", alignItems: "center" }}>
        <Card sx={{ width: "100%" }}>
          <CardContent sx={{ p: 4 }}>
            <Typography variant="h4" gutterBottom fontWeight={600}>
              Verify Email
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Enter the 6-digit code sent to {email}
            </Typography>
            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
            {message && <Alert severity="success" sx={{ mb: 2 }}>{message}</Alert>}
            <Box component="form" onSubmit={handleVerify}>
              <TextField
                fullWidth label="OTP Code" margin="normal"
                value={code} onChange={(e) => setCode(e.target.value)}
                placeholder="000000" required
                inputProps={{ maxLength: 6, style: { fontSize: "1.5rem", letterSpacing: 8 } }}
              />
              <Button type="submit" variant="contained" fullWidth size="large" sx={{ mt: 3 }} disabled={loading}>
                Verify Account
              </Button>
            </Box>
            <Box sx={{ mt: 2, textAlign: "center" }}>
              <Typography variant="body2">
                Didn't receive the code?{" "}
                <Button variant="text" onClick={handleResend} disabled={loading}>
                  Resend OTP
                </Button>
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
}

export default function VerifyOtpPage() {
  return (
    <Suspense fallback={
      <Container maxWidth="sm">
        <Box sx={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
          <CircularProgress />
        </Box>
      </Container>
    }>
      <VerifyOtpForm />
    </Suspense>
  );
}
