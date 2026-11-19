# Changelog

Todas as mudanças notáveis do projeto serão documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e o projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

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
