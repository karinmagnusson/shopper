import Image from 'next/image'
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { getProduct } from '@/lib/api'
import Navbar from '@/components/Navbar'
import { ArrowLeftIcon, ArrowTopRightOnSquareIcon } from '@heroicons/react/24/outline'
import { StarIcon } from '@heroicons/react/24/solid'

interface ProductPageProps {
  params: { id: string }
}

export default async function ProductPage({ params }: ProductPageProps) {
  let product
  try {
    product = await getProduct(params.id)
  } catch {
    notFound()
  }

  const currencySymbol =
    product.currency === 'USD' ? '$' : product.currency === 'EUR' ? '€' : '£'

  return (
    <div className="min-h-screen bg-white">
      <Navbar />

      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {/* Back */}
        <Link
          href="/recommendations"
          className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-900 mb-8 transition-colors"
        >
          <ArrowLeftIcon className="w-4 h-4" />
          Back to recommendations
        </Link>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
          {/* Image */}
          <div className="relative aspect-[3/4] rounded-3xl overflow-hidden bg-gray-100">
            <Image
              src={product.imageUrl}
              alt={product.title}
              fill
              sizes="(max-width: 768px) 100vw, 50vw"
              className="object-cover"
              priority
            />
            {!product.inStock && (
              <div className="absolute inset-0 bg-white/60 flex items-center justify-center">
                <span className="text-base font-semibold text-gray-600 bg-white px-4 py-2 rounded-full shadow">
                  Out of stock
                </span>
              </div>
            )}
          </div>

          {/* Details */}
          <div className="flex flex-col">
            {product.brand && (
              <p className="text-sm font-bold text-pinterest-red uppercase tracking-widest mb-1">
                {product.brand}
              </p>
            )}
            <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900 leading-tight">
              {product.title}
            </h1>

            {/* Rating */}
            {product.rating !== undefined && (
              <div className="flex items-center gap-2 mt-3">
                <div className="flex items-center gap-0.5">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <StarIcon
                      key={i}
                      className={`w-4 h-4 ${
                        i < Math.round(product.rating!)
                          ? 'text-yellow-400'
                          : 'text-gray-200'
                      }`}
                    />
                  ))}
                </div>
                <span className="text-sm text-gray-500">
                  {product.rating.toFixed(1)}
                  {product.reviewCount !== undefined && (
                    <span> ({product.reviewCount.toLocaleString()} reviews)</span>
                  )}
                </span>
              </div>
            )}

            {/* Price */}
            <div className="mt-4">
              <span className="text-3xl font-black text-gray-900">
                {currencySymbol}{product.price.toFixed(2)}
              </span>
              <span className="ml-2 text-sm text-gray-400">{product.retailer}</span>
            </div>

            {/* Description */}
            {product.description && (
              <p className="mt-4 text-gray-600 text-sm leading-relaxed">
                {product.description}
              </p>
            )}

            {/* Category */}
            <div className="mt-4 flex items-center gap-2">
              <span className="text-xs font-semibold text-gray-400 uppercase">Category</span>
              <span className="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded-full capitalize">
                {product.category}
              </span>
            </div>

            {/* Colors */}
            {product.colors.length > 0 && (
              <div className="mt-3 flex items-center gap-2 flex-wrap">
                <span className="text-xs font-semibold text-gray-400 uppercase">Colors</span>
                {product.colors.map((color) => (
                  <span
                    key={color}
                    className="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded-full capitalize"
                  >
                    {color}
                  </span>
                ))}
              </div>
            )}

            {/* Sizes */}
            {product.sizes && product.sizes.length > 0 && (
              <div className="mt-4">
                <p className="text-xs font-semibold text-gray-400 uppercase mb-2">
                  Available sizes
                </p>
                <div className="flex flex-wrap gap-2">
                  {product.sizes.map((size) => (
                    <span
                      key={size}
                      className="text-xs border border-gray-200 text-gray-700 px-3 py-1 rounded-lg"
                    >
                      {size}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* CTA */}
            <div className="mt-8 space-y-3">
              <a
                href={product.productUrl}
                target="_blank"
                rel="noopener noreferrer"
                className={`flex items-center justify-center gap-2 w-full py-4 rounded-2xl font-bold text-base transition-colors ${
                  product.inStock
                    ? 'bg-pinterest-red hover:bg-red-700 text-white shadow-lg shadow-red-100'
                    : 'bg-gray-200 text-gray-400 cursor-not-allowed pointer-events-none'
                }`}
              >
                Shop Now on {product.retailer}
                <ArrowTopRightOnSquareIcon className="w-4 h-4" />
              </a>
              <Link
                href="/recommendations"
                className="flex items-center justify-center w-full py-3 rounded-2xl border-2 border-gray-200 text-gray-700 font-semibold text-sm hover:border-gray-300 transition-colors"
              >
                Back to all recommendations
              </Link>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
