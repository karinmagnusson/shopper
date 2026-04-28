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

export interface ProductFilters {
  price_min?: number
  price_max?: number
  category?: string
  colors?: string[]
  q?: string
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

export const FASHION_CATEGORIES = [
  'Tops',
  'Bottoms',
  'Dresses',
  'Outerwear',
  'Shoes',
  'Bags',
  'Accessories',
  'Activewear',
  'Swimwear',
  'Lingerie',
] as const

export type FashionCategory = (typeof FASHION_CATEGORIES)[number]

export const COLOR_OPTIONS = [
  { label: 'Black', value: 'black', hex: '#000000' },
  { label: 'White', value: 'white', hex: '#FFFFFF' },
  { label: 'Red', value: 'red', hex: '#EF4444' },
  { label: 'Blue', value: 'blue', hex: '#3B82F6' },
  { label: 'Green', value: 'green', hex: '#22C55E' },
  { label: 'Yellow', value: 'yellow', hex: '#EAB308' },
  { label: 'Orange', value: 'orange', hex: '#F97316' },
  { label: 'Purple', value: 'purple', hex: '#A855F7' },
  { label: 'Pink', value: 'pink', hex: '#EC4899' },
  { label: 'Brown', value: 'brown', hex: '#92400E' },
  { label: 'Neutral', value: 'neutral', hex: '#D1D5DB' },
] as const
