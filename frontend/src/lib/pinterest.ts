/**
 * Pinterest OAuth utilities.
 * The actual OAuth flow is server-driven; these helpers talk to our backend
 * so the client_secret never touches the browser.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

/**
 * Ask the backend to generate a Pinterest OAuth URL (with PKCE).
 * Returns the URL to redirect the user to.
 */
export async function generateAuthUrl(): Promise<string> {
  const res = await fetch(`${API_URL}/auth/pinterest`, { credentials: 'include' })
  if (!res.ok) {
    throw new Error(`Failed to generate Pinterest auth URL: ${res.statusText}`)
  }
  const data = (await res.json()) as { auth_url: string; state: string }
  // Store state in sessionStorage for CSRF verification after redirect
  sessionStorage.setItem('pinterest_oauth_state', data.state)
  return data.auth_url
}

/**
 * Exchange the authorisation code (received in the callback URL) for a JWT.
 * The backend handles the PKCE exchange and returns our app's JWT.
 */
export async function exchangeCodeForToken(code: string, state: string): Promise<string> {
  const params = new URLSearchParams({ code, state })
  const res = await fetch(`${API_URL}/auth/callback?${params.toString()}`, {
    credentials: 'include',
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error((body as { detail?: string }).detail ?? 'OAuth callback failed')
  }
  const data = (await res.json()) as { access_token: string }
  return data.access_token
}

/**
 * Check if the stored state matches the returned state (CSRF guard).
 */
export function validateState(returnedState: string): boolean {
  const stored = sessionStorage.getItem('pinterest_oauth_state')
  sessionStorage.removeItem('pinterest_oauth_state')
  return stored === returnedState
}
