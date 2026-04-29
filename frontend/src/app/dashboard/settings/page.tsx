"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { ShieldCheck, Trash2 } from "lucide-react";
import Header from "@/components/ui/Header";
import { getToken, removeToken } from "@/lib/auth";

export default function SettingsPage() {
  const router = useRouter();

  useEffect(() => {
    if (!getToken()) router.replace("/");
  }, [router]);

  function handleDisconnect() {
    removeToken();
    router.replace("/");
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="mx-auto max-w-2xl px-4 py-10">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="mb-2 text-3xl font-bold text-gray-900">Settings</h1>
          <p className="mb-8 text-gray-500">Manage your Pinterest connection and privacy controls.</p>
        </motion.div>

        <div className="space-y-4">
          <div className="card p-6">
            <div className="flex items-start gap-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-green-50 text-green-600">
                <ShieldCheck className="h-5 w-5" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900">Privacy Controls</h3>
                <p className="mt-1 text-sm text-gray-500">
                  We only access public boards and pins you explicitly share. Your data is never sold.
                  You can delete your account and all data at any time.
                </p>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-start gap-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-red-50 text-[#E60023]">
                <Trash2 className="h-5 w-5" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900">Disconnect Pinterest</h3>
                <p className="mt-1 mb-4 text-sm text-gray-500">
                  Disconnecting will sign you out and clear your local session. Your synced data will remain
                  on our servers until you request full deletion.
                </p>
                <button onClick={handleDisconnect} className="btn-secondary text-[#E60023] border-[#E60023]/20 hover:bg-red-50">
                  Disconnect Pinterest
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
