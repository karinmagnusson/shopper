import { cn } from '@/lib/utils'

type Size = 'sm' | 'md' | 'lg'

const sizeClasses: Record<Size, string> = {
  sm: 'w-4 h-4 border-2',
  md: 'w-6 h-6 border-2',
  lg: 'w-10 h-10 border-[3px]',
}

interface LoadingSpinnerProps {
  size?: Size
  className?: string
}

export default function LoadingSpinner({ size = 'md', className }: LoadingSpinnerProps) {
  return (
    <span
      role="status"
      aria-label="Loading"
      className={cn(
        'inline-block rounded-full border-gray-300 border-t-rose-500 animate-spin',
        sizeClasses[size],
        className
      )}
    />
  )
}
