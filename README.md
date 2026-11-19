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
├── pyproject.toml             # Ruff, pytest, coverage config
├── .pre-commit-config.yaml    # Pre-commit hooks
├── .github/
│   ├── workflows/ci.yml       # Pipeline CI/CD
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
# Acessar http://localhost:8000/healthz — deve retornar "ok"
```

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
2. **test** — pytest com cobertura ≥ 80%
3. **security** — *(habilitado no Milestone 5)*
4. **build** — *(habilitado no Milestone 4)*
5. **deploy** — *(habilitado no Milestone 5)*

## 📌 Variáveis de ambiente

Veja o arquivo [`.env.example`](.env.example) para a lista completa com documentação.

## 🗺️ Roadmap (Milestones)

- [x] **M1 — Fundação**: estrutura, settings, CI esqueleto
- [x] **M2 — Domínio público**: modelos, i18n, Markdown, views, SEO
- [x] **M3 — Dashboard**: login, 2FA, CRUD, preview *(atual)*
- [ ] **M4 — Docker**: Dockerfile, compose, healthcheck
- [ ] **M5 — Produção**: Supabase, Upstash, Render, CI completo
- [ ] **M6 — Polimento**: acessibilidade, testes finais, screenshots

## 📄 Licença

MIT — veja [LICENSE](LICENSE).
