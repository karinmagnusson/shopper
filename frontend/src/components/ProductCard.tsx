import Image from 'next/image'
import Link from 'next/link'
import type { Product } from '@/types'
import clsx from 'clsx'

interface ProductCardProps {
  product: Product
  matchScore?: number
}

export default function ProductCard({ product, matchScore }: ProductCardProps) {
  return (
    <div className="group bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-md transition-shadow border border-gray-100 flex flex-col">
      {/* Image */}
      <div className="relative w-full aspect-[3/4] bg-gray-100 overflow-hidden">
        <Image
          src={product.imageUrl}
          alt={product.title}
          fill
          sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 25vw"
          className="object-cover group-hover:scale-105 transition-transform duration-300"
        />
        {/* Match badge */}
        {matchScore !== undefined && (
          <div className="absolute top-2 left-2 bg-pinterest-red text-white text-xs font-semibold px-2 py-1 rounded-full">
            {Math.round(matchScore * 100)}% match
          </div>
        )}
        {/* Out of stock overlay */}
        {!product.inStock && (
          <div className="absolute inset-0 bg-white/60 flex items-center justify-center">
            <span className="text-sm font-semibold text-gray-600 bg-white px-3 py-1 rounded-full shadow">
              Out of stock
            </span>
          </div>
        )}
      </div>

      {/* Details */}
      <div className="p-3 flex flex-col gap-1 flex-1">
        {/* Brand */}
        {product.brand && (
          <p className="text-xs font-semibold text-pinterest-red uppercase tracking-wide truncate">
            {product.brand}
          </p>
        )}

        {/* Title */}
        <h3 className="text-sm font-medium text-gray-900 line-clamp-2 leading-snug">
          {product.title}
        </h3>

        {/* Price row */}
        <div className="flex items-center justify-between mt-auto pt-2">
          <span className="text-base font-bold text-gray-900">
            {product.currency === 'USD' ? '$' : product.currency === 'EUR' ? '€' : '£'}
            {product.price.toFixed(2)}
          </span>
          <span className="text-xs text-gray-400">{product.retailer}</span>
        </div>

        {/* Rating */}
        {product.rating !== undefined && (
          <div className="flex items-center gap-1 text-xs text-gray-500">
            <span className="text-yellow-400">★</span>
            <span>{product.rating.toFixed(1)}</span>
            {product.reviewCount !== undefined && (
              <span className="text-gray-400">({product.reviewCount})</span>
            )}
          </div>
        )}

        {/* Colors */}
        {product.colors.length > 0 && (
          <div className="flex gap-1 flex-wrap">
            {product.colors.slice(0, 5).map((color) => (
              <span
                key={color}
                className="text-xs px-2 py-0.5 bg-gray-100 rounded-full text-gray-600 capitalize"
              >
                {color}
              </span>
            ))}
          </div>
        )}

        {/* CTA */}
        <a
          href={product.productUrl}
          target="_blank"
          rel="noopener noreferrer"
          className={clsx(
            'mt-2 w-full text-center text-sm font-semibold py-2 rounded-xl transition-colors',
            product.inStock
              ? 'bg-pinterest-red hover:bg-red-700 text-white'
              : 'bg-gray-200 text-gray-400 cursor-not-allowed pointer-events-none'
          )}
        >
          Shop Now
        </a>
      </div>
    </div>
  )
}
