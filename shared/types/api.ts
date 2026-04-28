/** Shared API type definitions used by both frontend and backend. */

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

export interface AuthUrlResponse {
  auth_url: string
  state: string
}

export interface TokenResponse {
  access_token: string
  token_type: 'bearer'
}

// ---------------------------------------------------------------------------
// Users
// ---------------------------------------------------------------------------

export interface UserProfile {
  id: string
  pinterest_id: string
  email: string | null
  style_preferences: StylePreferences
  created_at: string
  last_sync: string | null
}

export interface StylePreferences {
  preferred_styles?: string[]
  preferred_colors?: string[]
  preferred_categories?: string[]
  preferred_brands?: string[]
  price_range_min?: number | null
  price_range_max?: number | null
  size?: string | null
}

// ---------------------------------------------------------------------------
// Boards
// ---------------------------------------------------------------------------

export interface Board {
  id: string
  pinterest_board_id: string
  name: string
  description: string | null
  cover_image_url: string | null
  pin_count: number
  last_synced: string | null
}

export interface BoardsResponse {
  boards: Board[]
  total: number
}

export interface SyncBoardsResponse {
  synced: number
  message: string
}

export interface PinAnalysis {
  colors: string[]
  clothing_type: string | null
  styles: string[]
  detected_brands: string[]
  labels: string[]
  confidence: number
}

export interface Pin {
  id: string
  pinterest_pin_id: string
  image_url: string | null
  description: string | null
  link: string | null
  analyzed_at: string | null
  analysis_data: PinAnalysis | null
}

export interface PinsResponse {
  pins: Pin[]
  total: number
}

export interface BoardAnalysisResponse {
  board_id: string
  pins_processed: number
  pins_analyzed: number
  analyses: PinAnalysis[]
}

// ---------------------------------------------------------------------------
// Products
// ---------------------------------------------------------------------------

export interface Product {
  id: string
  retailer_id: string
  retailer_name: string
  title: string
  price: number | null
  currency: string
  image_url: string | null
  product_url: string
  affiliate_url: string | null
  category: string | null
  brand: string | null
  colors: string[]
  sizes: string[]
  relevance_score?: number
}

export interface RecommendationsResponse {
  recommendations: Product[]
  total: number
  offset: number
  limit: number
}

export interface SearchResponse {
  products: Product[]
  total: number
  offset: number
  limit: number
}

// ---------------------------------------------------------------------------
// Interactions
// ---------------------------------------------------------------------------

export interface TrackClickRequest {
  product_id: string
  interaction_type: 'click' | 'save' | 'purchase'
}

export interface TrackClickResponse {
  status: 'tracked'
}

// ---------------------------------------------------------------------------
// Error
// ---------------------------------------------------------------------------

export interface ApiError {
  detail: string
}
