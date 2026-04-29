'use client'

import { useState } from 'react'
import { useSession, signOut, signIn } from 'next-auth/react'
import { useMutation } from 'react-query'
import { useRouter } from 'next/navigation'
import Image from 'next/image'
import Navbar from '@/components/Navbar'
import LoadingSpinner from '@/components/LoadingSpinner'
import { deleteAccount, updateStylePreferences } from '@/lib/api'
import {
  UserCircleIcon,
  HeartIcon,
  ShieldExclamationIcon,
  ArrowRightStartOnRectangleIcon,
} from '@heroicons/react/24/outline'
import clsx from 'clsx'

const STYLE_TAGS = [
  'Minimalist', 'Boho', 'Streetwear', 'Classic', 'Romantic',
  'Sporty', 'Preppy', 'Edgy', 'Cottagecore', 'Y2K',
  'Business Casual', 'Vintage', 'Maximalist', 'Coastal',
]

type Tab = 'profile' | 'style' | 'data'

export default function SettingsPage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [activeTab, setActiveTab] = useState<Tab>('profile')
  const [selectedStyles, setSelectedStyles] = useState<string[]>([])
  const [deleteConfirm, setDeleteConfirm] = useState('')
  const [prefsSaved, setPrefsSaved] = useState(false)

  const accessToken = session?.accessToken as string | undefined

  const { mutate: savePrefs, isLoading: savingPrefs } = useMutation(
    () =>
      updateStylePreferences({ style_tags: selectedStyles }, accessToken!),
    {
      onSuccess: () => {
        setPrefsSaved(true)
        setTimeout(() => setPrefsSaved(false), 3000)
      },
    }
  )

  const { mutate: handleDeleteAccount, isLoading: deleting } = useMutation(
    () => deleteAccount(accessToken!),
    {
      onSuccess: () => signOut({ callbackUrl: '/' }),
    }
  )

  const toggleStyle = (style: string) => {
    setSelectedStyles((prev) =>
      prev.includes(style) ? prev.filter((s) => s !== style) : [...prev, style]
    )
  }

  if (status === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (status === 'unauthenticated') {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4 p-8 text-center">
        <h2 className="text-xl font-bold text-gray-900">Sign in to access settings</h2>
        <button
          onClick={() => signIn('pinterest')}
          className="px-6 py-3 bg-pinterest-red text-white font-semibold rounded-xl"
        >
          Connect Pinterest
        </button>
      </div>
    )
  }

  const tabs: { id: Tab; label: string; icon: React.ReactNode }[] = [
    {
      id: 'profile',
      label: 'Profile',
      icon: <UserCircleIcon className="w-4 h-4" />,
    },
    {
      id: 'style',
      label: 'Style Preferences',
      icon: <HeartIcon className="w-4 h-4" />,
    },
    {
      id: 'data',
      label: 'Data & Privacy',
      icon: <ShieldExclamationIcon className="w-4 h-4" />,
    },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900 mb-8">Settings</h1>

        {/* Tab bar */}
        <div className="flex gap-1 bg-white rounded-2xl p-1.5 shadow-sm border border-gray-100 mb-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={clsx(
                'flex-1 flex items-center justify-center gap-1.5 py-2.5 px-3 rounded-xl text-sm font-semibold transition-colors',
                activeTab === tab.id
                  ? 'bg-pinterest-red text-white shadow-sm'
                  : 'text-gray-500 hover:text-gray-900'
              )}
            >
              {tab.icon}
              <span className="hidden sm:inline">{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Profile tab */}
        {activeTab === 'profile' && (
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 space-y-6">
            <div className="flex items-center gap-4">
              {session?.user?.image ? (
                <Image
                  src={session.user.image}
                  alt={session.user.name ?? 'User'}
                  width={64}
                  height={64}
                  className="rounded-full ring-2 ring-pinterest-red/20"
                />
              ) : (
                <div className="w-16 h-16 rounded-full bg-pinterest-red flex items-center justify-center text-white text-2xl font-bold">
                  {session?.user?.name?.[0]?.toUpperCase() ?? 'U'}
                </div>
              )}
              <div>
                <p className="font-bold text-gray-900 text-lg">
                  {session?.user?.name ?? 'Pinterest User'}
                </p>
                <p className="text-sm text-gray-500">{session?.user?.email}</p>
                <p className="text-xs text-gray-400 mt-0.5">
                  Connected via Pinterest
                </p>
              </div>
            </div>

            <hr className="border-gray-100" />

            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-1">
                Pinterest Connection
              </h3>
              <p className="text-xs text-gray-500 mb-4">
                Your account is connected to Pinterest. We only have read access to your
                boards and pins.
              </p>
              <button
                onClick={() => signOut({ callbackUrl: '/' })}
                className="flex items-center gap-2 text-sm font-semibold text-red-600 hover:text-red-800 transition-colors"
              >
                <ArrowRightStartOnRectangleIcon className="w-4 h-4" />
                Disconnect Pinterest & Sign out
              </button>
            </div>
          </div>
        )}

        {/* Style preferences tab */}
        {activeTab === 'style' && (
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 space-y-6">
            <div>
              <h3 className="text-base font-bold text-gray-900 mb-1">
                Your Style Identity
              </h3>
              <p className="text-sm text-gray-500">
                Select the styles that resonate with you. This helps us tune your
                recommendations.
              </p>
            </div>

            <div className="flex flex-wrap gap-2">
              {STYLE_TAGS.map((style) => (
                <button
                  key={style}
                  onClick={() => toggleStyle(style)}
                  className={clsx(
                    'px-4 py-2 rounded-full border text-sm font-medium transition-colors',
                    selectedStyles.includes(style)
                      ? 'bg-pinterest-red border-pinterest-red text-white'
                      : 'border-gray-200 text-gray-600 hover:border-pinterest-red/40'
                  )}
                >
                  {style}
                </button>
              ))}
            </div>

            {prefsSaved && (
              <p className="text-sm text-green-600 font-medium">
                ✓ Preferences saved!
              </p>
            )}

            <button
              onClick={() => savePrefs()}
              disabled={savingPrefs || selectedStyles.length === 0}
              className="flex items-center gap-2 bg-pinterest-red hover:bg-red-700 disabled:opacity-50 text-white font-semibold px-6 py-2.5 rounded-xl transition-colors"
            >
              {savingPrefs ? (
                <>
                  <LoadingSpinner size="sm" className="border-white/30 border-t-white" />
                  Saving…
                </>
              ) : (
                'Save Preferences'
              )}
            </button>
          </div>
        )}

        {/* Data & Privacy tab */}
        {activeTab === 'data' && (
          <div className="space-y-5">
            {/* GDPR info */}
            <div className="bg-blue-50 border border-blue-100 rounded-2xl p-5">
              <h3 className="text-sm font-bold text-blue-900 mb-1">
                Your data rights (GDPR)
              </h3>
              <p className="text-xs text-blue-700 leading-relaxed">
                You have the right to access, rectify, and erase any personal data we hold
                about you. We store only the minimum data required to provide recommendations
                — your Pinterest user ID, board and pin metadata, and generated style
                preferences. We never store your full Pinterest access token permanently.
              </p>
            </div>

            {/* Data export */}
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
              <h3 className="text-base font-bold text-gray-900 mb-1">Export your data</h3>
              <p className="text-sm text-gray-500 mb-4">
                Download a copy of all data we hold about you in JSON format.
              </p>
              <button className="text-sm font-semibold text-pinterest-red border border-pinterest-red/30 hover:border-pinterest-red px-4 py-2 rounded-xl transition-colors">
                Request data export
              </button>
            </div>

            {/* Delete account */}
            <div className="bg-white rounded-2xl border border-red-100 shadow-sm p-6">
              <h3 className="text-base font-bold text-red-700 mb-1">Delete account</h3>
              <p className="text-sm text-gray-500 mb-4">
                Permanently delete your account and all associated data. This action{' '}
                <strong>cannot be undone</strong>.
              </p>

              <p className="text-sm text-gray-600 mb-2">
                Type <code className="bg-gray-100 px-1 py-0.5 rounded text-xs">DELETE</code> to
                confirm:
              </p>
              <input
                type="text"
                value={deleteConfirm}
                onChange={(e) => setDeleteConfirm(e.target.value)}
                placeholder="Type DELETE"
                className="border border-gray-200 rounded-xl px-4 py-2 text-sm mb-4 w-full max-w-xs focus:outline-none focus:ring-2 focus:ring-red-200"
              />

              <button
                onClick={() => handleDeleteAccount()}
                disabled={deleteConfirm !== 'DELETE' || deleting}
                className="flex items-center gap-2 bg-red-600 hover:bg-red-700 disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold px-5 py-2.5 rounded-xl transition-colors text-sm"
              >
                {deleting ? (
                  <>
                    <LoadingSpinner size="sm" className="border-white/30 border-t-white" />
                    Deleting…
                  </>
                ) : (
                  'Delete my account and all data'
                )}
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
