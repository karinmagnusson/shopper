"use client";
import { Suspense, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { setToken } from "@/lib/auth";
import LoadingSpinner from "@/components/ui/LoadingSpinner";

function AuthCallbackContent() {
  const router = useRouter();
  const params = useSearchParams();

  useEffect(() => {
    const token = params.get("token");
    const error = params.get("error");
    if (error) {
      router.replace(`/auth/error?reason=${encodeURIComponent(error)}`);
      return;
    }
    if (token) {
      setToken(token);
      router.replace("/dashboard");
    } else {
      router.replace("/auth/error?reason=missing_token");
    }
  }, [router, params]);

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <LoadingSpinner size="lg" />
        <p className="mt-4 text-gray-500">Completing sign-in…</p>
      </div>
    </div>
  );
}

export default function AuthCallbackPage() {
  return (
    <Suspense fallback={<div className="flex min-h-screen items-center justify-center"><LoadingSpinner size="lg" /></div>}>
      <AuthCallbackContent />
    </Suspense>
  );
}
