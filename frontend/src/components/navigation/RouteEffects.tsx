import { useEffect, useRef, useState } from "react";
import { useLocation } from "react-router";

function labelForPath(pathname: string) {
  if (pathname === "/") return "Home";
  if (pathname.startsWith("/search")) return "Search";
  if (pathname.startsWith("/advanced-search")) return "Advanced search";
  if (/^\/publications\/[^/]+/.test(pathname)) return "Publication details";
  if (pathname.startsWith("/publications")) return "Publications";
  if (pathname.startsWith("/clustering")) return "Clustering";
  if (pathname.startsWith("/evaluation")) return "Evaluation";
  if (pathname.startsWith("/system")) return "System";
  if (pathname.startsWith("/about")) return "About";
  return "Page";
}

export function RouteEffects() {
  const location = useLocation();
  const [announcement, setAnnouncement] = useState("");
  const firstRender = useRef(true);

  useEffect(() => {
    if (firstRender.current) {
      firstRender.current = false;
      return;
    }

    window.scrollTo({ top: 0, behavior: "auto" });
    setAnnouncement(`${labelForPath(location.pathname)} page loaded`);
  }, [location.pathname]);

  return (
    <div
      className="sr-only"
      role="status"
      aria-live="polite"
      aria-atomic="true"
    >
      {announcement}
    </div>
  );
}
