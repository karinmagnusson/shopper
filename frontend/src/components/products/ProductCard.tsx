"use client";
import Image from "next/image";
import { ExternalLink } from "lucide-react";
import { api } from "@/lib/api";
import { getToken } from "@/lib/auth";

interface Product {
  id: string;
  title: string;
  price?: number;
  image_url?: string;
  affiliate_url?: string;
  product_url?: string;
  retailer_name?: string;
  brand?: string;
  category?: string;
  colors?: string[];
}

export default function ProductCard({ product }: { product: Product }) {
  async function handleClick() {
    const token = getToken();
    if (token) {
      try {
        await api.post(`/api/v1/products/${product.id}/interact`, { interaction_type: "click" }, {
          headers: { Authorization: `Bearer ${token}` },
        });
      } catch { /* best-effort */ }
    }
    const dest = product.affiliate_url || product.product_url;
    if (dest) window.open(dest, "_blank", "noopener,noreferrer");
  }

  return (
    <div className="card overflow-hidden flex flex-col">
      <div className="relative h-60 bg-gray-100">
        {product.image_url ? (
          <Image src={product.image_url} alt={product.title} fill className="object-cover" sizes="(max-width:640px) 100vw, 25vw" />
        ) : (
          <div className="flex h-full items-center justify-center text-gray-300 text-4xl">👗</div>
        )}
        {product.category && (
          <span className="absolute top-2 left-2 rounded-full bg-white/90 px-2 py-0.5 text-xs font-medium text-gray-700 shadow">
            {product.category}
          </span>
        )}
      </div>
      <div className="p-4 flex flex-col flex-1">
        <h3 className="font-semibold text-gray-900 text-sm leading-snug line-clamp-2">{product.title}</h3>
        {product.brand && <p className="mt-0.5 text-xs text-gray-400">{product.brand}</p>}
        <div className="mt-auto flex items-center justify-between pt-3">
          <span className="text-lg font-bold text-gray-900">
            {product.price ? `$${Number(product.price).toFixed(2)}` : "–"}
          </span>
          <button onClick={handleClick} className="btn-primary text-xs px-3 py-1.5 gap-1">
            Shop <ExternalLink className="h-3 w-3" />
          </button>
        </div>
        {product.retailer_name && (
          <p className="mt-1 text-xs text-gray-400">{product.retailer_name}</p>
        )}
      </div>
    </div>
  );
}
