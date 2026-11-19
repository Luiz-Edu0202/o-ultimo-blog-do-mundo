# Changelog

Todas as mudanças notáveis do projeto serão documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e o projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [0.1.0] - 2026-11-19

### Adicionado (Milestone 1 — Fundação)

- Projeto Django 6.1.x inicializado com estrutura por domínio (`apps/core`, `apps/blog`, `apps/dashboard`, `apps/accounts`).
- Settings em camadas: `base.py` (comum), `local.py` (SQLite + DEBUG), `production.py` (PostgreSQL + Redis + HTTPS).
- Todas as variáveis sensíveis via `django-environ`; `.env.example` documentado.
- `requirements/` separados por ambiente (base, local, production).
- Ruff configurado como linter + formatter (Python 3.12, line-length 100).
- Pre-commit com Ruff, trailing-whitespace, end-of-file-fixer, check-yaml, detect-private-key.
- `pyproject.toml` com configuração de pytest, coverage (fail_under 80%).
- Endpoint `/healthz` (health check simples retornando 200 OK).
- Testes smoke: system check, apps registradas, admin não exposto, healthcheck.
- CI esqueleto no GitHub Actions: jobs de lint e test; security, build e deploy como placeholders.
- Dependabot configurado para pip e GitHub Actions (semanal).
- `.gitignore` atualizado para backups/, media/, staticfiles/.
- README com stack, estrutura, instruções de setup e roadmap.

### Decisões técnicas

- **Django 6.1.x** em vez do 5.x (spec original) — última estável, suporte ativo até ~2028.
- **psycopg3** (`psycopg[binary]`) como driver PostgreSQL — recomendado pelo Django 6.x.
- **MAILERS** em vez do `EMAIL_BACKEND` — adaptação para a API do Django 6.1 (deprecated).
