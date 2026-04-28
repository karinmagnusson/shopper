'use client'

import { useEffect, useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { getBoards, syncBoards, analyzeBoard, getToken } from '@/lib/api'
import type { PinterestBoard } from '@/types/pinterest'
import Header from '@/components/layout/Header'
import Footer from '@/components/layout/Footer'
import BoardCard from '@/components/pinterest/BoardCard'
import Button from '@/components/ui/Button'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import { RefreshCw, Sparkles } from 'lucide-react'

export default function BoardsPage() {
  const router = useRouter()
  const [boards, setBoards] = useState<PinterestBoard[]>([])
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!getToken()) {
      router.replace('/')
      return
    }
    fetchBoards()
  }, [router])

  const fetchBoards = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getBoards()
      setBoards(data.boards)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setLoading(false)
    }
  }, [])

  async function handleSync() {
    setSyncing(true)
    setError(null)
    try {
      await syncBoards()
      await fetchBoards()
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setSyncing(false)
    }
  }

  function toggleBoard(boardId: string) {
    setSelected((prev) => {
      const next = new Set(prev)
      if (next.has(boardId)) next.delete(boardId)
      else next.add(boardId)
      return next
    })
  }

  async function handleAnalyze() {
    if (selected.size === 0) return
    setAnalyzing(true)
    setError(null)
    try {
      await Promise.all(
        Array.from(selected).map((id) => analyzeBoard(id).catch((e) => console.warn(e)))
      )
      router.push('/recommendations')
    } catch (err) {
      setError((err as Error).message)
      setAnalyzing(false)
    }
  }

  return (
    <div className="flex flex-col min-h-screen">
      <Header />

      <main className="flex-1 max-w-6xl mx-auto w-full px-4 py-10">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Your Pinterest Boards</h1>
            <p className="text-gray-500 mt-1">
              Select the fashion boards you want to use for recommendations.
            </p>
          </div>
          <div className="flex gap-3">
            <Button variant="outline" onClick={handleSync} loading={syncing} className="gap-2">
              <RefreshCw size={16} />
              Sync boards
            </Button>
            <Button
              onClick={handleAnalyze}
              loading={analyzing}
              disabled={selected.size === 0}
              className="gap-2"
            >
              <Sparkles size={16} />
              Analyze {selected.size > 0 ? `(${selected.size})` : ''}
            </Button>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
            {error}
          </div>
        )}

        {loading ? (
          <div className="flex justify-center py-24">
            <LoadingSpinner size="lg" />
          </div>
        ) : boards.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-24 text-center">
            <div className="text-6xl mb-4">📌</div>
            <h2 className="text-xl font-semibold text-gray-700 mb-2">No boards found</h2>
            <p className="text-gray-500 mb-6">
              Click &quot;Sync boards&quot; to import your Pinterest boards.
            </p>
            <Button onClick={handleSync} loading={syncing}>
              Sync now
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
            {boards.map((board) => (
              <BoardCard
                key={board.id}
                board={board}
                selected={selected.has(board.pinterest_board_id)}
                onToggle={() => toggleBoard(board.pinterest_board_id)}
              />
            ))}
          </div>
        )}

        {selected.size > 0 && !loading && (
          <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50">
            <div className="bg-white rounded-2xl shadow-xl border border-gray-200 px-6 py-4 flex items-center gap-4">
              <span className="text-gray-700 text-sm font-medium">
                {selected.size} board{selected.size > 1 ? 's' : ''} selected
              </span>
              <Button onClick={handleAnalyze} loading={analyzing} className="gap-2">
                <Sparkles size={16} />
                Find my style
              </Button>
            </div>
          </div>
        )}
      </main>

      <Footer />
    </div>
  )
}
