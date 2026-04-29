import Link from "next/link";
import { ShoppingBag } from "lucide-react";

export default function Footer() {
  return (
    <footer className="border-t border-gray-100 bg-white">
      <div className="mx-auto max-w-7xl px-4 py-10">
        <div className="flex flex-col items-center justify-between gap-6 sm:flex-row">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-[#E60023]">
              <ShoppingBag className="h-4 w-4 text-white" />
            </div>
            <span className="font-bold text-gray-900">Shopper</span>
          </div>
          <nav className="flex flex-wrap justify-center gap-x-6 gap-y-2 text-sm text-gray-500">
            <Link href="/about" className="hover:text-gray-900 transition">About</Link>
            <Link href="/privacy" className="hover:text-gray-900 transition">Privacy Policy</Link>
            <Link href="/terms" className="hover:text-gray-900 transition">Terms of Service</Link>
            <a href="mailto:hello@shopper.app" className="hover:text-gray-900 transition">Contact</a>
          </nav>
        </div>
        <p className="mt-6 text-center text-xs text-gray-400">© {new Date().getFullYear()} Shopper. Not affiliated with Pinterest, Inc.</p>
      </div>
    </footer>
  );
}
