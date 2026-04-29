'use client'

import { useEffect, Suspense } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'
import LoadingSpinner from '@/components/LoadingSpinner'

function CallbackContent() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const { status } = useSession()

  const error = searchParams.get('error')

  useEffect(() => {
    if (error) {
      router.replace(`/?error=${encodeURIComponent(error)}`)
      return
    }
    if (status === 'authenticated') {
      router.replace('/dashboard')
    } else if (status === 'unauthenticated') {
      router.replace('/')
    }
  }, [status, error, router])

  if (error) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4 p-8">
        <div className="text-red-500 text-lg font-semibold">Authentication failed</div>
        <p className="text-gray-500 text-sm">{error}</p>
        <button
          onClick={() => router.push('/')}
          className="mt-4 px-6 py-2 bg-pinterest-red text-white font-semibold rounded-xl"
        >
          Back to home
        </button>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-4">
      <LoadingSpinner size="lg" />
      <p className="text-gray-500 text-sm">Connecting your Pinterest account…</p>
    </div>
  )
}

export default function PinterestCallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center">
          <LoadingSpinner size="lg" />
        </div>
      }
    >
      <CallbackContent />
    </Suspense>
  )
}
