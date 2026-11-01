import { Dialog } from "../ui/Dialog";

const SHORTCUTS = [{ keys: "?", description: "Show keyboard shortcuts" }];

export function ShortcutsHelp({ open, onOpenChange }: { open: boolean; onOpenChange: (o: boolean) => void }) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange} title="Keyboard shortcuts">
      <ul>
        {SHORTCUTS.map((s) => (
          <li key={s.keys}>
            <kbd>{s.keys}</kbd> {s.description}
          </li>
        ))}
      </ul>
    </Dialog>
  );
}
