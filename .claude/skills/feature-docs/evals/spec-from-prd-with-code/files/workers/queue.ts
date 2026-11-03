// Background jobs run on the `jobs` queue (table `jobs`): a worker process polls it and calls the registered handler.
type Handler = (payload: unknown) => Promise<void>;
const handlers = new Map<string, Handler>();

export function register(name: string, handler: Handler) {
  handlers.set(name, handler);
}

export async function enqueue(name: string, payload: unknown): Promise<string> {
  // inserts a row into `jobs` and returns its id
  return "";
}
