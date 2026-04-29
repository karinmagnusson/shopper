import { cn } from "@/lib/utils";

interface Props {
  size?: "sm" | "md" | "lg";
  className?: string;
}

export default function LoadingSpinner({ size = "md", className }: Props) {
  const s = { sm: "h-5 w-5", md: "h-8 w-8", lg: "h-12 w-12" }[size];
  return (
    <div
      className={cn("animate-spin rounded-full border-2 border-gray-200 border-t-[#E60023]", s, className)}
      role="status"
      aria-label="Loading"
    />
  );
}
