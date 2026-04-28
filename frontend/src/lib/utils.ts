import { clsx, type ClassValue } from 'clsx'

/** Merge Tailwind class names conditionally. */
export function cn(...inputs: ClassValue[]): string {
  return clsx(inputs)
}

/** Format a price with currency symbol. */
export function formatPrice(price: number | null, currency = 'USD'): string {
  if (price === null || price === undefined) return 'Price unavailable'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(price)
}

/** Truncate a string to a maximum length with ellipsis. */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return `${text.slice(0, maxLength - 3)}...`
}

/** Return initials from a display name (max 2 chars). */
export function initials(name: string): string {
  return name
    .split(' ')
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? '')
    .join('')
}
