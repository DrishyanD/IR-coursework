import type { ButtonHTMLAttributes, ReactNode } from "react";

type Variant = "primary" | "secondary" | "ghost";

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  children: ReactNode;
  variant?: Variant;
};

const variants: Record<Variant, string> = {
  primary: "bg-[var(--ink)] text-[var(--surface)] hover:opacity-90 shadow-[0_8px_30px_rgba(16,24,40,0.12)]",
  secondary: "border border-[var(--border-strong)] bg-[var(--surface)] text-[var(--ink)] hover:bg-[var(--surface-muted)]",
  ghost: "text-[var(--text-muted)] hover:bg-[var(--surface-muted)] hover:text-[var(--ink)]",
};

export function Button({ children, className = "", variant = "primary", ...props }: Props) {
  return (
    <button
      className={`inline-flex h-10 items-center justify-center gap-2 rounded-xl px-4 text-sm font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)] focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
