export interface PinterestBoard {
  id: string
  pinterest_board_id: string
  name: string
  description: string | null
  cover_image_url: string | null
  pin_count: number
  last_synced: string | null
}

export interface PinterestPin {
  id: string
  pinterest_pin_id: string
  image_url: string | null
  description: string | null
  link: string | null
  analyzed_at: string | null
  analysis_data: PinAnalysis | null
}

export interface PinAnalysis {
  colors: string[]
  clothing_type: string | null
  styles: string[]
  detected_brands: string[]
  labels: string[]
  confidence: number
}

export interface BoardsResponse {
  boards: PinterestBoard[]
  total: number
}

export interface PinsResponse {
  pins: PinterestPin[]
  total: number
}

export interface BoardAnalysisResponse {
  board_id: string
  pins_processed: number
  pins_analyzed: number
  analyses: PinAnalysis[]
}
