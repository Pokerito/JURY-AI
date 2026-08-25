export function Skeleton({ className = '' }) {
  return <div className={`animate-pulse rounded-lg bg-white/10 ${className}`} />;
}

export function CardSkeleton() {
  return (
    <div className="glass-card bg-white/5 backdrop-blur-md border border-white/10 rounded-xl p-6 space-y-4">
      <Skeleton className="h-5 w-3/4" />
      <Skeleton className="h-4 w-1/2" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-2/3" />
    </div>
  );
}

export function TableRowSkeleton({ cols = 4 }) {
  return (
    <tr>
      {Array.from({ length: cols }).map((_, i) => (
        <td key={i} className="px-6 py-4">
          <Skeleton className="h-4 w-full" />
        </td>
      ))}
    </tr>
  );
}
