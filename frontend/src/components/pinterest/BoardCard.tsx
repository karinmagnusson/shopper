import type { PinterestBoard } from '@/types/pinterest'
import { cn } from '@/lib/utils'
import { CheckCircle2, LayoutGrid } from 'lucide-react'
import Image from 'next/image'

interface BoardCardProps {
  board: PinterestBoard
  selected: boolean
  onToggle: () => void
}

export default function BoardCard({ board, selected, onToggle }: BoardCardProps) {
  return (
    <button
      type="button"
      onClick={onToggle}
      className={cn(
        'relative flex flex-col rounded-2xl border-2 overflow-hidden text-left transition-all duration-150 focus:outline-none focus-visible:ring-2 focus-visible:ring-rose-400',
        selected
          ? 'border-rose-500 shadow-md shadow-rose-100'
          : 'border-transparent bg-white shadow-sm hover:shadow-md hover:border-gray-200'
      )}
    >
      {/* Thumbnail */}
      <div className="relative w-full aspect-square bg-gray-100">
        {board.cover_image_url ? (
          <Image
            src={board.cover_image_url}
            alt={board.name}
            fill
            sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 25vw"
            className="object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-rose-50">
            <LayoutGrid size={36} className="text-rose-200" />
          </div>
        )}

        {/* Selected overlay */}
        {selected && (
          <div className="absolute inset-0 bg-rose-500/10 flex items-center justify-center">
            <CheckCircle2 size={40} className="text-rose-500 drop-shadow" />
          </div>
        )}
      </div>

      {/* Info */}
      <div className="p-3 bg-white">
        <p className="font-semibold text-gray-900 truncate">{board.name}</p>
        <p className="text-xs text-gray-400 mt-0.5">{board.pin_count} pins</p>
      </div>
    </button>
  )
}
