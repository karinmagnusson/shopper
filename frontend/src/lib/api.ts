import axios, { AxiosError } from 'axios'
import type {
  Board,
  Pin,
  Product,
  Recommendation,
  AnalysisJob,
  FilterOptions,
  PaginatedResponse,
} from '@/types'

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30_000,
})

// Attach bearer token from session storage when present
apiClient.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = sessionStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})

// Normalize errors
apiClient.interceptors.response.use(
  (res) => res,
  (error: AxiosError) => {
    const message =
      (error.response?.data as { detail?: string })?.detail ??
      error.message ??
      'An unexpected error occurred'
    return Promise.reject(new Error(message))
  }
)

// ─── Boards ────────────────────────────────────────────────────────────────

export async function getBoards(accessToken: string): Promise<Board[]> {
  const { data } = await apiClient.get<Board[]>('/api/boards', {
    headers: { Authorization: `Bearer ${accessToken}` },
  })
  return data
}

export async function getBoardPins(
  boardId: string,
  accessToken: string
): Promise<Pin[]> {
  const { data } = await apiClient.get<Pin[]>(`/api/boards/${boardId}/pins`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  })
  return data
}

// ─── Analysis ──────────────────────────────────────────────────────────────

export async function startAnalysis(
  boardIds: string[],
  accessToken: string
): Promise<AnalysisJob> {
  const { data } = await apiClient.post<AnalysisJob>(
    '/api/analysis/start',
    { board_ids: boardIds },
    { headers: { Authorization: `Bearer ${accessToken}` } }
  )
  return data
}

export async function getAnalysisStatus(jobId: string): Promise<AnalysisJob> {
  const { data } = await apiClient.get<AnalysisJob>(`/api/analysis/${jobId}`)
  return data
}

// ─── Recommendations ───────────────────────────────────────────────────────

export async function getRecommendations(
  filters: FilterOptions = {},
  page = 1,
  pageSize = 24
): Promise<PaginatedResponse<Recommendation>> {
  const { data } = await apiClient.get<PaginatedResponse<Recommendation>>(
    '/api/recommendations',
    {
      params: {
        page,
        page_size: pageSize,
        min_price: filters.minPrice,
        max_price: filters.maxPrice,
        colors: filters.colors?.join(','),
        categories: filters.categories?.join(','),
        brands: filters.brands?.join(','),
        retailers: filters.retailers?.join(','),
        in_stock: filters.inStock,
      },
    }
  )
  return data
}

// ─── Products ──────────────────────────────────────────────────────────────

export async function getProduct(productId: string): Promise<Product> {
  const { data } = await apiClient.get<Product>(`/api/products/${productId}`)
  return data
}

export async function searchProducts(
  query: string,
  filters: FilterOptions = {},
  page = 1
): Promise<PaginatedResponse<Product>> {
  const { data } = await apiClient.get<PaginatedResponse<Product>>(
    '/api/products/search',
    {
      params: {
        q: query,
        page,
        min_price: filters.minPrice,
        max_price: filters.maxPrice,
        colors: filters.colors?.join(','),
        categories: filters.categories?.join(','),
      },
    }
  )
  return data
}

// ─── User ──────────────────────────────────────────────────────────────────

export async function deleteAccount(accessToken: string): Promise<void> {
  await apiClient.delete('/api/users/me', {
    headers: { Authorization: `Bearer ${accessToken}` },
  })
}

export async function updateStylePreferences(
  preferences: Record<string, unknown>,
  accessToken: string
): Promise<void> {
  await apiClient.put('/api/users/me/preferences', preferences, {
    headers: { Authorization: `Bearer ${accessToken}` },
  })
}
