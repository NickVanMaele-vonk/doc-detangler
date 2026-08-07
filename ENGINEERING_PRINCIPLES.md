# Tournament Organizer PWA — Engineering Principles

## Document Status: Living reference — mandatory for all code changes

These principles are mandatory. They are derived from general software engineering best practice and from patterns already established in this codebase. Before writing or modifying any file, verify the proposed change against every applicable principle below.

---

## 1. File Size

**Hard limit: 300 lines. Soft limit: 200 lines. Never add features to a file that already exceeds 300 lines without extracting first.**

At 200 lines, evaluate whether the file has grown beyond its original purpose and propose a split. At 300 lines, stop immediately: do not add the requested feature, propose a concrete extraction plan (naming each new file and what it will contain), and wait for approval before writing any code. The limits apply to all file types — page components, API routes, utility modules, and hooks alike.

---

## 2. Single Responsibility

**Each file must do exactly one thing. Rendering, data fetching, state management, and business logic are four distinct concerns and must not coexist in a single file.**

A React component file should contain only JSX and the direct UI state that controls it (open/closed, hover, active tab). Data fetching belongs in a custom hook or a `services/` file. Business logic and transformations belong in a `utils/` or `lib/` file. If you find yourself writing a `fetch` call and a JSX return in the same file, that is a signal to split.

Always split these concerns into their own files:
- API calls / data fetching → `services/` or `api/`
- Reusable logic → `hooks/` (custom React hooks) or `utils/`
- Type/interface definitions → `types/` or a co-located `.types.ts` file
- Constants → `constants.ts`
- Complex conditional rendering → extract to a named sub-component

---

## 3. Component Extraction

**Extract a sub-component whenever a logical block of JSX has its own fetch/state/render cycle, or when it would otherwise be re-used across two or more parent files.**

Co-locate a sub-component alongside its parent (same directory) when it is used only by that parent and has no independent fetch cycle — for example, a dialog or a card that receives all its data via props. Place it in a dedicated file in a shared `components/` directory only when it is used by more than one parent. Any component that owns its own data fetching must live in its own file, never inline inside a parent, regardless of size.

---

## 4. Hook Extraction

**Extract a custom hook whenever two or more state variables always change together, or whenever a `useEffect` + its dependent state constitutes a coherent data-loading or side-effect unit.**

A hook named `useSomething` owns a slice of state and the logic that drives it; it returns only what the component needs to render. Hooks live in a `hooks/` directory unless they are used exclusively by a single co-located component, in which case they may be co-located. Never inline complex `useEffect` or multi-variable state logic directly in a page component when the same logic could be expressed as a named hook with a clear return type.

---

## 5. Prop Discipline

**A component with more than five props is a signal to consolidate. Dead props must be removed. Never pass raw server data that the child could receive pre-computed.**

Group tightly-related props into a single typed object (e.g. pass `session: SessionSummary` rather than `sessionId`, `sessionName`, `sessionType` as three separate props). Remove any prop that is defined in the interface but never read inside the component — dead props silently accumulate and mislead the next developer. When a parent fetches data, transform it into the shape the child needs before passing it; do not delegate transformation work to the child by passing a raw API response.

---

## 6. State Ownership

**State lives at the lowest component in the tree that needs it. State required by two or more siblings lives in their nearest common ancestor — not higher.**

Lifting state above the nearest common ancestor creates unnecessary coupling and prop drilling. If the same piece of state ends up being threaded through three or more components to reach its consumer, extract a context or a shared hook instead. Avoid storing derived values in state: compute them inline or with `useMemo` from their source values, and keep the state atom as small as possible.

---

## 7. Data Fetching

**No N+1 fetch patterns. Fire independent requests in parallel with `Promise.all`. Add a dedicated API route only when an existing route has a structural gap — never bolt extra data onto an existing route just to avoid creating a new one.**

An N+1 pattern — fetching a list of N items and then issuing one additional request per item inside a loop — is always wrong. Consolidate into a single route that returns all required data in one response, or issue all sub-requests in parallel. When a general-purpose route cannot return data a consumer needs without traversing an extra relation or aggregating a secondary table, create a dedicated route. The Cross-Tab route (`GET /api/organizer/crosstab`) is the canonical example: it exists because the general sessions list endpoint has structural gaps that cannot be fixed without breaking callers.

---

## 8. Dead Code

**Dead props, unused state variables, unreachable handlers, and commented-out code must be removed before a file is considered complete.**

Dead code is a maintenance liability: it implies the code is active and must be understood by anyone reading the file later. When a feature changes and a prop, handler, or state variable is no longer read, remove it in the same commit. Do not comment out code and leave it — if a block of logic may be needed again it belongs in version control history, not in a comment in the active file.

---

## 9. Documentation

**Architectural decisions belong in `requirements/ARCHITECTURE.md`. Implementation rationale that is not self-evident from the code belongs in `CLAUDE.md`. Source file comments are reserved for non-obvious local logic only.**

Do not add file-level doc comments or JSDoc blocks to source files in this project — the requirements documents are the canonical source of truth for decisions and rationale. When a piece of implementation detail is important enough to document, ask whether it belongs in `CLAUDE.md` (a pattern other developers must follow) or in `ARCHITECTURE.md` (a structural decision). A comment inside a `.ts` or `.tsx` file is appropriate only when the logic itself is genuinely non-obvious and cannot be made clearer by renaming or restructuring the code.

---

## 10. Consistency

**Follow existing patterns in the codebase before introducing new ones. Read two or three neighbouring files before writing a new component, route, or hook.**

When adding a new component, open the most structurally similar existing component first and match its file layout, naming conventions, import order, and state patterns. When adding a new API route, read an existing route in the same directory and match its JWT validation, error handling, and response shape. Introducing a second way to do something that already has an established pattern creates cognitive overhead for everyone who works on the codebase after you. If the existing pattern genuinely does not fit the new case, document the divergence in `CLAUDE.md` before writing the code.

---

## 11. Implementation Standards

Always use standard solutions. Never create custom CSS, custom utilities, custom hooks, or bespoke implementations when a standard Tailwind class, a standard React pattern, or an existing project convention already covers the need.

If a request cannot be satisfied with a standard solution, push back immediately. Explain why the standard approach does not fit, then propose the closest standard alternative before writing any code. Do not implement a custom solution without explicit approval.

Never write a new function or piece of code if an existing piece of code already solves the problem. Always search the existing codebase first. If exact re-use is impossible, consider refactoring before creating anything new. Only create net new code if the existing codebase cannot be made to cover it.

---

## 12. Schema Change Discipline

All schema changes must go through `prisma migrate dev`. No exceptions.

Forbidden:

- `prisma db push` — silently mutates the live database without creating a migration file, causing permanent migration history drift.
- Direct DDL against the database (`ALTER TABLE`, `CREATE TABLE`, `RENAME COLUMN`, `ADD CONSTRAINT`, etc.) run via Neon console, psql, or `prisma db execute` — these bypass the migration system entirely. The only permitted use of `prisma db execute` is to run read-only `SELECT` queries for diagnosis.
- Creating migration files manually and marking them as applied with `prisma migrate resolve` — this is a last-resort recovery tool only, not a substitute for the normal workflow.

Required workflow for every schema change:

1. Edit `prisma/schema.prisma` to reflect the intended change.
2. Run `npx prisma migrate dev --name <description>` to generate and apply the migration file.
3. Commit both `prisma/schema.prisma` and the new `prisma/migrations/*/migration.sql` file in the same commit.

If `prisma migrate dev` is blocked by drift: stop immediately. Do not attempt a workaround. Report the full output of `npx prisma migrate status` and wait for instructions.

---

## 13. Git Discipline

Commit after each screen or feature is complete and verified.

- Commit message format: `SCR-ORG-04: Room map editor — initial implementation`
- Never commit `.env`, `.env.local`, or any file containing secrets.
