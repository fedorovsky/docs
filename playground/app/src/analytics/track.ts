type EventName =
  | "header_search_submitted"
  | "search_result_opened"
  | "shortcuts_help_opened"
  | "refund_issued";

export function track(event: EventName, props: Record<string, string | number | boolean> = {}) {
  // Sent to the internal analytics collector; batched by the SDK.
  window.analytics?.track(event, props);
}

declare global {
  interface Window {
    analytics?: { track: (event: string, props: object) => void };
  }
}
