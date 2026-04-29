import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "Shopper – Discover Fashion From Your Pinterest Style",
  description: "Connect your Pinterest boards and discover fashion products that match your unique style.",
  keywords: ["fashion", "pinterest", "shopping", "style", "recommendations"],
  openGraph: {
    title: "Shopper – Discover Fashion From Your Pinterest Style",
    description: "Shop products tailored to your Pinterest aesthetic.",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
