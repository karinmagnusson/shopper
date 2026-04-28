'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { clearToken, getToken, logout } from '@/lib/api'
import { ShoppingBag, LogOut } from 'lucide-react'
import Button from '@/components/ui/Button'
import { useEffect, useState } from 'react'

export default function Header() {
  const router = useRouter()
  const [isLoggedIn, setIsLoggedIn] = useState(false)

  useEffect(() => {
    setIsLoggedIn(!!getToken())
  }, [])

  async function handleLogout() {
    try {
      await logout()
    } catch {
      clearToken()
    }
    setIsLoggedIn(false)
    router.push('/')
  }

  return (
    <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-sm border-b border-gray-100">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 font-bold text-gray-900 hover:text-rose-600 transition-colors">
          <ShoppingBag size={22} className="text-rose-500" />
          <span className="text-lg">Shopper</span>
        </Link>

        <nav className="flex items-center gap-4">
          {isLoggedIn ? (
            <>
              <Link href="/boards" className="text-sm text-gray-600 hover:text-gray-900 transition-colors hidden sm:block">
                Boards
              </Link>
              <Link href="/recommendations" className="text-sm text-gray-600 hover:text-gray-900 transition-colors hidden sm:block">
                Recommendations
              </Link>
              <Button variant="ghost" size="sm" onClick={handleLogout} className="gap-1.5">
                <LogOut size={15} />
                Log out
              </Button>
            </>
          ) : (
            <Link href="/">
              <Button size="sm">Connect Pinterest</Button>
            </Link>
          )}
        </nav>
      </div>
    </header>
  )
}
