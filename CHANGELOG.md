# Changelog

Todas as mudanças notáveis do projeto serão documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e o projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [0.5.0] - 2026-11-20

### Adicionado (Milestone 5 — Produção)

- **Infraestrutura em Nuvem (Custo Zero)**:
  - Documentação e configuração de integração com Supabase (PostgreSQL 16 com PgBouncer, `DISABLE_SERVER_SIDE_CURSORS=True`, connection pooling e Supabase Storage via S3).
  - Configuração do Upstash Redis 7 para cache e gerenciamento de sessões com expiração de 8h.
  - Configuração do serviço de deploy no Render Web Service baseado no Dockerfile multi-stage.
- **Pipeline CI/CD Completo (`.github/workflows/ci.yml`)**:
  - Job `security`: auditoria de vulnerabilidades de dependências via `pip-audit` e scan de sistema de arquivos via Trivy.
  - Job `test`: execução com serviços reais `postgres:16-alpine` e `redis:7-alpine` no GitHub Actions, garantindo que os testes rodem em ambiente idêntico ao de produção.
  - Job `build`: build multi-stage com Docker Buildx, push para o GitHub Container Registry (`ghcr.io`) com tags `:sha-<commit>` e `:latest`, e scan da imagem Docker gerada com Trivy.
  - Job `deploy`: disparo automático do webhook do Render (`RENDER_DEPLOY_HOOK_URL`) exclusivamente em push na branch `main` após aprovação de todos os jobs anteriores, integrado ao GitHub Environment `production`.
- **Automação e Manutenção**:
  - Dependabot: adicionado monitoramento semanal de dependências do ecossistema `docker` no `.github/dependabot.yml`.
  - Workflow `keep_alive.yml`: agendamento a cada 3 horas (e disparo manual via `workflow_dispatch`) para pingar `/healthz` no Render e evitar dormência do container gratuito e inatividade do projeto no Supabase.
  - Workflow `backup.yml`: rotina agendada semanalmente (e disparo manual) executando `pg_dump` no PostgreSQL e salvando o artefato de backup com retenção de 30 dias no GitHub Actions.
- **Operação e Recuperação de Desastres**:
  - `docs/backup_restore.md`: manual completo de procedimentos operacionais para backup manual e automático, restauração de dump (`pg_restore`), exportação de arquivos de mídia do Supabase Storage, aplicação de migrações e rollback de deploy no Render.
  - `.env.example`: atualizado com a documentação de todas as variáveis de ambiente necessárias para os serviços de produção.
- **Testes e Qualidade**:
  - 16 novos testes automatizados em `tests/test_production_settings.py` validando os parâmetros de segurança de `config/settings/production.py` (`DEBUG=False`, `ALLOWED_HOSTS`, redirecionamento HTTPS, HSTS, cookies seguros, Argon2, S3 Storage, WhiteNoise, connection pooling e falha explícita na ausência de variáveis obrigatórias).
  - Total de 89 testes automatizados passando com cobertura de 92.33% (mínimo exigido: 80%).

## [0.4.0] - 2026-11-20

### Adicionado (Milestone 4 — Docker)

- **Containerização**:
  - `Dockerfile` multi-stage (`builder` → `final`) baseado em `python:3.12-slim`.
  - Estágio `builder` instala dependências de build (gcc, libpq-dev) e pacotes Python em prefix isolado (`/install`).
  - Estágio `final` copia apenas o necessário, executa `collectstatic` durante o build (com `ARG SECRET_KEY` dummy, nunca em runtime) e WhiteNoise serve os estáticos.
  - Usuário non-root `appuser` (uid 1000) — a imagem não roda como root.
  - `HEALTHCHECK` Docker nativo chamando `/healthz` a cada 30s.
  - Gunicorn como entrypoint, workers e timeout configuráveis via env (`GUNICORN_WORKERS`, `GUNICORN_TIMEOUT`, `PORT`).
  - `.dockerignore` completo excluindo `.venv`, `media/`, `db.sqlite3`, `.env`, caches e arquivos de CI.
- **Docker Compose local**:
  - `docker-compose.yml` com três serviços: `web` (build local), `db` (postgres:16-alpine) e `redis` (redis:7-alpine).
  - Volumes nomeados `postgres_data` e `redis_data` para persistência de dados.
  - Healthchecks nativos em `db` (`pg_isready`) e `redis` (`redis-cli ping`).
  - `web` só sobe após `db` e `redis` estarem healthy (`depends_on: condition: service_healthy`).
  - Variáveis `DATABASE_URL` e `REDIS_URL` injetadas pelo compose, apontando para serviços internos.
- **Healthcheck `/healthz` aprimorado**:
  - Endpoint migrado de texto puro para JSON: `{"status": "ok", "checks": {"db": "ok", "cache": "ok"}}`.
  - Valida conectividade real com o banco de dados (executa `SELECT 1`) e com o cache Redis (set/get).
  - Retorna HTTP 503 com `{"status": "error", "checks": {...}}` em caso de falha em qualquer serviço.
- **Pipeline CI/CD — job `build` ativado**:
  - Docker Buildx com cache de GitHub Actions (`type=gha`).
  - Login no GHCR com `GITHUB_TOKEN` (permissão `packages: write`).
  - Build e push da imagem com tags `:sha-<git_sha>` e `:latest` (apenas em `main`).
  - Trivy scan da imagem após push (modo `table`, `exit-code: 0` — reporta sem bloquear; bloqueio habilitado no M5).
- **Makefile**:
  - Atalhos para todos os fluxos comuns: `make up`, `make down`, `make migrate`, `make test-docker`, `make shell`, `make build`, `make test`, `make lint`.
- **Testes**:
  - 12 novos testes em `tests/test_healthcheck.py` cobrindo: retorno 200/JSON, status ok, checks de DB e cache, retorno 503 em falha de DB, retorno 503 em falha de cache, acesso público sem autenticação, conectividade direta de DB e cache.
  - Cobertura total mantida: 92.33% (mínimo exigido: 80%).
- **Documentação**:
  - `.env.example` atualizado com variáveis do compose (`POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`).
  - README: nova seção "🐳 Rodando com Docker" com comandos completos de setup, uso e Makefile.
  - `pyproject.toml`: marker `integration` registrado para futuros testes de integração Docker.

## [0.3.0] - 2026-11-19

### Adicionado (Milestone 3 — Dashboard administrativo)

- **Segurança e Autenticação (fora do Django admin)**:
  - Painel administrativo montado exclusivamente em URL secreta `/{ADMIN_PATH}/` (configurável por env, padrão dev `/gestao/`), sem nenhuma rota do Django admin exposta.
  - Login customizado exclusivo para usuários com permissão de staff, com proteção contra força bruta e bloqueio temporário via `django-axes`.
  - Autenticação em dois fatores (2FA TOTP) obrigatória via `django-otp`, com geração de QR Code em SVG e exibição de chave manual para apps autenticadores.
  - Decorator e Mixin de autorização garantindo que todas as rotas da gestão exijam login e sessão 2FA ativa.
  - Template de lockout customizado para bloqueios de taxa de requisições (`429 Too Many Requests`).
  - Formulário autenticado de alteração de senha e fluxo seguro de encerramento de sessão (logout).
  - Argon2 configurado como hasher primário de senhas.
- **Painel de Gestão e CRUDs**:
  - Dashboard principal com métricas em tempo real (total de artigos, publicados, rascunhos, tags e mídias) e tabela de artigos recentes com filtros por status, idioma e busca textual.
  - Editor de artigos completo com abas de edição e pré-visualização em tempo real (Live Markdown Preview) via endpoint de API sanitizado.
  - Ação rápida para alternar artigos entre rascunho e publicado diretamente na listagem.
  - CRUD completo de Tags (criar, listar com contagem de artigos, editar e excluir).
  - Biblioteca de Mídia (Media Library) com upload, validação de `alt_text` para acessibilidade, cópia de código Markdown para a área de transferência e exclusão.
  - Editor das configurações gerais do site (`SiteConfig`) com abas para campos em Português e Inglês, redes sociais e imagem OpenGraph.
- **Testes e Qualidade**:
  - 59 testes automatizados cobrindo controle de acesso, obrigatoriedade de 2FA, bloqueio do axes, CRUDs de posts/tags/mídia/config e troca de senha.
  - Cobertura de código atingida: 92.14% (mínimo exigido: 80%).

## [0.2.0] - 2026-11-19

### Adicionado (Milestone 2 — Domínio público)

- **Modelos de dados**:
  - `apps.core.SiteConfig`: singleton com metadados do blog, biografia e redes sociais em PT e EN.
  - `apps.blog.Tag`: classificação de artigos com slug único.
  - `apps.blog.Post`: artigos em Markdown, sanitização com `nh3`, syntax highlight com Pygments, slug único por idioma, restrições para tradução entre idiomas e cálculo automático de tempo de leitura.
  - `apps.blog.MediaAsset`: arquivos de mídia com `alt_text` obrigatório para acessibilidade.
- **Páginas e funcionalidades públicas**:
  - Home: listagem paginada (10 por página) de posts publicados no idioma ativo.
  - Detalhe do artigo: HTML renderizado seguro, capa, metatags SEO (Open Graph, Twitter Card, JSON-LD Article) e aviso/link de tradução.
  - Listagem por Tag e Busca (`q` em título e conteúdo Markdown).
  - Página Sobre: biografia e links do autor vindos do `SiteConfig`.
  - Feed RSS (`/feed/` e `/en/feed/`) com `django.contrib.syndication`.
  - Sitemap XML (`/sitemap.xml`) e `robots.txt` apontando para o sitemap e bloqueando o caminho da gestão.
  - Páginas de erro customizadas (404 e 500).
- **Interface e Acessibilidade**:
  - Base em Bootstrap 5.3 com alternador de tema claro/escuro persistente via `localStorage` e suporte inicial a `prefers-color-scheme`.
  - Skip link para o conteúdo principal, tags semânticas e contraste adequado.
  - Seletor de idioma PT-BR / EN com templatetag `change_lang` mantendo a página equivalente.
  - Traduções compiladas em `.mo` para inglês e português.
- **Testes e Qualidade**:
  - Cobertura de testes de 98.84% com 36 testes passando (modelos, views, sitemaps, RSS, SEO, i18n).

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
