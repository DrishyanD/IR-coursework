function SkeletonLine({ className = "" }: { className?: string }) {
  return (
    <div
      className={`animate-pulse rounded-full bg-[var(--surface-muted)] ${className}`}
    />
  );
}

export function SearchResultsSkeleton() {
  return (
    <div aria-label="Loading search results" aria-busy="true">
      {[1, 2, 3, 4].map((item) => (
        <div
          key={item}
          className="border-b border-[var(--border)] py-8 first:pt-2 last:border-b-0"
        >
          <div className="grid gap-4 sm:grid-cols-[34px_minmax(0,1fr)]">
            <SkeletonLine className="mt-1 hidden h-3 w-5 sm:block" />
            <div>
              <SkeletonLine className="h-5 w-[76%]" />
              <SkeletonLine className="mt-3 h-3 w-[42%]" />
              <div className="mt-5 space-y-2.5">
                <SkeletonLine className="h-3 w-full" />
                <SkeletonLine className="h-3 w-[91%]" />
                <SkeletonLine className="h-3 w-[64%]" />
              </div>
              <SkeletonLine className="mt-6 h-3 w-28" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
