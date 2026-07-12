import api from "./api";

export async function login(email: string, password: string) {
  const { data } = await api.post("/api/auth/login", { email, password });
  localStorage.setItem("token", data.access_token);
  return data;
}

export async function register(name: string, email: string, password: string) {
  const { data } = await api.post("/api/auth/register", { name, email, password });
  return data;
}

export async function verifyOtp(email: string, code: string) {
  const { data } = await api.post("/api/auth/verify-otp", { email, code });
  localStorage.setItem("token", data.access_token);
  return data;
}

export async function resendOtp(email: string) {
  const { data } = await api.post("/api/auth/resend-otp", { email });
  return data;
}

export async function getMe() {
  const { data } = await api.get("/api/auth/me");
  return data;
}

export function logout() {
  localStorage.removeItem("token");
  window.location.href = "/login";
}

export function getToken(): string | null {
  if (typeof window !== "undefined") {
    return localStorage.getItem("token");
  }
  return null;
}

export function isAuthenticated(): boolean {
  return !!getToken();
}
