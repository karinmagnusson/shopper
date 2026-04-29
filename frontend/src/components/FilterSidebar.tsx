'use client'

import { useState, useCallback } from 'react'
import type { FilterOptions } from '@/types'
import { FunnelIcon, XMarkIcon } from '@heroicons/react/24/outline'
import clsx from 'clsx'

const CATEGORIES = [
  'Tops', 'Bottoms', 'Dresses', 'Outerwear', 'Shoes',
  'Accessories', 'Bags', 'Jewelry', 'Activewear', 'Swimwear',
]

const COLORS = [
  { label: 'Black', hex: '#000000' },
  { label: 'White', hex: '#FFFFFF' },
  { label: 'Red', hex: '#EF4444' },
  { label: 'Pink', hex: '#EC4899' },
  { label: 'Blue', hex: '#3B82F6' },
  { label: 'Green', hex: '#22C55E' },
  { label: 'Yellow', hex: '#EAB308' },
  { label: 'Orange', hex: '#F97316' },
  { label: 'Purple', hex: '#A855F7' },
  { label: 'Brown', hex: '#92400E' },
  { label: 'Grey', hex: '#9CA3AF' },
  { label: 'Beige', hex: '#D4B896' },
]

const RETAILERS = ['ASOS', 'Zara', 'H&M', 'Amazon Fashion', 'Mango', 'Revolve']

interface FilterSidebarProps {
  filters: FilterOptions
  onChange: (filters: FilterOptions) => void
}

export default function FilterSidebar({ filters, onChange }: FilterSidebarProps) {
  const [mobileOpen, setMobileOpen] = useState(false)

  const update = useCallback(
    (partial: Partial<FilterOptions>) => onChange({ ...filters, ...partial }),
    [filters, onChange]
  )

  const toggleArray = <K extends keyof FilterOptions>(
    key: K,
    value: string
  ) => {
    const current = (filters[key] as string[] | undefined) ?? []
    const next = current.includes(value)
      ? current.filter((v) => v !== value)
      : [...current, value]
    update({ [key]: next.length > 0 ? next : undefined } as Partial<FilterOptions>)
  }

  const hasActiveFilters =
    filters.minPrice !== undefined ||
    filters.maxPrice !== undefined ||
    (filters.colors?.length ?? 0) > 0 ||
    (filters.categories?.length ?? 0) > 0 ||
    (filters.retailers?.length ?? 0) > 0

  const clearAll = () =>
    onChange({ inStock: filters.inStock })

  const content = (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider">
          Filters
        </h3>
        {hasActiveFilters && (
          <button
            onClick={clearAll}
            className="text-xs text-pinterest-red hover:underline"
          >
            Clear all
          </button>
        )}
      </div>

      {/* Price range */}
      <div>
        <p className="text-sm font-semibold text-gray-700 mb-3">Price range</p>
        <div className="flex items-center gap-2">
          <input
            type="number"
            min={0}
            placeholder="Min"
            value={filters.minPrice ?? ''}
            onChange={(e) =>
              update({ minPrice: e.target.value ? Number(e.target.value) : undefined })
            }
            className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-pinterest-red/30"
          />
          <span className="text-gray-400 text-sm shrink-0">—</span>
          <input
            type="number"
            min={0}
            placeholder="Max"
            value={filters.maxPrice ?? ''}
            onChange={(e) =>
              update({ maxPrice: e.target.value ? Number(e.target.value) : undefined })
            }
            className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-pinterest-red/30"
          />
        </div>
      </div>

      {/* In stock toggle */}
      <div className="flex items-center justify-between">
        <span className="text-sm font-semibold text-gray-700">In stock only</span>
        <button
          role="switch"
          aria-checked={filters.inStock ?? false}
          onClick={() => update({ inStock: !filters.inStock })}
          className={clsx(
            'relative inline-flex w-10 h-6 rounded-full transition-colors',
            filters.inStock ? 'bg-pinterest-red' : 'bg-gray-200'
          )}
        >
          <span
            className={clsx(
              'absolute top-1 w-4 h-4 rounded-full bg-white shadow transition-transform',
              filters.inStock ? 'translate-x-5' : 'translate-x-1'
            )}
          />
        </button>
      </div>

      {/* Colors */}
      <div>
        <p className="text-sm font-semibold text-gray-700 mb-3">Color</p>
        <div className="flex flex-wrap gap-2">
          {COLORS.map((color) => {
            const active = filters.colors?.includes(color.label.toLowerCase()) ?? false
            return (
              <button
                key={color.label}
                title={color.label}
                onClick={() => toggleArray('colors', color.label.toLowerCase())}
                className={clsx(
                  'w-7 h-7 rounded-full border-2 transition-transform hover:scale-110',
                  active ? 'border-pinterest-red scale-110' : 'border-gray-200',
                  color.label === 'White' && 'border-gray-300'
                )}
                style={{ backgroundColor: color.hex }}
                aria-pressed={active}
                aria-label={color.label}
              />
            )
          })}
        </div>
      </div>

      {/* Categories */}
      <div>
        <p className="text-sm font-semibold text-gray-700 mb-3">Category</p>
        <div className="flex flex-wrap gap-2">
          {CATEGORIES.map((cat) => {
            const active = filters.categories?.includes(cat) ?? false
            return (
              <button
                key={cat}
                onClick={() => toggleArray('categories', cat)}
                className={clsx(
                  'text-xs px-3 py-1.5 rounded-full border transition-colors',
                  active
                    ? 'bg-pinterest-red border-pinterest-red text-white'
                    : 'border-gray-200 text-gray-600 hover:border-pinterest-red/40'
                )}
              >
                {cat}
              </button>
            )
          })}
        </div>
      </div>

      {/* Retailers */}
      <div>
        <p className="text-sm font-semibold text-gray-700 mb-3">Retailer</p>
        <div className="space-y-2">
          {RETAILERS.map((retailer) => {
            const active = filters.retailers?.includes(retailer) ?? false
            return (
              <label key={retailer} className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={active}
                  onChange={() => toggleArray('retailers', retailer)}
                  className="w-4 h-4 accent-pinterest-red rounded"
                />
                <span className="text-sm text-gray-700">{retailer}</span>
              </label>
            )
          })}
        </div>
      </div>
    </div>
  )

  return (
    <>
      {/* Mobile toggle button */}
      <button
        onClick={() => setMobileOpen(true)}
        className="lg:hidden flex items-center gap-2 px-4 py-2 border border-gray-200 rounded-xl text-sm font-medium text-gray-700 hover:border-pinterest-red transition-colors"
      >
        <FunnelIcon className="w-4 h-4" />
        Filters
        {hasActiveFilters && (
          <span className="bg-pinterest-red text-white text-xs w-5 h-5 rounded-full flex items-center justify-center">
            {[
              filters.colors?.length,
              filters.categories?.length,
              filters.retailers?.length,
            ]
              .filter(Boolean)
              .reduce((a, b) => (a ?? 0) + (b ?? 0), 0)}
          </span>
        )}
      </button>

      {/* Mobile drawer */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div
            className="absolute inset-0 bg-black/40"
            onClick={() => setMobileOpen(false)}
          />
          <div className="absolute right-0 top-0 bottom-0 w-80 bg-white shadow-2xl overflow-y-auto p-6">
            <div className="flex items-center justify-between mb-6">
              <p className="font-bold text-gray-900">Filters</p>
              <button onClick={() => setMobileOpen(false)}>
                <XMarkIcon className="w-6 h-6 text-gray-500" />
              </button>
            </div>
            {content}
            <button
              onClick={() => setMobileOpen(false)}
              className="mt-6 w-full bg-pinterest-red text-white font-semibold py-3 rounded-xl"
            >
              Apply filters
            </button>
          </div>
        </div>
      )}

      {/* Desktop sidebar */}
      <aside className="hidden lg:block w-64 shrink-0">{content}</aside>
    </>
  )
}
