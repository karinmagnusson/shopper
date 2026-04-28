'use client'

import { generateAuthUrl } from '@/lib/pinterest'
import { getToken } from '@/lib/api'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Header from '@/components/layout/Header'
import Footer from '@/components/layout/Footer'
import Button from '@/components/ui/Button'
import { Sparkles, ShoppingBag, Heart, Zap } from 'lucide-react'

const FEATURES = [
  {
    icon: Heart,
    title: 'Powered by your taste',
    description:
      'We analyse the fashion pins on your Pinterest boards to understand your unique style.',
  },
  {
    icon: Sparkles,
    title: 'AI-matched products',
    description:
      'Our AI compares colours, styles, and clothing types to surface products you will love.',
  },
  {
    icon: ShoppingBag,
    title: 'Shop in one click',
    description:
      'Every recommendation links directly to the retailer so you can buy instantly.',
  },
]

const STEPS = [
  { step: '01', title: 'Connect Pinterest', description: 'Log in with your Pinterest account securely.' },
  { step: '02', title: 'Choose boards', description: 'Pick the fashion boards that best reflect your style.' },
  { step: '03', title: 'AI analysis', description: 'We scan your pins and detect colours, styles, and categories.' },
  { step: '04', title: 'Shop your style', description: 'Browse shoppable products matched to your aesthetic.' },
]

export default function HomePage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (getToken()) router.replace('/boards')
  }, [router])

  async function handleConnect() {
    setLoading(true)
    try {
      const url = await generateAuthUrl()
      window.location.href = url
    } catch (err) {
      console.error('Failed to start Pinterest auth:', err)
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col min-h-screen">
      <Header />

      {/* Hero */}
      <section className="relative flex flex-col items-center justify-center text-center px-4 py-28 bg-gradient-to-br from-rose-50 via-white to-pink-50 overflow-hidden">
        <div className="absolute inset-0 pointer-events-none" aria-hidden>
          <div className="absolute -top-32 -left-32 w-96 h-96 bg-pink-200 rounded-full opacity-20 blur-3xl" />
          <div className="absolute -bottom-32 -right-32 w-96 h-96 bg-rose-200 rounded-full opacity-20 blur-3xl" />
        </div>

        <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-rose-100 text-rose-700 text-sm font-medium mb-6">
          <Zap size={14} /> AI-powered fashion discovery
        </span>

        <h1 className="text-5xl sm:text-6xl font-extrabold text-gray-900 leading-tight max-w-3xl mb-6">
          Discover Fashion{' '}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-rose-500 to-pink-600">
            You&apos;ll Love
          </span>
        </h1>

        <p className="text-xl text-gray-600 max-w-xl mb-10">
          Connect your Pinterest account, select your favourite fashion boards, and instantly
          find shoppable products that match your style.
        </p>

        <Button
          onClick={handleConnect}
          loading={loading}
          size="lg"
          className="gap-2 shadow-lg"
        >
          <svg viewBox="0 0 24 24" className="w-5 h-5 fill-current" aria-hidden>
            <path d="M12 0C5.373 0 0 5.373 0 12c0 5.084 3.163 9.426 7.627 11.174-.105-.949-.2-2.405.042-3.441.218-.937 1.407-5.965 1.407-5.965s-.359-.719-.359-1.782c0-1.668.967-2.914 2.171-2.914 1.023 0 1.518.769 1.518 1.69 0 1.029-.655 2.568-.994 3.995-.283 1.194.599 2.169 1.777 2.169 2.133 0 3.772-2.249 3.772-5.495 0-2.873-2.064-4.882-5.012-4.882-3.414 0-5.418 2.561-5.418 5.207 0 1.031.397 2.138.893 2.738a.36.36 0 0 1 .083.345l-.333 1.36c-.053.22-.174.267-.402.161-1.499-.698-2.436-2.889-2.436-4.649 0-3.785 2.75-7.262 7.929-7.262 4.163 0 7.398 2.967 7.398 6.931 0 4.136-2.607 7.464-6.227 7.464-1.216 0-2.359-.632-2.75-1.378l-.748 2.853c-.271 1.043-1.002 2.35-1.492 3.146C9.57 23.812 10.763 24 12 24c6.627 0 12-5.373 12-12S18.627 0 12 0z" />
          </svg>
          Connect Pinterest
        </Button>

        <p className="mt-4 text-sm text-gray-400">Free to use · No card required</p>
      </section>

      {/* Features */}
      <section className="py-20 px-4 bg-white">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            Why Shopper?
          </h2>
          <div className="grid sm:grid-cols-3 gap-8">
            {FEATURES.map(({ icon: Icon, title, description }) => (
              <div
                key={title}
                className="flex flex-col items-center text-center p-8 rounded-2xl bg-gray-50 hover:bg-rose-50 transition-colors"
              >
                <div className="w-14 h-14 rounded-full bg-rose-100 flex items-center justify-center mb-5">
                  <Icon className="text-rose-600" size={26} />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
                <p className="text-gray-500 text-sm leading-relaxed">{description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-20 px-4 bg-gradient-to-b from-white to-rose-50">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-14">
            How it works
          </h2>
          <div className="grid sm:grid-cols-4 gap-6">
            {STEPS.map(({ step, title, description }) => (
              <div key={step} className="flex flex-col items-center text-center">
                <span className="text-4xl font-extrabold text-rose-200 mb-3">{step}</span>
                <h3 className="font-semibold text-gray-900 mb-1">{title}</h3>
                <p className="text-sm text-gray-500">{description}</p>
              </div>
            ))}
          </div>

          <div className="flex justify-center mt-14">
            <Button onClick={handleConnect} loading={loading} size="lg" variant="outline">
              Get started for free
            </Button>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  )
}
