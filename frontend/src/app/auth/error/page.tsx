"use client";
import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { AlertCircle, ArrowLeft } from "lucide-react";
import { auth } from "@/lib/api";

const MESSAGES: Record<string, string> = {
  access_denied: "You declined permission to access Pinterest. Please try again.",
  missing_token: "Something went wrong during sign-in. Please try again.",
  invalid_state: "Session expired during sign-in. Please try again.",
  server_error: "A server error occurred. Please try again.",
  default: "An unexpected error occurred. Please try again.",
};

function AuthErrorContent() {
  const params = useSearchParams();
  const reason = params.get("reason") ?? "default";
  const message = MESSAGES[reason] ?? MESSAGES.default;

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md rounded-2xl bg-white p-8 shadow-lg text-center">
        <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-red-50">
          <AlertCircle className="h-8 w-8 text-[#E60023]" />
        </div>
        <h1 className="mb-2 text-2xl font-bold text-gray-900">Sign-in Failed</h1>
        <p className="mb-8 text-gray-500">{message}</p>
        <div className="flex flex-col gap-3">
          <button onClick={() => { window.location.href = auth.getLoginUrl(); }} className="btn-primary w-full justify-center">
            Try Again
          </button>
          <Link href="/" className="btn-secondary w-full justify-center">
            <ArrowLeft className="h-4 w-4" /> Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
}

export default function AuthErrorPage() {
  return (
    <Suspense fallback={<div className="flex min-h-screen items-center justify-center" />}>
      <AuthErrorContent />
    </Suspense>
  );
}
