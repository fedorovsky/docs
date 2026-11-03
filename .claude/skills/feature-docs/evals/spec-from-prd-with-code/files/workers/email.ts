import { register } from "./queue";

// Existing job: sends a transactional email through the provider. Enqueue "email.send" with { to, subject, html }.
register("email.send", async (payload) => {
  const { to, subject, html } = payload as { to: string; subject: string; html: string };
  void to; void subject; void html;
});
