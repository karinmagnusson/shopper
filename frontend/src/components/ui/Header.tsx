"use client";
import Link from "next/link";
import { ShoppingBag } from "lucide-react";
import { getToken, removeToken } from "@/lib/auth";
import { auth } from "@/lib/api";
import { useRouter } from "next/navigation";

export default function Header() {
  const token = getToken();
  const router = useRouter();

  function handleLogout() {
    removeToken();
    router.push("/");
  }

  return (
    <header className="sticky top-0 z-30 border-b border-gray-100 bg-white/80 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
        <Link href={token ? "/dashboard" : "/"} className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#E60023]">
            <ShoppingBag className="h-4 w-4 text-white" />
          </div>
          <span className="text-lg font-bold text-gray-900">Shopper</span>
        </Link>

        {token ? (
          <nav className="flex items-center gap-6">
            <Link href="/dashboard" className="text-sm font-medium text-gray-600 hover:text-gray-900">Dashboard</Link>
            <Link href="/products" className="text-sm font-medium text-gray-600 hover:text-gray-900">Discover</Link>
            <button onClick={handleLogout} className="btn-secondary text-sm px-4 py-2">Sign Out</button>
          </nav>
        ) : (
          <div className="flex items-center gap-3">
            <button onClick={() => { window.location.href = auth.getLoginUrl(); }} className="btn-primary text-sm px-4 py-2">
              Connect Pinterest
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
