import type { PinterestPin } from '@/types/pinterest'
import Image from 'next/image'
import { Tag } from 'lucide-react'

interface PinCardProps {
  pin: PinterestPin
}

export default function PinCard({ pin }: PinCardProps) {
  const analysis = pin.analysis_data

  return (
    <div className="rounded-xl overflow-hidden bg-white shadow-sm border border-gray-100">
      <div className="relative aspect-square bg-gray-100">
        {pin.image_url ? (
          <Image
            src={pin.image_url}
            alt={pin.description ?? 'Pinterest pin'}
            fill
            sizes="(max-width: 640px) 50vw, 33vw"
            className="object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <Tag size={28} className="text-gray-300" />
          </div>
        )}
      </div>

      {analysis && (
        <div className="p-3">
          {analysis.clothing_type && (
            <span className="inline-block px-2 py-0.5 rounded-full bg-rose-50 text-rose-600 text-xs font-medium mb-1.5 capitalize">
              {analysis.clothing_type}
            </span>
          )}
          {analysis.colors.length > 0 && (
            <div className="flex gap-1 flex-wrap">
              {analysis.colors.map((color) => (
                <span key={color} className="text-xs text-gray-500 capitalize">
                  {color}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
