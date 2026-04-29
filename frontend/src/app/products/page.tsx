"use client";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { SlidersHorizontal } from "lucide-react";
import Header from "@/components/ui/Header";
import LoadingSpinner from "@/components/ui/LoadingSpinner";
import ProductCard from "@/components/products/ProductCard";
import { api } from "@/lib/api";
import { getToken } from "@/lib/auth";

const CATEGORIES = ["All", "dress", "top", "jeans", "skirt", "jacket", "coat", "shoes", "bag", "accessories"];

export default function ProductsPage() {
  const [category, setCategory] = useState("");
  const [priceMax, setPriceMax] = useState("");
  const token = getToken();

  const { data: products = [], isLoading } = useQuery({
    queryKey: ["products", category, priceMax],
    queryFn: () => {
      const params = new URLSearchParams();
      if (category) params.set("category", category);
      if (priceMax) params.set("price_max", priceMax);
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      return api.get(`/api/v1/products?${params}`, { headers }).then((r) => r.data);
    },
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="mx-auto max-w-7xl px-4 py-10">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Recommendations</h1>
          <p className="mt-1 text-gray-500">Products matched to your Pinterest style.</p>
        </div>

        {/* Filters */}
        <div className="mb-6 flex flex-wrap gap-3 items-center">
          <SlidersHorizontal className="h-5 w-5 text-gray-400" />
          {CATEGORIES.map((c) => (
            <button
              key={c}
              onClick={() => setCategory(c === "All" ? "" : c)}
              className={`rounded-full px-4 py-1.5 text-sm font-medium transition ${
                (c === "All" && !category) || category === c
                  ? "bg-[#E60023] text-white"
                  : "bg-white text-gray-600 ring-1 ring-gray-200 hover:bg-gray-50"
              }`}
            >
              {c}
            </button>
          ))}
          <select
            value={priceMax}
            onChange={(e) => setPriceMax(e.target.value)}
            className="ml-auto rounded-lg border border-gray-200 bg-white px-3 py-1.5 text-sm text-gray-600 outline-none focus:border-[#E60023]"
          >
            <option value="">Any price</option>
            <option value="50">Under $50</option>
            <option value="100">Under $100</option>
            <option value="150">Under $150</option>
          </select>
        </div>

        {isLoading ? (
          <div className="flex justify-center py-24">
            <LoadingSpinner size="lg" />
          </div>
        ) : (
          <motion.div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            {products.map((p: any) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </motion.div>
        )}

        {!isLoading && products.length === 0 && (
          <div className="py-24 text-center text-gray-500">
            No products found. Try adjusting your filters or sync your Pinterest boards first.
          </div>
        )}
      </main>
    </div>
  );
}
