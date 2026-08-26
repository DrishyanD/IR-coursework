import { Menu, X } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, NavLink, useLocation } from "react-router";
import { APP_NAME } from "../../config";
import { Button } from "../ui/Button";
import { Container } from "../ui/Container";

const links = [
  { label: "Search", href: "/search" },
  { label: "Publications", href: "/publications" },
  { label: "Clustering", href: "/clustering" },
  { label: "Data Management", href: "/data" },
];

export function Header() {
  const [open, setOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    setOpen(false);
  }, [location.pathname]);

  return (
    <header className="sticky top-0 z-50 border-b border-[var(--border)] bg-[color-mix(in_srgb,var(--background)_88%,transparent)] backdrop-blur-xl print:static print:bg-white">
      <Container>
        <div className="flex h-[72px] items-center justify-between gap-4">
          <Link
            to="/"
            className="flex min-w-0 items-center gap-3 rounded-xl focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)]"
            aria-label={`${APP_NAME} home`}
          >
            <BrandMark />
            <div className="min-w-0">
              <div className="truncate text-[15px] font-bold tracking-[-0.02em] text-[var(--ink)]">
                Coventry Research
              </div>
              <div className="truncate text-[11px] font-medium text-[var(--text-faint)]">
                Information Retrieval
              </div>
            </div>
          </Link>

          <nav className="hidden items-center gap-0.5 lg:flex" aria-label="Main navigation">
            {links.map((item) => (
              <NavLink
                key={item.href}
                to={item.href}
                className={({ isActive }) =>
                  `rounded-xl px-3 py-2 text-sm font-medium transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)] ${
                    isActive
                      ? "bg-[var(--surface-muted)] text-[var(--ink)]"
                      : "text-[var(--text-muted)] hover:bg-[var(--surface-muted)] hover:text-[var(--ink)]"
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>

          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              className="h-10 w-10 px-0 lg:hidden print:hidden"
              onClick={() => setOpen((value) => !value)}
              aria-label={open ? "Close navigation" : "Open navigation"}
              aria-expanded={open}
              aria-controls="mobile-navigation"
            >
              {open ? <X size={19} /> : <Menu size={19} />}
            </Button>
          </div>
        </div>

        {open && (
          <nav
            id="mobile-navigation"
            className="grid gap-1 border-t border-[var(--border)] py-3 lg:hidden print:hidden"
            aria-label="Mobile navigation"
          >
            {links.map((item) => (
              <NavLink
                key={item.href}
                to={item.href}
                className={({ isActive }) =>
                  `rounded-xl px-3 py-2.5 text-sm font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)] ${
                    isActive
                      ? "bg-[var(--surface-muted)] text-[var(--ink)]"
                      : "text-[var(--text-muted)]"
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        )}
      </Container>
    </header>
  );
}

function BrandMark() {
  return (
    <div
      className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-[var(--ink)] text-[var(--surface)] shadow-sm"
      aria-hidden="true"
    >
      <svg width="19" height="19" viewBox="0 0 24 24" fill="none">
        <path
          d="M6.5 6.8c1.5-1.7 3.4-2.6 5.8-2.6 2 0 3.8.6 5.2 1.9"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
        />
        <path
          d="M17.8 17c-1.5 1.8-3.4 2.7-5.8 2.7-4.4 0-7.7-3.2-7.7-7.7S7.6 4.3 12 4.3"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
        />
        <circle cx="16.8" cy="11.8" r="2.5" fill="currentColor" />
      </svg>
    </div>
  );
}
