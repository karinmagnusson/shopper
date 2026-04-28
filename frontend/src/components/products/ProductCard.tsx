'use client'

import type { Product } from '@/types/products'
import { formatPrice, truncate } from '@/lib/utils'
import { trackClick } from '@/lib/api'
import Image from 'next/image'
import { Heart, ShoppingBag, Tag } from 'lucide-react'
import { useState } from 'react'
import { cn } from '@/lib/utils'

interface ProductCardProps {
  product: Product
}

export default function ProductCard({ product }: ProductCardProps) {
  const [saved, setSaved] = useState(false)
  const [savingClick, setSavingClick] = useState(false)

  async function handleShopNow() {
    setSavingClick(true)
    try {
      await trackClick(product.id, 'click')
    } catch {
      // Non-critical; ignore tracking errors
    } finally {
      setSavingClick(false)
    }
    const url = product.affiliate_url ?? product.product_url
    window.open(url, '_blank', 'noopener,noreferrer')
  }

  async function handleSave() {
    setSaved((v) => !v)
    try {
      await trackClick(product.id, 'save')
    } catch {
      // ignore
    }
  }

  return (
    <div className="group relative flex flex-col rounded-2xl bg-white border border-gray-100 shadow-sm hover:shadow-md transition-shadow overflow-hidden">
      {/* Image */}
      <div className="relative aspect-[3/4] bg-gray-50 overflow-hidden">
        {product.image_url ? (
          <Image
            src={product.image_url}
            alt={product.title}
            fill
            sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 25vw"
            className="object-cover group-hover:scale-105 transition-transform duration-300"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gray-100">
            <Tag size={36} className="text-gray-300" />
          </div>
        )}

        {/* Save button */}
        <button
          type="button"
          onClick={handleSave}
          className="absolute top-3 right-3 w-8 h-8 rounded-full bg-white/90 flex items-center justify-center shadow transition-transform hover:scale-110"
          aria-label={saved ? 'Unsave product' : 'Save product'}
        >
          <Heart
            size={16}
            className={cn('transition-colors', saved ? 'fill-rose-500 text-rose-500' : 'text-gray-400')}
          />
        </button>

        {/* Relevance badge */}
        {product.relevance_score !== undefined && product.relevance_score > 0 && (
          <div className="absolute bottom-3 left-3 px-2 py-0.5 rounded-full bg-black/60 text-white text-xs">
            {Math.round(product.relevance_score * 100)}% match
          </div>
        )}
      </div>

      {/* Details */}
      <div className="p-4 flex flex-col flex-1">
        {product.brand && (
          <p className="text-xs font-medium text-rose-500 uppercase tracking-wide mb-0.5">
            {product.brand}
          </p>
        )}
        <p className="text-sm font-semibold text-gray-900 leading-snug mb-1">
          {truncate(product.title, 60)}
        </p>
        <p className="text-base font-bold text-gray-900 mt-auto mb-3">
          {formatPrice(product.price, product.currency)}
        </p>

        <button
          type="button"
          onClick={handleShopNow}
          disabled={savingClick}
          className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-gray-900 text-white text-sm font-medium hover:bg-gray-700 transition-colors disabled:opacity-60"
        >
          <ShoppingBag size={15} />
          Shop now
        </button>
      </div>
    </div>
  )
}
