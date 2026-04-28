'use client'

import { useState } from 'react'
import type { ProductFilters } from '@/types/products'
import { FASHION_CATEGORIES, COLOR_OPTIONS } from '@/types/products'
import Button from '@/components/ui/Button'
import { SlidersHorizontal, X } from 'lucide-react'

interface FilterPanelProps {
  filters: ProductFilters
  onChange: (filters: ProductFilters) => void
}

export default function FilterPanel({ filters, onChange }: FilterPanelProps) {
  const [local, setLocal] = useState<ProductFilters>(filters)

  function update<K extends keyof ProductFilters>(key: K, value: ProductFilters[K]) {
    setLocal((prev) => ({ ...prev, [key]: value }))
  }

  function toggleColor(color: string) {
    const current = local.colors ?? []
    const next = current.includes(color)
      ? current.filter((c) => c !== color)
      : [...current, color]
    update('colors', next.length > 0 ? next : undefined)
  }

  function handleApply() {
    onChange(local)
  }

  function handleReset() {
    const empty: ProductFilters = {}
    setLocal(empty)
    onChange(empty)
  }

  const hasFilters =
    local.price_min != null ||
    local.price_max != null ||
    local.category != null ||
    (local.colors?.length ?? 0) > 0

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-gray-900 flex items-center gap-2">
          <SlidersHorizontal size={16} className="text-rose-500" />
          Filters
        </h3>
        {hasFilters && (
          <button
            type="button"
            onClick={handleReset}
            className="text-xs text-gray-400 hover:text-gray-600 flex items-center gap-1"
          >
            <X size={12} /> Clear all
          </button>
        )}
      </div>

      {/* Price range */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Price range</label>
        <div className="flex gap-2 items-center">
          <input
            type="number"
            placeholder="Min"
            min={0}
            value={local.price_min ?? ''}
            onChange={(e) => update('price_min', e.target.value ? Number(e.target.value) : undefined)}
            className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-300"
          />
          <span className="text-gray-400 text-sm">–</span>
          <input
            type="number"
            placeholder="Max"
            min={0}
            value={local.price_max ?? ''}
            onChange={(e) => update('price_max', e.target.value ? Number(e.target.value) : undefined)}
            className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-300"
          />
        </div>
      </div>

      {/* Category */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
        <select
          value={local.category ?? ''}
          onChange={(e) => update('category', e.target.value || undefined)}
          className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-300 bg-white"
        >
          <option value="">All categories</option>
          {FASHION_CATEGORIES.map((cat) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>
      </div>

      {/* Colors */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">Colors</label>
        <div className="flex flex-wrap gap-2">
          {COLOR_OPTIONS.map(({ label, value, hex }) => {
            const isSelected = (local.colors ?? []).includes(value)
            return (
              <button
                key={value}
                type="button"
                title={label}
                onClick={() => toggleColor(value)}
                className={`w-7 h-7 rounded-full border-2 transition-transform hover:scale-110 ${
                  isSelected ? 'border-rose-500 ring-2 ring-rose-200' : 'border-transparent'
                }`}
                style={{ backgroundColor: hex }}
                aria-label={label}
                aria-pressed={isSelected}
              />
            )
          })}
        </div>
        {(local.colors?.length ?? 0) > 0 && (
          <p className="text-xs text-gray-400 mt-2">
            {local.colors?.join(', ')}
          </p>
        )}
      </div>

      <Button onClick={handleApply} className="w-full">
        Apply filters
      </Button>
    </div>
  )
}
