"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { RefreshCw, LayoutGrid } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Header from "@/components/ui/Header";
import LoadingSpinner from "@/components/ui/LoadingSpinner";
import { api } from "@/lib/api";
import { getToken } from "@/lib/auth";

export default function BoardsPage() {
  const router = useRouter();
  const qc = useQueryClient();
  const [syncing, setSyncing] = useState(false);

  useEffect(() => {
    if (!getToken()) router.replace("/");
  }, [router]);

  const { data: boards = [], isLoading } = useQuery({
    queryKey: ["boards"],
    queryFn: () => api.get("/api/v1/boards").then((r) => r.data),
    enabled: !!getToken(),
  });

  const syncMutation = useMutation({
    mutationFn: () => api.post("/api/v1/boards/sync"),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["boards"] }); setSyncing(false); },
    onError: () => setSyncing(false),
  });

  if (isLoading) return <div className="flex min-h-screen items-center justify-center"><LoadingSpinner size="lg" /></div>;

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="mx-auto max-w-6xl px-4 py-10">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Your Boards</h1>
            <p className="mt-1 text-gray-500">Select boards to analyze for style recommendations.</p>
          </div>
          <button
            onClick={() => { setSyncing(true); syncMutation.mutate(); }}
            disabled={syncing}
            className="btn-primary gap-2"
          >
            <RefreshCw className={`h-4 w-4 ${syncing ? "animate-spin" : ""}`} />
            {syncing ? "Syncing…" : "Sync Boards"}
          </button>
        </div>

        {boards.length === 0 ? (
          <div className="card p-16 text-center">
            <LayoutGrid className="mx-auto mb-4 h-16 w-16 text-gray-300" />
            <h3 className="mb-2 text-xl font-semibold text-gray-700">No boards yet</h3>
            <p className="mb-6 text-gray-500">Click &ldquo;Sync Boards&rdquo; to import your Pinterest boards.</p>
            <button onClick={() => { setSyncing(true); syncMutation.mutate(); }} className="btn-primary mx-auto">
              <RefreshCw className="h-4 w-4" /> Sync Now
            </button>
          </div>
        ) : (
          <motion.div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            {boards.map((board: any) => (
              <motion.div key={board.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="card overflow-hidden">
                <div className="h-40 bg-gradient-to-br from-rose-100 to-pink-200 flex items-center justify-center">
                  {board.cover_image_url ? (
                    <img src={board.cover_image_url} alt={board.name} className="h-full w-full object-cover" />
                  ) : (
                    <LayoutGrid className="h-12 w-12 text-[#E60023]/50" />
                  )}
                </div>
                <div className="p-4">
                  <h3 className="font-semibold text-gray-900">{board.name}</h3>
                  <p className="mt-1 text-sm text-gray-500">{board.pin_count} pins</p>
                  {board.last_synced && (
                    <p className="mt-1 text-xs text-gray-400">
                      Last synced {new Date(board.last_synced).toLocaleDateString()}
                    </p>
                  )}
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}
      </main>
    </div>
  );
}
