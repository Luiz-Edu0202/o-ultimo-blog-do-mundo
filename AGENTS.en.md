# AGENTS.md — Governance Instructions for AI Agents

> **English** | [Versão em Português](AGENTS.md)

This document provides operational rules and workflow guidelines for AI agents and developers working on **The Last Blog in the World**.

---

## 1. Mandatory Reading Order

1. `SPEC.md` (or `SPEC.en.md`) — Product specification and architecture (single source of truth).
2. `AGENTS.md` (this file) — Operational rules and workflow.
3. `CONTRIBUTING.md` — Branch conventions, commit standards, and styling.
4. `docs/` — Deep-dive guides for architecture, security, and operations.

---

## 2. Project Status & Milestone 7 Completion

The initial foundational cycle of the project (MVP / version `v1.0.0`) was **successfully completed in Milestone 7**:
- **Milestones 1 through 7 completed and integrated**.
- Over 100 automated tests passing with >90% code coverage.
- Full cloud infrastructure (Render, Supabase Postgres/S3, Upstash Redis) and CI/CD pipelines live in production.
- Soft Cyberpunk / Retro-Futuristic Terminal visual identity fully implemented.

---

## 3. Post-v1.0.0 Working Rules

Starting with version `v1.0.0`, all development follows the **Simplified Gitflow** model:

1. **Strict Branching from `develop`**:
   - All new work must be developed in branches created from `develop`: `fix/<slug>`, `perf/<slug>`, `feat/<slug>`, `docs/<slug>`.
   - **Direct commits to the `main` branch are strictly prohibited**.
2. **Integration and Testing in `develop`**:
   - Daily merges are integrated into `develop` only after passing local linting and tests.
3. **Production Deployment**:
   - Automated deployment to Render occurs **exclusively upon merging into `main`**.
   - The `main` branch only receives merges from `develop` when authorized by the user for a new release (`v1.x.x`).
4. **Permanent Zero Cost**:
   - No decision may introduce recurring operational costs. Paid services must be rejected immediately.
5. **Test Coverage**:
   - Maintain minimum 80% coverage (CI fails below this threshold). All new functionality requires tests.
6. **Secrets**:
   - Never commit secrets. Use local `.env` and GitHub Secrets in CI.
7. **No Exposed Django Admin**:
   - Keep `admin.site.urls` disabled. All management happens via the custom dashboard at `ADMIN_PATH`.

---

## 4. Commits & Conventions

- Follow English Conventional Commits strictly as defined in `CONTRIBUTING.md`.
- Format: `<type>(<scope>): <description in imperative>`.
- Keep commits atomic, tested, and avoid vague messages like `wip` or `fix stuff`.

---

## 5. When to Ask (and When to Act)

- **Ask**: New external dependencies, scope changes, infrastructure decisions, or architectural ambiguities.
- **Act directly**: Code formatting according to Ruff conventions, fixing typos, and writing additional tests.
