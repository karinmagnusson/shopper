'use client'

import { useState, useCallback } from 'react'
import { useSession, signIn } from 'next-auth/react'
import { useQuery } from 'react-query'
import Navbar from '@/components/Navbar'
import ProductCard from '@/components/ProductCard'
import FilterSidebar from '@/components/FilterSidebar'
import LoadingSpinner from '@/components/LoadingSpinner'
import { getRecommendations } from '@/lib/api'
import type { FilterOptions, Recommendation } from '@/types'
import { AdjustmentsHorizontalIcon } from '@heroicons/react/24/outline'

const PAGE_SIZE = 24

export default function RecommendationsPage() {
  const { data: session, status: sessionStatus } = useSession()
  const [filters, setFilters] = useState<FilterOptions>({})
  const [page, setPage] = useState(1)
  const [allItems, setAllItems] = useState<Recommendation[]>([])

  const { data, isLoading, isFetching, error } = useQuery(
    ['recommendations', filters, page],
    () => getRecommendations(filters, page, PAGE_SIZE),
    {
      enabled: sessionStatus === 'authenticated',
      keepPreviousData: true,
      onSuccess: (result) => {
        if (page === 1) {
          setAllItems(result.items)
        } else {
          setAllItems((prev) => [...prev, ...result.items])
        }
      },
    }
  )

  const handleFilterChange = useCallback((newFilters: FilterOptions) => {
    setFilters(newFilters)
    setPage(1)
    setAllItems([])
  }, [])

  const loadMore = () => setPage((p) => p + 1)

  if (sessionStatus === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (sessionStatus === 'unauthenticated') {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4 p-8 text-center">
        <h2 className="text-xl font-bold text-gray-900">Sign in to see recommendations</h2>
        <button
          onClick={() => signIn('pinterest')}
          className="px-6 py-3 bg-pinterest-red text-white font-semibold rounded-xl"
        >
          Connect Pinterest
        </button>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900">
            Your Recommendations
          </h1>
          <p className="mt-1 text-gray-500 text-sm">
            Products matched to your Pinterest style.{' '}
            {data && (
              <span className="font-medium text-gray-700">
                {data.total.toLocaleString()} results
              </span>
            )}
          </p>
        </div>

        <div className="flex gap-8 items-start">
          {/* Filter sidebar */}
          <FilterSidebar filters={filters} onChange={handleFilterChange} />

          {/* Product grid */}
          <div className="flex-1 min-w-0">
            {isLoading && page === 1 ? (
              <div className="flex items-center justify-center py-24">
                <LoadingSpinner size="lg" />
              </div>
            ) : error ? (
              <div className="text-center py-24">
                <p className="text-gray-500 mb-2">Failed to load recommendations.</p>
                <p className="text-sm text-gray-400">Make sure you have analyzed some boards first.</p>
              </div>
            ) : allItems.length === 0 ? (
              <div className="text-center py-24">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <AdjustmentsHorizontalIcon className="w-8 h-8 text-gray-300" />
                </div>
                <p className="text-gray-500 font-medium">No recommendations yet</p>
                <p className="text-sm text-gray-400 mt-1">
                  Go to <a href="/dashboard" className="text-pinterest-red hover:underline">My Boards</a> and analyze some boards first.
                </p>
              </div>
            ) : (
              <>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                  {allItems.map((rec) => (
                    <ProductCard
                      key={rec.id}
                      product={rec.product}
                      matchScore={rec.score}
                    />
                  ))}
                </div>

                {/* Load more */}
                {data?.hasMore && (
                  <div className="flex justify-center mt-10">
                    <button
                      onClick={loadMore}
                      disabled={isFetching}
                      className="flex items-center gap-2 px-8 py-3 bg-white border-2 border-gray-200 hover:border-pinterest-red text-gray-700 font-semibold rounded-xl transition-colors disabled:opacity-50"
                    >
                      {isFetching ? (
                        <>
                          <LoadingSpinner size="sm" />
                          Loading…
                        </>
                      ) : (
                        'Load more'
                      )}
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
