export interface User {
  id: string
  email: string
  name: string
  image?: string
  pinterestId?: string
  pinterestAccessToken?: string
  createdAt: string
  updatedAt: string
}

export interface Board {
  id: string
  name: string
  description?: string
  pinCount: number
  followerCount: number
  imageCoverUrl?: string
  privacy: 'PUBLIC' | 'PROTECTED' | 'SECRET'
  owner: {
    username: string
  }
}

export interface Pin {
  id: string
  title?: string
  description?: string
  link?: string
  imageUrl: string
  boardId: string
  dominantColor?: string
  createdAt: string
}

export interface Product {
  id: string
  title: string
  description?: string
  price: number
  currency: string
  imageUrl: string
  productUrl: string
  retailer: string
  brand?: string
  category: string
  colors: string[]
  sizes?: string[]
  inStock: boolean
  rating?: number
  reviewCount?: number
}

export interface Recommendation {
  id: string
  product: Product
  score: number
  matchedPinId?: string
  matchedBoardId?: string
  reasons: string[]
  createdAt: string
}

export interface AnalysisJob {
  id: string
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED'
  progress: number
  boardIds: string[]
  totalPins: number
  processedPins: number
  message?: string
  createdAt: string
  completedAt?: string
}

export interface FilterOptions {
  minPrice?: number
  maxPrice?: number
  colors?: string[]
  categories?: string[]
  brands?: string[]
  retailers?: string[]
  inStock?: boolean
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
  hasMore: boolean
}

export interface ApiError {
  message: string
  statusCode: number
  details?: Record<string, unknown>
}
