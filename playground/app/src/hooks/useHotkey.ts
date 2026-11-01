import { useEffect } from "react";

/**
 * Registers a global keyboard shortcut. Ignored while typing in inputs,
 * textareas and contenteditable elements.
 *
 * Currently used for "?" → keyboard shortcuts help (Header).
 */
export function useHotkey(key: string, handler: (e: KeyboardEvent) => void, opts: { meta?: boolean } = {}) {
  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      const target = e.target as HTMLElement;
      if (target.closest("input, textarea, [contenteditable=true]")) return;
      if (opts.meta && !(e.metaKey || e.ctrlKey)) return;
      if (e.key.toLowerCase() !== key.toLowerCase()) return;
      e.preventDefault();
      handler(e);
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [key, handler, opts.meta]);
}
