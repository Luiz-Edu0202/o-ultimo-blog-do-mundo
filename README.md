# O Último Blog do Mundo

> Blog pessoal de artigos técnicos + projeto de portfólio DevOps/Back-end.

[![CI](https://github.com/Luiz-Edu0202/o-ultimo-blog-do-mundo/actions/workflows/ci.yml/badge.svg)](https://github.com/Luiz-Edu0202/o-ultimo-blog-do-mundo/actions/workflows/ci.yml)

## 📋 Sobre o projeto

**O Último Blog do Mundo** é o blog pessoal de Luiz Eduardo Araujo Brayner, com dois objetivos:

1. **Blog real** de artigos técnicos escritos em Markdown.
2. **Projeto de portfólio** para vagas de DevOps/Back-end, demonstrando Docker, CI/CD, segurança, testes e deploy em nuvem com custo zero.

## 🛠️ Stack

| Camada | Tecnologia |
|--------|-----------|
| Linguagem/Framework | Python 3.12 + Django 6.1.x |
| Banco de dados | SQLite (dev local) / PostgreSQL 16 (prod via Supabase) |
| Cache/Sessões | Redis 7 (Upstash em prod) |
| Mídia | Supabase Storage (S3-compatível) |
| Servidor WSGI | Gunicorn |
| Estáticos | WhiteNoise |
| Front-end | Bootstrap 5.3, crispy-forms |
| Qualidade | Ruff, pytest, pre-commit |
| CI/CD | GitHub Actions, Docker, GHCR |
| Deploy | Render (free tier) |

### Decisões técnicas

- **Django 6.1.x** (última estável, nov/2026) em vez do 5.x original da spec — suporte ativo de segurança até ~2028, stack atualizada para portfólio.
- **psycopg3** (`psycopg[binary]`) como driver PostgreSQL — recomendado pelo Django 6.x, melhor performance e tipagem.
- **Sem Django admin** — dashboard customizado em URL secreta para demonstrar skills de front-end e segurança.
- **Sem Kubernetes** — foco em demonstrar Docker + CI/CD + deploy simples; orquestração será projeto separado.

## 📁 Estrutura do projeto

```
o-ultimo-blog-do-mundo/
├── config/                    # Configuração Django
│   ├── settings/
│   │   ├── base.py            # Settings compartilhados
│   │   ├── local.py           # Dev: SQLite, DEBUG=True
│   │   └── production.py      # Prod: Postgres, Redis, HTTPS
│   ├── urls.py                # URL root
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── core/                  # SiteConfig, healthcheck, utils
│   ├── blog/                  # Posts, tags, views públicas
│   ├── dashboard/             # Painel admin customizado
│   └── accounts/              # Gestão de usuário admin
├── templates/                 # Templates globais
├── static/                    # Arquivos estáticos
├── locale/{pt_BR,en}/         # Arquivos de tradução
├── tests/                     # Testes do projeto
├── requirements/
│   ├── base.txt               # Deps compartilhadas
│   ├── local.txt              # Deps de dev
│   └── production.txt         # Deps de produção
├── docs/                      # Documentação operacional
│   └── backup_restore.md      # Backup, restore e rollback
├── pyproject.toml             # Ruff, pytest, coverage config
├── .pre-commit-config.yaml    # Pre-commit hooks
├── .github/
│   ├── workflows/
│   │   ├── ci.yml             # Pipeline CI/CD
│   │   ├── keep_alive.yml     # Ping periódico (Render + Supabase)
│   │   └── backup.yml         # Backup semanal do banco
│   └── dependabot.yml         # Atualização automática de deps
├── .env.example               # Variáveis de ambiente (template)
└── backups/                   # Backups locais (ignorado no Git)
```

## 🚀 Como rodar localmente

### Pré-requisitos

- Python 3.12+
- Git

### Setup

```bash
# Clonar o repositório
git clone https://github.com/Luiz-Edu0202/o-ultimo-blog-do-mundo.git
cd o-ultimo-blog-do-mundo

# Criar e ativar virtualenv
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Instalar dependências de desenvolvimento
pip install -r requirements/local.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env conforme necessário (os defaults funcionam para dev)

# Rodar migrações (ainda sem modelos customizados no M1)
python manage.py migrate

# Verificar que tudo funciona
python manage.py check
```

### Verificar o healthcheck

```bash
python manage.py runserver
# Acessar http://localhost:8000/healthz — retorna JSON com status do banco e cache:
# {"status": "ok", "checks": {"db": "ok", "cache": "ok"}}
```

## 🐳 Rodando com Docker

### Pré-requisitos

- Docker 24+ e Docker Compose v2

### Setup

```bash
# Copie o .env e ajuste as variáveis (os defaults já funcionam para o compose local)
cp .env.example .env

# Suba todos os serviços (web + PostgreSQL + Redis)
docker compose up --build

# Em outro terminal: aplique as migrações
docker compose exec web python manage.py migrate

# Acesse:
# http://localhost:8000        — site público
# http://localhost:8000/healthz — healthcheck (retorna JSON com status de DB e Redis)
```

### Comandos úteis

```bash
# Parar containers e remover volumes
docker compose down -v

# Rodar testes dentro do container
docker compose run --rm web pytest --cov --cov-report=term-missing

# Criar superusuário
docker compose exec web python manage.py createsuperuser

# Ver logs
docker compose logs -f web

# Usar o Makefile (atalhos)
make up          # docker compose up --build
make down        # docker compose down -v
make migrate     # migrações dentro do container
make test-docker # testes dentro do container
make shell       # Django shell dentro do container
```

### Variáveis do Compose

As variáveis `DATABASE_URL` e `REDIS_URL` são injetadas automaticamente pelo `docker-compose.yml` apontando para os containers internos. Para personalizar o banco local, edite no `.env`:

```
POSTGRES_DB=blog
POSTGRES_USER=blog
POSTGRES_PASSWORD=blog
```

---

## ✅ Qualidade de código

```bash
# Lint
ruff check .

# Format check
ruff format --check .

# Testes com cobertura
pytest --cov --cov-report=term-missing

# Instalar pre-commit hooks (uma vez)
pre-commit install

# Rodar pre-commit em todos os arquivos
pre-commit run --all-files
```

## 🔄 Pipeline CI/CD

O GitHub Actions executa em push/PR para `main`:

1. **lint** — Ruff check + format check
2. **test** — pytest com cobertura ≥ 80% (com PostgreSQL e Redis via services)
3. **security** — pip-audit + Trivy filesystem scan
4. **build** — Docker Buildx → push GHCR (`:sha` + `:latest`) → Trivy scan da imagem
5. **deploy** — Render deploy hook (dispara redeploy automático)

### Workflows adicionais

- **keep_alive** — cron a cada 3 h: pinga `https://o-ultimo-blog-do-mundo.onrender.com/healthz` para evitar dormência do Render e inatividade do Supabase.
- **backup** — cron semanal: executa `pg_dump` do Supabase e faz upload do artefato para o GitHub Actions.

## 🚀 Produção — Supabase, Upstash & Render

### Serviços utilizados (todos free tier)

| Serviço | Função | Variáveis de ambiente |
|---------|--------|-----------------------|
| **Supabase** | PostgreSQL 16 + Storage S3 | `DATABASE_URL`, `SUPABASE_S3_ENDPOINT`, `SUPABASE_S3_ACCESS_KEY`, `SUPABASE_S3_SECRET_KEY`, `SUPABASE_STORAGE_BUCKET` |
| **Upstash** | Redis 7 (cache + sessões) | `REDIS_URL` |
| **Render** | Web Service (Docker) | `RENDER_DEPLOY_HOOK_URL` (GitHub Secret) |

### Como fazer deploy

1. Crie os serviços no Supabase, Upstash e Render (todos free tier).
2. No painel do **Render**, configure como Web Service apontando para o repositório GitHub ou use o deploy hook.
3. Configure as variáveis de ambiente no Render (veja `.env.example` para a lista completa).
4. Adicione `RENDER_DEPLOY_HOOK_URL` como secret no GitHub Actions.
5. A cada push na `main`, o CI faz build → push GHCR → dispara deploy no Render.

### Backup, restore e rollback

Veja a documentação completa em [`docs/backup_restore.md`](docs/backup_restore.md).

## 📌 Variáveis de ambiente

Veja o arquivo [`.env.example`](.env.example) para a lista completa com documentação.

## 🗺️ Roadmap (Milestones)

- [x] **M1 — Fundação**: estrutura, settings, CI esqueleto
- [x] **M2 — Domínio público**: modelos, i18n, Markdown, views, SEO
- [x] **M3 — Dashboard**: login, 2FA, CRUD, preview
- [x] **M4 — Docker**: Dockerfile multi-stage, compose, healthcheck, CI build
- [x] **M5 — Produção**: Supabase, Upstash, Render, CI completo *(atual)*
- [ ] **M6 — Polimento**: acessibilidade, testes finais, screenshots

## 📄 Licença

MIT — veja [LICENSE](LICENSE).
