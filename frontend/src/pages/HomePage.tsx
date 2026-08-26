import { BrainCircuit, Database, Search } from "lucide-react";
import { Link } from "react-router";
import { SearchBar } from "../components/search/SearchBar";
import { Card } from "../components/ui/Card";
import { Container } from "../components/ui/Container";
import { useDocumentTitle } from "../hooks/useDocumentTitle";

const tasks = [
  { to: "/search", icon: Search, title: "Search publications", text: "Run ranked searches over the PurePortal publication index." },
  { to: "/clustering", icon: BrainCircuit, title: "Assign a cluster", text: "Enter document text or a BBC News link for Task 2." },
  { to: "/data", icon: Database, title: "Manage crawler", text: "Start or stop Task 1 updates and inspect crawl logs." },
];

export function HomePage() {
  useDocumentTitle("Research Search");
  return (
    <Container className="py-14 sm:py-20">
      <div className="mx-auto max-w-3xl text-center">
        <h1 className="text-4xl font-extrabold tracking-[-0.045em] sm:text-6xl">Coventry publication search</h1>
        <p className="mt-4 text-sm text-[var(--text-muted)]">Search publications from the Centre for Healthcare and Community Transformation.</p>
        <div className="mt-8"><SearchBar /></div>
      </div>
      <div className="mx-auto mt-12 grid max-w-4xl gap-4 md:grid-cols-3">
        {tasks.map(({ to, icon: Icon, title, text }) => (
          <Link key={to} to={to}>
            <Card className="h-full p-5 transition hover:border-[var(--border-strong)]">
              <Icon size={20} className="text-[var(--accent)]" />
              <h2 className="mt-4 font-bold">{title}</h2>
              <p className="mt-2 text-xs leading-5 text-[var(--text-muted)]">{text}</p>
            </Card>
          </Link>
        ))}
      </div>
    </Container>
  );
}
