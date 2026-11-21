# SPEC.en.md — Product & Technical Specification

> **English** | [Versão em Português](SPEC.md)

## 0. Instructions for Agents

- This document is the official specification for **The Last Blog in the World**. Do not implement anything out of scope without asking.
- **Do not add unapproved dependencies** beyond those listed in Section 3.
- **Zero cost is mandatory**: everything must fit within permanent free tiers (Render, Supabase, Upstash, GHCR).
- **Never commit secrets**. Use local `.env`, GitHub Secrets, and host environment variables.
- Write tests alongside each feature. Minimum 80% coverage required.

---

## 1. Context and Objective

**The Last Blog in the World** is a single-author personal blog with two primary goals:
1. A real personal blog to publish thoughts, ideas, reflections, book notes, and technical articles.
2. A hands-on engineering portfolio project showcasing Docker, CI/CD, security, testing, and cloud deployment with zero operating cost.

---

## 2. Scope

### In Scope
- Public site: Home, post detail, tag listing, search, About page, RSS, sitemap, `robots.txt`, custom 404/500 pages.
- Custom administrative dashboard in a secret configurable URL (`ADMIN_PATH`), with login, 2FA TOTP, and CRUDs for posts/tags/media/SiteConfig.
- Markdown rendering with syntax highlighting, strict sanitization (`nh3`), and HTML caching.
- Internationalization (PT-BR default, EN at `/en/`) with optional post translations.
- Light/Dark theme switching (`data-bs-theme`).
- SQLite for local dev; PostgreSQL 16 (Supabase) + Redis 7 (Upstash) in production.
- Multi-stage Dockerfile, local `docker-compose`, GitHub Actions CI/CD with automated deploy.

### Out of Scope
- Public comments, public registration, multiple authors, newsletters, contact forms.
- Kubernetes, Helm, Argo CD (reserved for a companion project).
- Prometheus/Grafana/Loki (future roadmap).
- Standard Django admin (`admin.site.urls`).
- E-commerce or public API.

---

## 3. Tech Stack

- **Framework**: Python 3.12 + Django 6.1.x
- **Database**: SQLite (dev) / PostgreSQL 16 via Supabase with PgBouncer connection pooler (prod)
- **DB Driver**: `psycopg[binary]` (psycopg3)
- **Cache & Sessions**: Redis 7 via Upstash (8-hour isolated sessions)
- **Media Storage**: Supabase Storage via S3 API (`django-storages[s3]` + `boto3`)
- **WSGI Server & Statics**: Gunicorn + WhiteNoise
- **Front-end**: Space Grotesk, Inter, and JetBrains Mono served locally (WOFF2)
- **Markdown**: Python-Markdown + Pygments + `nh3` sanitization
- **Security**: `django-axes`, `django-otp` + `qrcode`, `argon2-cffi`
- **Quality**: `pytest`, `pytest-django`, `pytest-cov`, `Ruff`, `pre-commit`
- **CI/CD**: GitHub Actions, Docker Buildx, GHCR, Trivy, `pip-audit`, Dependabot
- **Deploy**: Render free web service

---

## 4. Completed Milestones

1. **M1 — Foundation**: Project scaffolding, layered settings, Ruff, pre-commit, initial CI.
2. **M2 — Public Domain**: Post and Tag models, i18n, Markdown, views, RSS, sitemap, SEO.
3. **M3 — Dashboard**: Custom login, 2FA TOTP, rate limiting, CRUDs, preview API.
4. **M4 — Docker**: Multi-stage Dockerfile, local compose with Postgres and Redis, healthchecks.
5. **M5 — Production**: Supabase, Upstash, Render, full security scans, keep-alive workflow.
6. **M6 — Visual Identity & Mobile**: Soft Cyberpunk / Retro-Futuristic Terminal theme, local fonts, responsive offcanvas.
7. **M7 — Polish & v1.0.0 Release**: WCAG AA accessibility, automated screenshots, `seed_demo` command, exhaustive documentation, v1.0.0 release.
