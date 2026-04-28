import { ShoppingBag } from 'lucide-react'
import Link from 'next/link'

export default function Footer() {
  return (
    <footer className="bg-white border-t border-gray-100 py-10 mt-10">
      <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2 text-gray-600">
          <ShoppingBag size={18} className="text-rose-500" />
          <span className="font-semibold">Shopper</span>
          <span className="text-sm text-gray-400">— Pinterest Fashion Finder</span>
        </div>

        <nav className="flex gap-6 text-sm text-gray-500">
          <Link href="/" className="hover:text-gray-800 transition-colors">Home</Link>
          <Link href="/boards" className="hover:text-gray-800 transition-colors">Boards</Link>
          <Link href="/recommendations" className="hover:text-gray-800 transition-colors">Recommendations</Link>
        </nav>

        <p className="text-xs text-gray-400">© {new Date().getFullYear()} Shopper. All rights reserved.</p>
      </div>
    </footer>
  )
}
