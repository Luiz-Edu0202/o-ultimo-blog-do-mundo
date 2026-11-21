## 0. Instruções para o agente

- Este documento é a **especificação oficial** do projeto **O Último Blog do Mundo**. Não implemente nada fora do escopo sem perguntar.
- **Não adicione dependências** além das listadas sem justificar e pedir aprovação.
- **Custo zero obrigatório**: toda solução deve caber em free tiers (Render, Supabase, Upstash, GHCR). Se algo exigir serviço pago, **pare e pergunte**.
- **Nunca commite segredos**. Use `.env` local (no `.gitignore`), GitHub Secrets e variáveis de ambiente do host.
- Trabalhe em **milestones** (seção 15). Ao final de cada milestone, entregue: o que foi feito, como testar, o que ficou pendente, e atualize o README.
- Escreva **testes junto com cada funcionalidade**. Cobertura mínima 80%; CI falha abaixo disso.
- Se algo da especificação for ambíguo, **pergunte antes de codar**; não assuma.

---

## 1. Contexto e objetivo

**O Último Blog do Mundo** é um blog pessoal de **autor único** (Luiz Eduardo Araujo Brayner), com dois objetivos:

1. Blog real de artigos técnicos escritos em Markdown.
2. Projeto de portfólio para vagas de **DevOps/Back-end**, demonstrando Docker, CI/CD, segurança, testes e deploy em nuvem com custo zero.

O foco é **backend e infraestrutura**. O front deve ser funcional, acessível e responsivo (Bootstrap); refinamento estético fica para uma fase futura.

---

## 2. Escopo

**Dentro do escopo**

- Site público: home, detalhe do post, listagem por tag, busca, página “Sobre”, RSS, sitemap, `robots.txt`, 404/500 customizadas.
- Painel administrativo customizado (fora do Django admin) em URL secreta, com login, 2FA TOTP, dashboard e CRUD de posts/tags/mídia/SiteConfig.
- Markdown com syntax highlight, sanitização e cache de HTML.
- i18n da interface (PT-BR padrão, EN em `/en/`) e tradução opcional de posts.
- Tema claro/escuro.
- SQLite local (sem Docker), PostgreSQL (Supabase em produção; container local via Docker), Storage de imagens no Supabase, Redis para cache/sessões.
- Dockerfile multi-stage, `docker-compose` local, pipeline CI/CD no GitHub Actions, deploy automático no merge da `main`.
- Testes, lint, pre-commit, Dependabot, scan de vulnerabilidades.

**Fora do escopo (não implementar)**

- Comentários, cadastro público, múltiplos autores, newsletter, formulário de contato.
- Kubernetes, Helm, Argo CD, GitOps, HPA, service mesh.
- Prometheus/Grafana/Loki (será projeto separado).
- Django admin (`admin.site.urls`).
- E-commerce, API pública, app mobile.
- Analytics, Sentry, contador de views, `django-prometheus`.
- Domínio próprio.

---

## 3. Stack

- **Linguagem/Framework**: Python 3.12 + Django 6.1.x.
- **Banco**: SQLite (local sem Docker) e PostgreSQL 16 (produção/Supabase; local via Docker). Driver: `psycopg[binary]` (psycopg3, recomendado pelo Django 6.x).
- **Cache/Sessões**: Redis 7 (local via Docker; Upstash em produção).
- **Armazenamento de mídia**: Supabase Storage via API S3-compatível (`django-storages[s3]` + `boto3`).
- **Servidor WSGI**: Gunicorn.
- **Estáticos**: WhiteNoise.
- **Front**: Bootstrap 5.3 (CDN no dev; local em produção), `django-crispy-forms` + `crispy-bootstrap5`, `django-bootstrap5`.
- **Markdown**: `markdown` (extensões `fenced_code`, `codehilite`, `tables`, `toc`, `attr_list`), `Pygments`, `nh3` para sanitização.
- **Config**: `django-environ`.
- **Segurança**: `django-axes`, `django-otp` + `qrcode`, `argon2-cffi`.
- **Qualidade**: `pytest`, `pytest-django`, `pytest-cov`, `Ruff` (lint + format), `pre-commit`.
- **CI/CD**: GitHub Actions, Docker Buildx, GHCR, Trivy, `pip-audit`, Dependabot.
- **Deploy**: Render free web service (Dockerfile + deploy hook).

---

## 4. Arquitetura e estrutura

Projeto Django organizado por domínio, settings em camadas, requirements separados.

```
o-ultimo-blog-do-mundo/
├── config/
│   ├── settings/{base,local,production}.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── core/        # SiteConfig, healthcheck, views institucionais, templatetags
│   ├── blog/        # Post, Tag, views públicas, busca, RSS, sitemap
│   ├── dashboard/   # login, 2FA, CRUD, media library
│   └── accounts/    # usuário admin (customização mínima)
├── templates/
├── static/
├── locale/{pt_BR,en}/
├── requirements/{base,local,production}.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .pre-commit-config.yaml
├── pyproject.toml
├── backups/          # ignorada no Git
└── README.md
```

Regras:

- `config/settings/base.py` contém o comum; `local.py` e `production.py` importam de `base`.
- Toda configuração sensível via env: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DATABASE_URL`, `REDIS_URL`, `ADMIN_PATH`, credenciais Supabase, `TOTP_ISSUER`, `SITE_NAME`.
- `production.py`: `DEBUG=False`, `ALLOWED_HOSTS` explícito, cookies seguros, HSTS, redirect SSL, CSP básica compatível com Bootstrap local e Pygments.
- `local.py`: SQLite opcional, `DEBUG=True`, e-mail em console.

---

## 5. Modelo de dados

**`core.SiteConfig`** (singleton)

- `site_title_pt`, `site_title_en`, `tagline_pt`, `tagline_en`, `about_pt`, `about_en`, `email`, `github_url`, `linkedin_url`, `portfolio_url`, `default_og_image`.
- Defaults: `site_title_pt="O Último Blog do Mundo"`, `site_title_en="The Last Blog in the World"`.

**`blog.Tag`**

- `name`, `slug` (único), `created_at`.

**`blog.Post`**

- `title`, `slug` (único, gerado de `title` com `slugify`, editável, máx. 200), `summary`, `content_md`, `content_html` (gerado no save), `cover_image` (opcional), `tags` (M2M), `language` (`pt`/`en`), `translation_of` (FK para `Post`, opcional), `status` (`draft`/`published`), `published_at` (opcional), `created_at`, `updated_at`, `meta_description`, `reading_time`.
- Regras: post publicado exige `published_at`; `content_html` regenerado a cada save; sanitização obrigatória; tradução só aponta para post de outro idioma; slug único por idioma.
- Ordenação padrão: `-published_at`.

**`blog.MediaAsset`**

- `file` (Supabase Storage), `alt_text` (obrigatório), `uploaded_at`, `uploaded_by`.

Sem modelos de comentário, categoria ou usuário público.

---

## 6. Funcionalidades públicas

- **Home**: posts publicados no idioma atual, paginação de 10, capa, título, resumo, data, tags e reading time.
- **Detalhe do post**: HTML renderizado, tags, data, reading time, botão de tema, link para tradução quando existir, meta tags SEO, Open Graph, Twitter Card, JSON-LD `Article`.
- **Listagem por tag**: posts publicados com a tag, paginados.
- **Busca**: `icontains` em `title` e `content_md`, somente publicados e no idioma atual; resultados paginados.
- **Sobre**: conteúdo de `SiteConfig` no idioma atual.
- **RSS**: `django.contrib.syndication`, resumo + link, por idioma.
- **Sitemap**: `django.contrib.sitemaps` (home, posts, tags, páginas estáticas).
- **`robots.txt`**: aponta para o sitemap e bloqueia o caminho do dashboard.
- **404/500** customizadas.
- **Tema claro/escuro**: Bootstrap 5.3 (`data-bs-theme`), preferência em `localStorage`, respeitando `prefers-color-scheme` no primeiro acesso.
- **Acessibilidade**: HTML semântico, `alt` obrigatório, foco visível, contraste adequado, navegação por teclado. Documentar no README.
- **Idioma**: seletor PT/EN no header; troca mantém página equivalente quando possível.

---

## 7. Dashboard administrativo

- Acessível apenas em `/{ADMIN_PATH}/` (env; em dev `/gestao/`). Não aparece em menus, sitemap ou robots.
- **Sem Django admin**: não incluir `admin.site.urls`.
- **Login**: formulário customizado, `django-axes` para bloqueio após tentativas falhas, sessão em Redis com expiração de 8h, Argon2.
- **2FA TOTP** obrigatório; QR code no primeiro acesso; códigos de recuperação documentados.
- **Dashboard**: lista de posts com filtros por status/idioma, busca, ações de criar/editar/excluir, alternar rascunho/publicado, preview de Markdown.
- **Editor de post**: campos da seção 5, upload de capa, seleção de tags, escolha de idioma, vínculo de tradução, preview renderizado.
- **Media library**: upload, listagem, cópia de URL, exclusão no Supabase Storage.
- **Tags**: CRUD simples.
- **SiteConfig**: edição dos campos em PT e EN.
- **Logout** e troca de senha (sem e-mail; via formulário autenticado).
- **Segurança**: todas as views exigem login; CSRF em todos os formulários; `X-Frame-Options: DENY`; rate limit em ações sensíveis; logs de login.

---

## 8. Internacionalização

- `LANGUAGE_CODE='pt-br'`, `LANGUAGES=[('pt-br','Português'),('en','English')]`, `LocaleMiddleware`, `i18n_patterns` com `/en/` para inglês.
- Textos da interface via `{% trans %}` e arquivos `.po` em `locale/`.
- `SiteConfig` com campos `_pt` e `_en`.
- Posts: `language` + `translation_of`. Post em EN sem tradução exibe aviso e link para o original PT (e vice-versa).
- Slugs independentes por post/tradução.
- Documentar no README como adicionar novos textos traduzíveis.

---

## 9. Armazenamento e mídia

- **Local sem Docker**: SQLite + filesystem.
- **Local com Docker**: PostgreSQL + Redis em containers; mídia em filesystem ou bucket de dev no Supabase (via env).
- **Produção**: PostgreSQL do Supabase (usar connection pooler; `DISABLE_SERVER_SIDE_CURSORS=True` e `conn_max_age` adequado), Redis do Upstash, Storage do Supabase via `django-storages[s3]` com endpoint S3 do projeto.
- Buckets: `media` público para leitura; upload restrito ao dashboard.
- Validar tipo/tamanho de imagem no upload; `alt_text` obrigatório.
- Documentar variáveis de ambiente necessárias.

---

## 10. Segurança

- `DEBUG=False` em produção; `ALLOWED_HOSTS` explícito; `SECRET_KEY` só em env.
- Cookies `Secure`, `HttpOnly`, `SameSite=Lax`; `SECURE_SSL_REDIRECT=True`; HSTS; `SECURE_PROXY_SSL_HEADER` conforme host.
- CSRF habilitado; `X_FRAME_OPTIONS=DENY`; `Referrer-Policy`.
- CSP básica em produção compatível com Bootstrap local e Pygments (sem CDN em produção).
- Argon2 como hasher primário.
- `django-axes` com limite e bloqueio temporário.
- 2FA TOTP obrigatório.
- Caminho do dashboard via env, nunca hardcoded; `robots.txt` bloqueia; nenhum link público.
- Dependabot para `pip`, Actions e Docker; `pip-audit` e Trivy no CI; `gitleaks` opcional no pre-commit.
- Nunca logar senhas, tokens ou conteúdo de `.env`.

---

## 11. DevOps

**Dockerfile**

- Multi-stage com `python:3.12-slim`.
- Estágio builder instala dependências de build; estágio final copia apenas o necessário.
- Usuário non-root (`appuser`).
- `collectstatic` no build; WhiteNoise serve estáticos.
- `HEALTHCHECK` chamando `/healthz`.
- `Gunicorn` como entrypoint, workers configuráveis por env.
- `.dockerignore` adequado.

**docker-compose local**

- Serviços: `web`, `db` (Postgres 16), `redis` (Redis 7).
- Volumes para dados; `.env` para configuração; healthchecks; `depends_on` com condição de saúde.
- Comando documentado para rodar sem Docker usando SQLite.

**Pipeline GitHub Actions** (`.github/workflows/ci.yml`)

1. **lint**: Ruff check + format check.
2. **test**: pytest com coverage; serviços Postgres e Redis; falha se cobertura < 80%.
3. **security**: `pip-audit`, Trivy filesystem, `gitleaks` (opcional).
4. **build**: Docker Buildx, push para `ghcr.io/<usuario>/o-ultimo-blog-do-mundo` com tags `sha` e `latest`, Trivy na imagem.
5. **deploy**: apenas em `main`, chama o deploy hook do Render via secret; exige lint/test/security/build aprovados.

- Concorrência para cancelar execuções antigas; cache de pip e Docker.
- GitHub Environments: `production` com secrets e aprovação opcional.
- Dependabot semanal para pip, Actions e Docker.

**Deploy**

- Render free web service criado a partir do Dockerfile do repositório; nome do serviço `o-ultimo-blog-do-mundo`; domínio `o-ultimo-blog-do-mundo.onrender.com`.
- Variáveis de ambiente no Render: todas da seção 10 + `ADMIN_PATH`, `DATABASE_URL`, `REDIS_URL`, credenciais Supabase.
- Deploy automático via deploy hook chamado pelo CI após merge na `main`.
- Healthcheck `/healthz` validando DB e cache.
- Documentar rollback (redeploy de tag anterior) e como rodar migrações no deploy.
- Workflow agendado de “keep-alive” para evitar pausa do Supabase free tier.

**Ambientes**

- `local`: SQLite ou compose, `DEBUG=True`, e-mail em console.
- `production`: Supabase + Upstash + Render, `DEBUG=False`, tudo via env.
- `.env.example` com todas as variáveis comentadas.

**Backups e migrações**

- Migrações com `django-migrations` padrão; comando documentado no deploy.
- Backup documentado: `pg_dump` do Supabase + exports locais em `backups/` (ignorado no Git); procedimento de restauração descrito no README.

---

## 12. Qualidade e testes

- `pytest-django` com testes de modelos, views públicas, dashboard, i18n, busca, RSS, sitemap e healthcheck.
- Cobertura mínima 80% (falha no CI abaixo disso).
- Ruff para lint e format; config em `pyproject.toml`.
- `pre-commit` com Ruff, verificação de YAML, trailing whitespace, fim de arquivo e detecção de segredos.
- Testes de segurança: login inválido bloqueado por `django-axes`; acesso ao dashboard sem login redireciona; 2FA obrigatório; CSRF ativo.
- Documentar como rodar testes localmente e no Docker.

---

## 13. Documentação (README)

Deve conter:

- Descrição e objetivo de portfólio.
- Diagrama de arquitetura (app, Supabase, Redis, Render, GHCR).
- Stack e decisões técnicas (por que Django, por que Supabase, por que sem Kubernetes).
- Estrutura de pastas.
- Como rodar localmente com e sem Docker.
- Variáveis de ambiente (`.env.example`).
- Como rodar testes, lint e pre-commit.
- Pipeline CI/CD explicada passo a passo.
- Como fazer deploy, rollback, migrações e backups.
- Segurança: o que está implementado e o que ficou de fora.
- Limitações conhecidas (free tiers, pausa do Supabase, spin-down do Render).
- Screenshots das telas principais.
- Link da demo.
- Roadmap futuro (Kubernetes, observabilidade, e-commerce).

---

## 14. Critérios de aceite

1. Site público funciona em PT e EN, com troca de idioma e tema claro/escuro.
2. Posts em Markdown renderizam com syntax highlight, sanitização e cache.
3. Busca, paginação, RSS, sitemap e `robots.txt` funcionam.
4. Dashboard em URL secreta exige login + 2FA; CRUD de posts, tags, mídia e SiteConfig funciona.
5. Nenhuma rota do Django admin está exposta.
6. `docker-compose up` sobe web + Postgres + Redis; aplicação responde em `/healthz`.
7. Pipeline no GitHub Actions passa lint, testes com cobertura ≥ 80%, security scans, build e push para GHCR.
8. Merge na `main` dispara deploy automático no Render; aplicação sobe com `DEBUG=False`.
9. Produção usa Supabase (DB + Storage) e Upstash Redis; nenhum segredo no repositório.
10. README completo com diagrama, comandos, screenshots e link da demo.
11. Dependabot e pre-commit ativos.
12. Custo total permanece zero nos free tiers escolhidos.

---

## 15. Milestones

1. **Fundação**: repositório `o-ultimo-blog-do-mundo`, estrutura, settings em camadas, `.env.example`, Ruff, pre-commit, CI esqueleto.
2. **Domínio público**: modelos, i18n, Markdown, home, post, tag, busca, sobre, RSS, sitemap, SEO, tema.
3. **Dashboard**: login, 2FA, rate limit, CRUD de posts/tags/mídia/SiteConfig, preview.
4. **Docker**: Dockerfile multi-stage, compose com Postgres e Redis, healthcheck, testes em container.
5. **Produção**: Supabase (DB + Storage), Upstash, Render, pipeline completa, Dependabot, keep-alive.
6. **Identidade visual & Mobile**: tipografia, paleta de cores, tema claro/escuro refinado, front-end responsivo para celulares e dispositivos móveis.
7. **Polimento**: acessibilidade (WCAG AA), testes finais, README, screenshots, revisão de segurança e release v1.0.0.

---

## 16. Premissas confirmadas pelo usuário

- Autor único; login com credenciais para postar.
- Tags (não categorias).
- Sem comentários.
- Status apenas `draft` e `published`.
- Busca, paginação, RSS, sitemap, SEO: sim.
- Markdown: sim.
- Armazenamento de mídia no Supabase.
- Interface bilíngue (PT-BR/EN); post traduzido opcionalmente.
- Tema claro/escuro.
- Dashboard customizado, URL secreta, sem Django admin.
- 2FA TOTP.
- SQLite local, PostgreSQL em produção.
- Redis para cache/sessões.
- Backup e migrações documentados.
- Bootstrap 5 (dev e prod).
- `crispy-forms` + `django-bootstrap5` juntos.
- Acessibilidade como requisito.
- Dockerfile multi-stage, non-root, healthcheck.
- Compose local com Postgres e Redis.
- Sem deploy de imagem em registry pago (GHCR).
- CI/CD completo, deploy automático no merge da `main`.
- GitHub Environments com secrets.
- Sem Kubernetes, GitOps, Helm.
- Observabilidade é projeto separado; aqui só `/healthz` e logs.
- Testes, lint, pré-commit, Dependabot, Trivy: sim.
- README completo.
- Objetivo: portfólio DevOps + blog real.
- Custo zero.

---

## 17. Fluxo de trabalho do agente (ver AGENTS.md)

- Milestones, commits, branches e tags estão definidos em `AGENTS.md`.
- Convenções de commit e estilo estão em `CONTRIBUTING.md`.
- O `AGENTS.md` tem precedência sobre este documento apenas em questões de processo; para escopo e requisitos, este documento prevalece.

## 18. Encerramento do projeto

Ao concluir o Milestone 7, o agente deve:

1. Garantir que o `README.md` está completo conforme a seção 13.
2. Gerar/atualizar `CHANGELOG.md` com a entrada da versão `v1.0.0`.
3. Criar a tag anotada `v1.0.0` no commit final.
4. Executar `gh repo edit --description "<descrição>" --homepage "<url-da-demo>"` (se `gh` estiver autenticado).
5. Publicar um GitHub Release `v1.0.0` com o conteúdo do `CHANGELOG.md`.

---

Se algo não estiver claro na execução, **pergunte antes de implementar**. Este documento é a fonte única de verdade do projeto.
