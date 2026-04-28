/**
 * Backend API client with JWT handling and typed responses.
 */

import type { BoardAnalysisResponse, BoardsResponse, PinsResponse } from '@/types/pinterest'
import type { ProductFilters, RecommendationsResponse, SearchResponse } from '@/types/products'

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

const TOKEN_KEY = 'shopper_jwt'

// ---------------------------------------------------------------------------
// Token helpers
// ---------------------------------------------------------------------------

export function getToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

// ---------------------------------------------------------------------------
// Core fetch wrapper
// ---------------------------------------------------------------------------

interface RequestOptions extends Omit<RequestInit, 'body'> {
  body?: unknown
  params?: Record<string, string | number | boolean | string[] | undefined>
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { body, params, ...init } = options

  const url = new URL(`${API_URL}${path}`)
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value === undefined) return
      if (Array.isArray(value)) {
        value.forEach((v) => url.searchParams.append(key, String(v)))
      } else {
        url.searchParams.set(key, String(value))
      }
    })
  }

  const token = getToken()
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(init.headers ?? {}),
  }

  const response = await fetch(url.toString(), {
    ...init,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
    credentials: 'include',
  })

  if (response.status === 401) {
    clearToken()
    if (typeof window !== 'undefined') {
      window.location.href = '/'
    }
    throw new Error('Unauthorised – please log in again')
  }

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}))
    const message = (errorBody as { detail?: string }).detail ?? response.statusText
    throw new Error(message)
  }

  if (response.status === 204) return undefined as unknown as T
  return response.json() as Promise<T>
}

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

export async function logout(): Promise<void> {
  await request('/auth/logout', { method: 'DELETE' })
  clearToken()
}

// ---------------------------------------------------------------------------
// Boards
// ---------------------------------------------------------------------------

export async function getBoards(): Promise<BoardsResponse> {
  return request<BoardsResponse>('/boards')
}

export async function syncBoards(): Promise<{ synced: number; message: string }> {
  return request('/boards/sync', { method: 'POST' })
}

export async function getBoardPins(boardId: string): Promise<PinsResponse> {
  return request<PinsResponse>(`/boards/${boardId}/pins`)
}

export async function analyzeBoard(boardId: string): Promise<BoardAnalysisResponse> {
  return request<BoardAnalysisResponse>(`/boards/${boardId}/analyze`)
}

// ---------------------------------------------------------------------------
// Products
// ---------------------------------------------------------------------------

export async function getRecommendations(
  filters: ProductFilters & { limit?: number; offset?: number } = {}
): Promise<RecommendationsResponse> {
  const { colors, ...rest } = filters
  return request<RecommendationsResponse>('/products/recommendations', {
    params: {
      ...rest,
      ...(colors && colors.length > 0 ? { colors } : {}),
    } as Record<string, string | number | boolean | string[] | undefined>,
  })
}

export async function searchProducts(
  filters: ProductFilters & { limit?: number; offset?: number } = {}
): Promise<SearchResponse> {
  const { colors, ...rest } = filters
  return request<SearchResponse>('/products/search', {
    params: {
      ...rest,
      ...(colors && colors.length > 0 ? { colors } : {}),
    } as Record<string, string | number | boolean | string[] | undefined>,
  })
}

export async function trackClick(productId: string, interactionType = 'click'): Promise<void> {
  await request('/products/track-click', {
    method: 'POST',
    body: { product_id: productId, interaction_type: interactionType },
  })
}

// ---------------------------------------------------------------------------
// Users
// ---------------------------------------------------------------------------

export interface UserProfile {
  id: string
  pinterest_id: string
  email: string | null
  style_preferences: Record<string, unknown>
  created_at: string
  last_sync: string | null
}

export async function getCurrentUser(): Promise<UserProfile> {
  return request<UserProfile>('/users/me')
}

export async function updatePreferences(
  preferences: Record<string, unknown>
): Promise<{ message: string; style_preferences: Record<string, unknown> }> {
  return request('/users/me/preferences', { method: 'PUT', body: preferences })
}

export async function deleteAccount(): Promise<void> {
  await request('/users/me', { method: 'DELETE' })
  clearToken()
}
