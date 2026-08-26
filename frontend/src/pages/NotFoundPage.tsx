import { ArrowLeft } from "lucide-react";
import { Link } from "react-router";
import { Container } from "../components/ui/Container";

export function NotFoundPage() {
  return (
    <Container className="grid min-h-[65vh] place-items-center py-20 text-center">
      <div>
        <div className="text-xs font-bold uppercase tracking-[0.16em] text-[var(--accent)]">404</div>
        <h1 className="mt-3 text-4xl font-bold tracking-[-0.04em]">Page not found</h1>
        <p className="mt-3 text-sm text-[var(--text-muted)]">The page you requested does not exist.</p>
        <Link to="/" className="mt-7 inline-flex items-center gap-2 text-sm font-bold hover:text-[var(--accent)]"><ArrowLeft size={16} />Back to research search</Link>
      </div>
    </Container>
  );
}
