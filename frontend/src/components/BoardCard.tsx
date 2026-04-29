import Image from 'next/image'
import type { Board } from '@/types'
import clsx from 'clsx'
import { CheckCircleIcon } from '@heroicons/react/24/solid'

interface BoardCardProps {
  board: Board
  selected: boolean
  onToggle: (id: string) => void
}

export default function BoardCard({ board, selected, onToggle }: BoardCardProps) {
  return (
    <button
      onClick={() => onToggle(board.id)}
      className={clsx(
        'group relative rounded-2xl overflow-hidden border-2 transition-all text-left w-full',
        selected
          ? 'border-pinterest-red shadow-md shadow-red-100'
          : 'border-transparent hover:border-gray-200 shadow-sm hover:shadow-md'
      )}
      aria-pressed={selected}
    >
      {/* Cover image */}
      <div className="relative aspect-square bg-gray-200">
        {board.imageCoverUrl ? (
          <Image
            src={board.imageCoverUrl}
            alt={board.name}
            fill
            sizes="(max-width: 640px) 50vw, 33vw"
            className="object-cover group-hover:scale-105 transition-transform duration-300"
          />
        ) : (
          <div className="absolute inset-0 bg-gradient-to-br from-pink-100 to-red-100 flex items-center justify-center">
            <svg
              className="w-12 h-12 text-pinterest-red/30"
              viewBox="0 0 24 24"
              fill="currentColor"
            >
              <path d="M12 0C5.373 0 0 5.373 0 12c0 5.084 3.163 9.426 7.627 11.174-.105-.949-.2-2.405.042-3.441.218-.937 1.407-5.965 1.407-5.965s-.359-.719-.359-1.782c0-1.668.967-2.914 2.171-2.914 1.023 0 1.518.769 1.518 1.69 0 1.029-.655 2.568-.994 3.995-.283 1.194.599 2.169 1.777 2.169 2.133 0 3.772-2.249 3.772-5.495 0-2.873-2.064-4.882-5.012-4.882-3.414 0-5.418 2.561-5.418 5.207 0 1.031.397 2.138.893 2.738a.36.36 0 0 1 .083.345l-.333 1.36c-.053.22-.174.267-.402.161-1.499-.698-2.436-2.889-2.436-4.649 0-3.785 2.75-7.262 7.929-7.262 4.163 0 7.398 2.967 7.398 6.931 0 4.136-2.607 7.464-6.227 7.464-1.216 0-2.359-.632-2.75-1.378l-.748 2.853c-.271 1.043-1.002 2.35-1.492 3.146C9.57 23.812 10.763 24 12 24c6.627 0 12-5.373 12-12S18.627 0 12 0z" />
            </svg>
          </div>
        )}

        {/* Selected overlay */}
        {selected && (
          <div className="absolute inset-0 bg-pinterest-red/20" />
        )}

        {/* Check icon */}
        <div
          className={clsx(
            'absolute top-2 right-2 transition-opacity',
            selected ? 'opacity-100' : 'opacity-0 group-hover:opacity-30'
          )}
        >
          <CheckCircleIcon className="w-6 h-6 text-pinterest-red drop-shadow" />
        </div>

        {/* Privacy badge */}
        {board.privacy !== 'PUBLIC' && (
          <div className="absolute top-2 left-2 bg-black/50 text-white text-xs px-2 py-0.5 rounded-full">
            {board.privacy === 'SECRET' ? '🔒 Secret' : '🔗 Protected'}
          </div>
        )}
      </div>

      {/* Meta */}
      <div className="bg-white p-3">
        <p className="text-sm font-semibold text-gray-900 truncate">{board.name}</p>
        <p className="text-xs text-gray-400 mt-0.5">
          {board.pinCount.toLocaleString()} pins
        </p>
        {board.description && (
          <p className="text-xs text-gray-500 mt-1 line-clamp-2">{board.description}</p>
        )}
      </div>
    </button>
  )
}
