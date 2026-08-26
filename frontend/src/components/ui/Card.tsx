import type { ReactNode } from "react";

export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <div className={`rounded-[22px] border border-[var(--border)] bg-[var(--surface)] shadow-[var(--shadow-soft)] ${className}`}>
      {children}
    </div>
  );
}
