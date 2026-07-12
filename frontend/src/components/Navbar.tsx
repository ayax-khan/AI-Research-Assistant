"use client";
import { AppBar, Toolbar, Typography, Button, Box } from "@mui/material";
import { useRouter } from "next/navigation";
import { logout, isAuthenticated } from "@/lib/auth";

export default function Navbar() {
  const router = useRouter();

  return (
    <AppBar position="static" elevation={0} sx={{ bgcolor: "white", borderBottom: 1, borderColor: "divider" }}>
      <Toolbar>
        <Typography
          variant="h6"
          fontWeight={700}
          color="primary"
          sx={{ cursor: "pointer", flexGrow: 1 }}
          onClick={() => router.push("/dashboard")}
        >
          ResearchAI
        </Typography>
        {isAuthenticated() && (
          <Box sx={{ display: "flex", gap: 1 }}>
            <Button color="inherit" onClick={() => router.push("/dashboard")}>
              Dashboard
            </Button>
            <Button color="inherit" onClick={() => router.push("/upload")}>
              Upload
            </Button>
            <Button color="error" onClick={() => { logout(); }}>
              Logout
            </Button>
          </Box>
        )}
      </Toolbar>
    </AppBar>
  );
}
