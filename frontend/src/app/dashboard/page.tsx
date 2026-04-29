'use client'

import { useState, useCallback } from 'react'
import { useSession, signIn } from 'next-auth/react'
import { useQuery, useMutation } from 'react-query'
import { useRouter } from 'next/navigation'
import Navbar from '@/components/Navbar'
import BoardCard from '@/components/BoardCard'
import AnalysisStatus from '@/components/AnalysisStatus'
import LoadingSpinner from '@/components/LoadingSpinner'
import { getBoards, startAnalysis, getAnalysisStatus } from '@/lib/api'
import type { AnalysisJob } from '@/types'
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline'

export default function DashboardPage() {
  const { data: session, status: sessionStatus } = useSession()
  const router = useRouter()
  const [selectedBoards, setSelectedBoards] = useState<Set<string>>(new Set())
  const [currentJob, setCurrentJob] = useState<AnalysisJob | null>(null)
  const [searchQuery, setSearchQuery] = useState('')

  const accessToken = session?.accessToken as string | undefined

  // Fetch boards
  const {
    data: boards,
    isLoading: boardsLoading,
    error: boardsError,
    refetch,
  } = useQuery(
    ['boards', accessToken],
    () => getBoards(accessToken!),
    {
      enabled: !!accessToken,
      staleTime: 5 * 60 * 1000,
    }
  )

  // Poll analysis job
  useQuery(
    ['analysis', currentJob?.id],
    () => getAnalysisStatus(currentJob!.id),
    {
      enabled: !!currentJob && currentJob.status === 'RUNNING',
      refetchInterval: 2000,
      onSuccess: (job) => {
        setCurrentJob(job)
        if (job.status === 'COMPLETED') {
          setTimeout(() => router.push('/recommendations'), 1500)
        }
      },
    }
  )

  // Start analysis mutation
  const { mutate: analyzeBoards, isLoading: analysisStarting } = useMutation(
    (boardIds: string[]) => startAnalysis(boardIds, accessToken!),
    {
      onSuccess: (job) => setCurrentJob(job),
    }
  )

  const toggleBoard = useCallback((id: string) => {
    setSelectedBoards((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }, [])

  const filteredBoards = boards?.filter((b) =>
    b.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  // Auth guard
  if (sessionStatus === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (sessionStatus === 'unauthenticated') {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4 p-8 text-center">
        <h2 className="text-xl font-bold text-gray-900">Sign in to continue</h2>
        <p className="text-gray-500 text-sm">Connect your Pinterest account to view your boards.</p>
        <button
          onClick={() => signIn('pinterest')}
          className="mt-4 px-6 py-3 bg-pinterest-red text-white font-semibold rounded-xl"
        >
          Connect Pinterest
        </button>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900">
            Your Pinterest Boards
          </h1>
          <p className="mt-1 text-gray-500 text-sm">
            Select the fashion boards you want to analyze, then click{' '}
            <strong>Analyze</strong>.
          </p>
        </div>

        {/* Analysis status */}
        {currentJob && (
          <div className="mb-8">
            <AnalysisStatus job={currentJob} />
          </div>
        )}

        {/* Toolbar */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
          <div className="relative w-full sm:w-72">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search boards…"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-pinterest-red/30"
            />
          </div>

          <div className="flex items-center gap-3">
            {selectedBoards.size > 0 && (
              <span className="text-sm text-gray-500">
                {selectedBoards.size} board{selectedBoards.size !== 1 ? 's' : ''} selected
              </span>
            )}
            <button
              onClick={() => analyzeBoards(Array.from(selectedBoards))}
              disabled={
                selectedBoards.size === 0 ||
                analysisStarting ||
                currentJob?.status === 'RUNNING'
              }
              className="flex items-center gap-2 bg-pinterest-red hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold px-5 py-2.5 rounded-xl transition-colors text-sm"
            >
              {analysisStarting ? (
                <>
                  <LoadingSpinner size="sm" className="border-white/30 border-t-white" />
                  Starting…
                </>
              ) : (
                'Analyze Selected Boards'
              )}
            </button>
          </div>
        </div>

        {/* Boards grid */}
        {boardsLoading ? (
          <div className="flex items-center justify-center py-24">
            <LoadingSpinner size="lg" />
          </div>
        ) : boardsError ? (
          <div className="text-center py-24">
            <p className="text-gray-500 mb-4">Failed to load your boards.</p>
            <button
              onClick={() => refetch()}
              className="text-pinterest-red text-sm font-semibold hover:underline"
            >
              Try again
            </button>
          </div>
        ) : filteredBoards?.length === 0 ? (
          <div className="text-center py-24 text-gray-400">
            {searchQuery ? `No boards match "${searchQuery}"` : 'No boards found.'}
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {filteredBoards?.map((board) => (
              <BoardCard
                key={board.id}
                board={board}
                selected={selectedBoards.has(board.id)}
                onToggle={toggleBoard}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
