import { useEffect } from "react";

function isTypingTarget(target: EventTarget | null) {
  if (!(target instanceof HTMLElement)) return false;

  return (
    target.tagName === "INPUT" ||
    target.tagName === "TEXTAREA" ||
    target.tagName === "SELECT" ||
    target.isContentEditable
  );
}

export function useGlobalSearchShortcut() {
  useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      if (event.key === "/" && !isTypingTarget(event.target)) {
        const searchInput =
          document.querySelector<HTMLInputElement>(
            '[data-global-search="true"]',
          );

        if (searchInput) {
          event.preventDefault();
          searchInput.focus();
          searchInput.select();
        }
      }

      if (event.key === "Escape") {
        const active = document.activeElement;
        if (
          active instanceof HTMLInputElement &&
          active.dataset.globalSearch === "true"
        ) {
          active.blur();
        }
      }
    };

    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, []);
}
