'use client'

import { useCallback, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { getRecommendations, getToken } from '@/lib/api'
import type { Product, ProductFilters } from '@/types/products'
import Header from '@/components/layout/Header'
import Footer from '@/components/layout/Footer'
import ProductGrid from '@/components/products/ProductGrid'
import FilterPanel from '@/components/products/FilterPanel'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import Button from '@/components/ui/Button'
import { SlidersHorizontal } from 'lucide-react'

const PAGE_SIZE = 20

export default function RecommendationsPage() {
  const router = useRouter()
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [loadingMore, setLoadingMore] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFilters] = useState<ProductFilters>({})
  const [offset, setOffset] = useState(0)
  const [hasMore, setHasMore] = useState(true)
  const [showFilters, setShowFilters] = useState(false)

  useEffect(() => {
    if (!getToken()) {
      router.replace('/')
      return
    }
    fetchRecommendations(filters, 0, true)
  }, [router]) // eslint-disable-line react-hooks/exhaustive-deps

  const fetchRecommendations = useCallback(
    async (currentFilters: ProductFilters, currentOffset: number, reset: boolean) => {
      if (reset) setLoading(true)
      else setLoadingMore(true)
      setError(null)

      try {
        const data = await getRecommendations({
          ...currentFilters,
          limit: PAGE_SIZE,
          offset: currentOffset,
        })
        setProducts((prev) => (reset ? data.recommendations : [...prev, ...data.recommendations]))
        setHasMore(data.recommendations.length === PAGE_SIZE)
        setOffset(currentOffset + data.recommendations.length)
      } catch (err) {
        setError((err as Error).message)
      } finally {
        setLoading(false)
        setLoadingMore(false)
      }
    },
    []
  )

  function handleFiltersChange(newFilters: ProductFilters) {
    setFilters(newFilters)
    fetchRecommendations(newFilters, 0, true)
  }

  function handleLoadMore() {
    fetchRecommendations(filters, offset, false)
  }

  return (
    <div className="flex flex-col min-h-screen">
      <Header />

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Your Style Picks</h1>
            <p className="text-gray-500 mt-1">
              Products matched to your Pinterest aesthetic.
            </p>
          </div>
          <Button
            variant="outline"
            onClick={() => setShowFilters((v) => !v)}
            className="gap-2 sm:hidden"
          >
            <SlidersHorizontal size={16} />
            Filters
          </Button>
        </div>

        <div className="flex gap-6">
          {/* Filter panel – desktop always visible, mobile toggled */}
          <aside
            className={`${showFilters ? 'block' : 'hidden'} sm:block w-64 flex-shrink-0`}
          >
            <FilterPanel filters={filters} onChange={handleFiltersChange} />
          </aside>

          {/* Products */}
          <div className="flex-1">
            {loading ? (
              <div className="flex justify-center py-24">
                <LoadingSpinner size="lg" />
              </div>
            ) : error ? (
              <div className="p-6 rounded-xl bg-red-50 border border-red-200 text-red-700">
                {error}
              </div>
            ) : products.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-24 text-center">
                <div className="text-6xl mb-4">👗</div>
                <h2 className="text-xl font-semibold text-gray-700 mb-2">No products found</h2>
                <p className="text-gray-500 mb-6">
                  Try adjusting your filters or go back to select more boards.
                </p>
                <Button variant="outline" onClick={() => router.push('/boards')}>
                  ← Back to boards
                </Button>
              </div>
            ) : (
              <>
                <ProductGrid products={products} />

                {hasMore && (
                  <div className="flex justify-center mt-10">
                    <Button variant="outline" onClick={handleLoadMore} loading={loadingMore}>
                      Load more
                    </Button>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </main>

      <Footer />
    </div>
  )
}
