import { cn } from '@/lib/utils'
import type { HTMLAttributes } from 'react'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  hover?: boolean
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

const paddingClasses = {
  none: '',
  sm: 'p-3',
  md: 'p-5',
  lg: 'p-7',
}

export default function Card({
  hover = false,
  padding = 'md',
  className,
  children,
  ...props
}: CardProps) {
  return (
    <div
      className={cn(
        'bg-white rounded-2xl border border-gray-100 shadow-sm',
        hover && 'transition-shadow hover:shadow-md cursor-pointer',
        paddingClasses[padding],
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}
