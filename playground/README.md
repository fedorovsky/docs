# playground

Test bed for tuning the `feature-docs` skill.

- `input/brief.md`: the feature request, written as a product ticket. This is the fixed input for every run.
- `app/docs/features/<feature>/`: output of the latest run.
- `app/`: a Vite + React + TypeScript app for the TRACK-12 feature, built task by task from the docs in `app/docs/features/`.

## Running the app

From `playground/app/`:

```bash
npm install
```

```bash
npm run dev
```

```bash
npm test
```

In the Claude desktop app the `playground-app` configuration in `.claude/launch.json` starts the dev server.
