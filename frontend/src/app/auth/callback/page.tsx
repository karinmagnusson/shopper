'use client'

import { Suspense, useEffect, useRef, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { exchangeCodeForToken, validateState } from '@/lib/pinterest'
import { setToken } from '@/lib/api'
import LoadingSpinner from '@/components/ui/LoadingSpinner'

type Status = 'loading' | 'success' | 'error'

function AuthCallbackContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [status, setStatus] = useState<Status>('loading')
  const [message, setMessage] = useState('Completing sign-in…')
  const called = useRef(false)

  useEffect(() => {
    if (called.current) return
    called.current = true

    const code = searchParams.get('code')
    const state = searchParams.get('state')
    const error = searchParams.get('error')

    if (error) {
      setStatus('error')
      setMessage(`Pinterest returned an error: ${error}`)
      return
    }

    if (!code || !state) {
      setStatus('error')
      setMessage('Missing OAuth parameters. Please try again.')
      return
    }

    if (!validateState(state)) {
      setStatus('error')
      setMessage('Security check failed (invalid state). Please try again.')
      return
    }

    exchangeCodeForToken(code, state)
      .then((token) => {
        setToken(token)
        setStatus('success')
        setMessage('Signed in! Redirecting to your boards…')
        setTimeout(() => router.replace('/boards'), 1200)
      })
      .catch((err: unknown) => {
        setStatus('error')
        setMessage((err as Error).message ?? 'Authentication failed. Please try again.')
      })
  }, [router, searchParams])

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-rose-50 to-pink-50 px-4">
      <div className="bg-white rounded-2xl shadow-lg p-10 max-w-sm w-full text-center">
        {status === 'loading' && (
          <>
            <LoadingSpinner size="lg" className="mx-auto mb-4" />
            <p className="text-gray-600">{message}</p>
          </>
        )}

        {status === 'success' && (
          <>
            <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <p className="font-semibold text-gray-800">{message}</p>
          </>
        )}

        {status === 'error' && (
          <>
            <div className="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <p className="font-semibold text-red-700 mb-4">{message}</p>
            <button
              onClick={() => router.push('/')}
              className="text-sm text-rose-600 hover:underline"
            >
              ← Back to home
            </button>
          </>
        )}
      </div>
    </div>
  )
}

export default function AuthCallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-rose-50 to-pink-50">
          <LoadingSpinner size="lg" />
        </div>
      }
    >
      <AuthCallbackContent />
    </Suspense>
  )
}
