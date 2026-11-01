import { useCallback, useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useHotkey } from "../../hooks/useHotkey";
import { track } from "../../analytics/track";
import { ShortcutsHelp } from "./ShortcutsHelp";

export function Header() {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [helpOpen, setHelpOpen] = useState(false);

  useHotkey("?", useCallback(() => {
    setHelpOpen(true);
    track("shortcuts_help_opened");
  }, []));

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (query.trim().length < 2) return;
    track("header_search_submitted", { length: query.length });
    navigate(`/search?q=${encodeURIComponent(query.trim())}`);
  }

  return (
    <header className="header">
      <form onSubmit={onSubmit} role="search">
        <input
          type="search"
          placeholder="Search orders, customers…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </form>
      <ShortcutsHelp open={helpOpen} onOpenChange={setHelpOpen} />
    </header>
  );
}
