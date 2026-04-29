"use client";
import { motion } from "framer-motion";
import { Sparkles, ArrowRight, Link2, Search, ShoppingBag } from "lucide-react";
import Link from "next/link";
import Header from "@/components/ui/Header";
import Footer from "@/components/ui/Footer";
import { auth } from "@/lib/api";

const steps = [
  {
    icon: <Link2 className="h-8 w-8" />,
    title: "Connect Pinterest",
    description: "Link your Pinterest account and choose the fashion boards that best represent your personal style.",
    step: "01",
  },
  {
    icon: <Search className="h-8 w-8" />,
    title: "Analyze Your Style",
    description: "Our AI studies your saved pins to understand your color palette, aesthetic, and fashion preferences.",
    step: "02",
  },
  {
    icon: <ShoppingBag className="h-8 w-8" />,
    title: "Shop Recommendations",
    description: "Receive curated product recommendations from top retailers that match your unique Pinterest aesthetic.",
    step: "03",
  },
];

const features = [
  { title: "AI-Powered Style Analysis", description: "Advanced image recognition identifies your preferred colors, silhouettes, and aesthetics." },
  { title: "Personalized Picks", description: "Every recommendation is scored against your style profile for maximum relevance." },
  { title: "Top Retailer Partners", description: "Shop from curated brands and retailers with easy one-click affiliate links." },
  { title: "Privacy First", description: "Your Pinterest data stays yours. Delete your account and data at any time." },
];

const container = { hidden: {}, show: { transition: { staggerChildren: 0.1 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1">
        {/* Hero */}
        <section className="relative overflow-hidden bg-gradient-to-br from-rose-50 via-white to-pink-50 px-4 py-24 text-center sm:py-36">
          <div className="pointer-events-none absolute inset-0">
            <div className="absolute -top-40 -right-40 h-96 w-96 rounded-full bg-[#E60023]/5 blur-3xl" />
            <div className="absolute -bottom-40 -left-40 h-96 w-96 rounded-full bg-pink-200/30 blur-3xl" />
          </div>
          <motion.div
            className="relative mx-auto max-w-4xl"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-[#E60023]/10 px-4 py-1.5 text-sm font-medium text-[#E60023]">
              <Sparkles className="h-4 w-4" /> AI-Powered Fashion Discovery
            </div>
            <h1 className="mb-6 text-5xl font-bold tracking-tight text-gray-900 sm:text-6xl lg:text-7xl">
              Discover Fashion <span className="text-[#E60023]">You&apos;ll Love</span>
              <br />Based on Your Pinterest Style
            </h1>
            <p className="mx-auto mb-10 max-w-2xl text-xl text-gray-600">
              Connect your Pinterest boards and let our AI find shoppable products that perfectly match your saved aesthetic.
            </p>
            <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
              <button
                onClick={() => { window.location.href = auth.getLoginUrl(); }}
                className="btn-primary text-base px-8 py-4 shadow-lg shadow-[#E60023]/25"
              >
                Connect Pinterest <ArrowRight className="h-5 w-5" />
              </button>
              <Link href="#how-it-works" className="btn-secondary text-base px-8 py-4">
                How it works
              </Link>
            </div>
            <p className="mt-4 text-sm text-gray-400">Free to use · No credit card required</p>
          </motion.div>
        </section>

        {/* How it works */}
        <section id="how-it-works" className="bg-white px-4 py-24">
          <div className="mx-auto max-w-6xl">
            <motion.div className="mb-16 text-center" initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
              <h2 className="mb-4 text-4xl font-bold text-gray-900">How It Works</h2>
              <p className="text-lg text-gray-500">Three simple steps to your personalized fashion feed</p>
            </motion.div>
            <motion.div className="grid gap-8 md:grid-cols-3" variants={container} initial="hidden" whileInView="show" viewport={{ once: true }}>
              {steps.map((s) => (
                <motion.div key={s.step} variants={item} className="card relative p-8 text-center">
                  <div className="absolute -top-3 right-4 text-6xl font-black text-gray-100 select-none">{s.step}</div>
                  <div className="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-[#E60023]/10 text-[#E60023]">{s.icon}</div>
                  <h3 className="mb-2 text-xl font-semibold text-gray-900">{s.title}</h3>
                  <p className="text-gray-500 leading-relaxed">{s.description}</p>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </section>

        {/* Features */}
        <section className="bg-gray-50 px-4 py-24">
          <div className="mx-auto max-w-6xl">
            <motion.div className="mb-16 text-center" initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
              <h2 className="mb-4 text-4xl font-bold text-gray-900">Why Shopper?</h2>
              <p className="text-lg text-gray-500">Built for fashion lovers who want smarter, more personal shopping experiences.</p>
            </motion.div>
            <motion.div className="grid gap-6 sm:grid-cols-2" variants={container} initial="hidden" whileInView="show" viewport={{ once: true }}>
              {features.map((f) => (
                <motion.div key={f.title} variants={item} className="card p-6 flex items-start gap-4">
                  <div className="mt-1 h-3 w-3 shrink-0 rounded-full bg-[#E60023]" />
                  <div>
                    <h3 className="mb-1 font-semibold text-gray-900">{f.title}</h3>
                    <p className="text-gray-500 text-sm leading-relaxed">{f.description}</p>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </section>

        {/* CTA */}
        <section className="bg-[#E60023] px-4 py-24 text-center text-white">
          <motion.div className="mx-auto max-w-2xl" initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
            <h2 className="mb-4 text-4xl font-bold">Ready to shop your aesthetic?</h2>
            <p className="mb-8 text-rose-100">Connect your Pinterest account in seconds and start discovering products you&apos;ll actually love.</p>
            <button
              onClick={() => { window.location.href = auth.getLoginUrl(); }}
              className="inline-flex items-center gap-2 rounded-full bg-white px-8 py-4 text-base font-semibold text-[#E60023] shadow-xl transition hover:bg-rose-50 active:scale-95"
            >
              Get Started Free <ArrowRight className="h-5 w-5" />
            </button>
          </motion.div>
        </section>
      </main>
      <Footer />
    </div>
  );
}
