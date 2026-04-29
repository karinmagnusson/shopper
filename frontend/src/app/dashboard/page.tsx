"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { ArrowRight, Sparkles, LayoutGrid, Settings } from "lucide-react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import Header from "@/components/ui/Header";
import LoadingSpinner from "@/components/ui/LoadingSpinner";
import { api, auth } from "@/lib/api";
import { getToken } from "@/lib/auth";

export default function DashboardPage() {
  const router = useRouter();

  useEffect(() => {
    if (!getToken()) router.replace("/");
  }, [router]);

  const { data: user, isLoading } = useQuery({
    queryKey: ["me"],
    queryFn: () => api.get("/api/v1/auth/me").then((r) => r.data),
    enabled: !!getToken(),
  });

  const { data: boards } = useQuery({
    queryKey: ["boards"],
    queryFn: () => api.get("/api/v1/boards").then((r) => r.data),
    enabled: !!getToken(),
  });

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="mx-auto max-w-6xl px-4 py-10">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="mb-2 text-3xl font-bold text-gray-900">
            Welcome back{user?.email ? `, ${user.email.split("@")[0]}` : ""}!
          </h1>
          <p className="mb-8 text-gray-500">Here&apos;s your style dashboard.</p>
        </motion.div>

        {/* Quick stats */}
        <div className="mb-8 grid gap-4 sm:grid-cols-3">
          {[
            { label: "Boards synced", value: boards?.length ?? 0 },
            { label: "Pins analyzed", value: "–" },
            { label: "Products found", value: "–" },
          ].map((stat) => (
            <motion.div key={stat.label} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="card p-6">
              <div className="text-3xl font-bold text-[#E60023]">{stat.value}</div>
              <div className="mt-1 text-sm text-gray-500">{stat.label}</div>
            </motion.div>
          ))}
        </div>

        {/* Actions */}
        <div className="grid gap-4 sm:grid-cols-2">
          <Link href="/dashboard/boards" className="card p-6 flex items-start gap-4 hover:ring-[#E60023]/40">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-[#E60023]/10 text-[#E60023]">
              <LayoutGrid className="h-6 w-6" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900">Manage Boards</h3>
              <p className="mt-1 text-sm text-gray-500">Sync Pinterest boards and trigger style analysis.</p>
            </div>
            <ArrowRight className="h-5 w-5 text-gray-400" />
          </Link>

          <Link href="/products" className="card p-6 flex items-start gap-4 hover:ring-[#E60023]/40">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-[#E60023]/10 text-[#E60023]">
              <Sparkles className="h-6 w-6" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900">See Recommendations</h3>
              <p className="mt-1 text-sm text-gray-500">Browse products matched to your Pinterest style.</p>
            </div>
            <ArrowRight className="h-5 w-5 text-gray-400" />
          </Link>

          <Link href="/dashboard/settings" className="card p-6 flex items-start gap-4 hover:ring-[#E60023]/40">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gray-100 text-gray-600">
              <Settings className="h-6 w-6" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900">Settings</h3>
              <p className="mt-1 text-sm text-gray-500">Manage your Pinterest connection and privacy.</p>
            </div>
            <ArrowRight className="h-5 w-5 text-gray-400" />
          </Link>
        </div>
      </main>
    </div>
  );
}
