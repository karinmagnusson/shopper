const KEY = "shopper_token";

export function setToken(token: string) {
  if (typeof window !== "undefined") localStorage.setItem(KEY, token);
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(KEY);
}

export function removeToken() {
  if (typeof window !== "undefined") localStorage.removeItem(KEY);
}
