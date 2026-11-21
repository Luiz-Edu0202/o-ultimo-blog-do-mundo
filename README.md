# O Último Blog do Mundo

> [English Version](README.en.md) | **Português**

[![CI Pipeline](https://github.com/Luiz-Edu0202/o-ultimo-blog-do-mundo/actions/workflows/ci.yml/badge.svg)](https://github.com/Luiz-Edu0202/o-ultimo-blog-do-mundo/actions/workflows/ci.yml)
[![Keep-Alive](https://github.com/Luiz-Edu0202/o-ultimo-blog-do-mundo/actions/workflows/keep_alive.yml/badge.svg)](https://github.com/Luiz-Edu0202/o-ultimo-blog-do-mundo/actions/workflows/keep_alive.yml)
[![Backup Routine](https://github.com/Luiz-Edu0202/o-ultimo-blog-do-mundo/actions/workflows/backup.yml/badge.svg)](https://github.com/Luiz-Edu0202/o-ultimo-blog-do-mundo/actions/workflows/backup.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://www.python.org/)
[![Django 6.1](https://img.shields.io/badge/Django-6.1-green?logo=django)](https://www.djangoproject.com/)
[![Docker Multi-Stage](https://img.shields.io/badge/Docker-Multi--Stage-2496ED?logo=docker)](Dockerfile)

Bem-vindo ao **O Último Blog do Mundo**! Este é o meu blog pessoal e também um projeto de engenharia onde demonstro práticas modernas de desenvolvimento back-end, automação e infraestrutura em nuvem.

A ideia original deste projeto foi inspirada pelo desafio do [roadmap.sh — Personal Blog](https://roadmap.sh/projects/personal-blog).

---

## 💡 Sobre o Projeto & Objetivos

Criei este projeto com dois propósitos complementares:

1. **Meu Espaço Pessoal**: Um blog para publicar qualquer coisa que eu tiver vontade de compartilhar — pensamentos, ideias, reflexões, notas de livros, experiências do cotidiano e também artigos técnicos.
2. **Portfólio Prático de DevOps & Back-end**: Demonstrar na prática a construção de uma aplicação resiliente e segura, com Docker multi-stage, pipeline CI/CD automatizado, testes rigorosos (cobertura acima de 90%), autenticação 2FA TOTP e deploy em nuvem operando com **custo zero absoluto**.

Desenvolvido por **[Luiz](https://github.com/Luiz-Edu0202)** ([LinkedIn](https://linkedin.com/in/luizbrayner)).

---

## 📸 Demonstração Visual

O blog conta com uma identidade visual **Cyberpunk Suave / Terminal Retrô-Futurista**, com tipografia servida localmente e experiência mobile-first fluida:

| Visão Desktop (Dark Mode) | Leitura do Artigo (Tipografia & Código) |
|:---:|:---:|
| ![Home](docs/screenshots/01_home_dark.png) | ![Artigo](docs/screenshots/02_post_detail_dark.png) |

| Página 404 (ASCII Terminal) | Mobile Viewport (iPhone 14) |
|:---:|:---:|
| ![404](docs/screenshots/04_404_terminal.png) | ![Mobile](docs/screenshots/06_mobile_home_dark.png) |

---

## 🛠️ Stack Tecnológica

- **Linguagem & Framework**: Python 3.12 + Django 6.1.x
- **Banco de Dados**: SQLite (desenvolvimento local) / PostgreSQL 16 com PgBouncer no Supabase (produção)
- **Cache & Sessões**: Redis 7 gerenciado no Upstash com TLS (sessões administrativas isoladas de 8 horas)
- **Armazenamento de Mídia**: Supabase Storage via API S3 (`django-storages[s3]` + `boto3`)
- **Servidor WSGI & Estáticos**: Gunicorn + WhiteNoise (compressão Brotli/Gzip)
- **Design System & Tipografia**: Space Grotesk, Inter e JetBrains Mono servidos localmente (WOFF2)
- **Segurança**: Hasher Argon2, 2FA TOTP (`django-otp`), proteção por IP contra força bruta (`django-axes`), sem Django admin exposto
- **Qualidade & CI/CD**: Ruff, pytest (104 testes, 92.7% de cobertura), Trivy, pip-audit, Docker Buildx e GitHub Actions
- **Hospedagem**: Render Web Service (deploy automatizado a partir do Dockerfile multi-stage)

---

## ⚡ Como Rodar em 2 Minutos

### Opção 1: Com Docker Compose (Recomendado)

```bash
# 1. Copiar as variáveis de ambiente
cp .env.example .env

# 2. Subir os containers (Web + PostgreSQL 16 + Redis 7)
make up

# 3. Aplicar migrações e popular dados realistas de demonstração
make migrate
make seed-docker

# Acesse:
# Blog público: http://localhost:8000/
# Healthcheck:  http://localhost:8000/healthz
```

### Opção 2: Localmente sem Docker (SQLite)

```bash
# 1. Ativar o virtualenv e instalar dependências
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/local.txt

# 2. Configurar variáveis de ambiente e rodar
cp .env.example .env
make run
# Em outro terminal:
make seed
```

---

## 📚 Guias Especializados & Documentação Técnica

Para manter esta vitrine objetiva, dividi a documentação técnica aprofundada em guias dedicados:

- 🏛️ **[Arquitetura do Sistema](docs/architecture.md)**: Diagrama Mermaid completo de topologia, fluxo de dados e justificativas de cada decisão de engenharia.
- 🔒 **[Políticas & Hardening de Segurança](docs/security.md)**: Modelo de ameaças, Argon2, 2FA TOTP, bloqueio com django-axes, sanitização nh3 e auditorias do CI.
- 🛠️ **[Operações, Backups & Free Tiers](docs/operations.md)**: Procedimentos de backup com `pg_dump`, restauração de desastres, rollback e mitigação da dormência dos free tiers via `keep_alive.yml`.
- 🤝 **[Guia de Contribuição & Fluxo Git](CONTRIBUTING.md)**: Como contribuir, convenções de commits e o fluxo das branches `develop` ➔ `main`.

---

## 🗺️ Roadmap Futuro

- [ ] 🐛 **Correções contínuas de bugs e estabilização de edge cases**
- [ ] ⚡ **Otimizações contínuas de desempenho** (queries, profiling, caching em camadas e tempos de resposta)
- [ ] ☸️ **Orquestração em Kubernetes**: Implantação em cluster bare-metal / home-lab com k3s e GitOps (projeto complementar)
- [ ] 📊 **Observabilidade Completa**: Exportador Prometheus, dashboards no Grafana e agregação de logs com Loki
- [ ] 🌐 **CDN de Borda**: Configuração de distribuição global com cache dinâmico em edge workers

---

## 📄 Licença

Distribuído sob a licença MIT. Consulte [`LICENSE`](LICENSE) para mais detalhes.
