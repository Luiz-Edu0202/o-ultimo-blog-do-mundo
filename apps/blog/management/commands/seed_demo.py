from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.blog.models import Post, Tag
from apps.core.models import SiteConfig


class Command(BaseCommand):
    help = "Populate the database with realistic demo articles, tags and site configuration."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Iniciando povoamento de dados de demonstração..."))

        # 1. SiteConfig
        site_config = SiteConfig.get_solo()
        site_config.site_title_pt = "O Último Blog do Mundo"
        site_config.site_title_en = "The Last Blog in the World"
        site_config.tagline_pt = (
            "Transmissões técnicas do fim dos tempos // DevOps, Backend & Nuvem"
        )
        site_config.tagline_en = (
            "Technical transmissions from the end of times // DevOps, Backend & Cloud"
        )
        site_config.about_pt = (
            "Engenheiro de Software & DevOps focado em resiliência e automação em nuvem.\n\n"
            "Espaço dedicado a registrar investigações profundas sobre Linux, containers, "
            "CI/CD e sobrevivência de aplicações em ambientes hostis.\n\n"
            "Quando todos os servidores caírem, este será o último log de transmissão."
        )
        site_config.about_en = (
            "Software & DevOps Engineer focused on resilience and cloud automation.\n\n"
            "Dedicated space to logging deep investigations into Linux, containers, "
            "CI/CD, and application survival in hostile environments.\n\n"
            "When all servers fall, this will be the last transmission log remaining."
        )
        site_config.email = "luiz.brayner@example.com"
        site_config.github_url = "https://github.com/Luiz-Edu0202"
        site_config.linkedin_url = "https://linkedin.com/in/luizbrayner"
        site_config.portfolio_url = "https://github.com/Luiz-Edu0202/o-ultimo-blog-do-mundo"
        site_config.save()
        self.stdout.write(self.style.SUCCESS("✓ SiteConfig atualizado."))

        # 2. Tags
        tags_data = [
            ("DevOps", "devops"),
            ("Docker", "docker"),
            ("CI/CD", "ci-cd"),
            ("Python", "python"),
            ("PostgreSQL", "postgresql"),
            ("Linux", "linux"),
            ("Arquitetura", "arquitetura"),
        ]
        created_tags = {}
        for name, slug in tags_data:
            tag, _ = Tag.objects.get_or_create(name=name, defaults={"slug": slug})
            created_tags[name] = tag
        self.stdout.write(self.style.SUCCESS(f"✓ {len(created_tags)} Tags configuradas."))

        # 3. Posts
        now = timezone.now()

        # Post 1 (PT)
        p1_pt_content = (
            "## 01. // A Premissa da Escassez\n\n"
            "Projetar para o limite gratuito é o melhor teste de engenharia possível.\n\n"
            "Neste artigo, documentamos a arquitetura do **O Último Blog do Mundo**, "
            "desenhada para operar com **custo zero absoluto** sem abrir mão de segurança, "
            "CI/CD e cache distribuído.\n\n"
            "### Diagrama Conceitual\n\n"
            "```\n"
            "+-------------------------------------------------------+\n"
            "|  CLIENTE / NAVEGADOR (HTTPS + HSTS + CSP)             |\n"
            "+---------------------------+---------------------------+\n"
            "                            |\n"
            "                            v\n"
            "+-------------------------------------------------------+\n"
            "|  RENDER WEB SERVICE (Gunicorn + WhiteNoise + Docker)  |\n"
            "+-------------+---------------------------+-------------+\n"
            "              |                           |\n"
            "              v                           v\n"
            "+---------------------------+ +-------------------------+\n"
            "|  SUPABASE (PostgreSQL 16) | |  UPSTASH (Redis 7)      |\n"
            "|  Pooler PgBouncer         | |  Cache L1 + Sessões 8h  |\n"
            "+---------------------------+ +-------------------------+\n"
            "```\n\n"
            "## 02. // Docker Multi-Stage\n\n"
            "```dockerfile\n"
            "FROM python:3.12-slim AS builder\n"
            "WORKDIR /app\n"
            "RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev\n"
            "COPY requirements/production.txt .\n"
            "RUN pip install --prefix=/install -r production.txt\n\n"
            "FROM python:3.12-slim AS final\n"
            "WORKDIR /app\n"
            "COPY --from=builder /install /usr/local\n"
            "COPY . .\n"
            "RUN python manage.py collectstatic --noinput\n"
            "USER appuser\n"
            'CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]\n'
            "```\n\n"
            "> **Transmissão**: Arquitetura validada e prontidão operacional comprovada.\n"
        )
        p1_pt, _ = Post.objects.get_or_create(
            slug="arquitetura-resiliente-deploy-custo-zero",
            language="pt-br",
            defaults={
                "title": "Arquitetura Resiliente: Deploy em Nuvem com Custo Zero",
                "summary": (
                    "Como orquestrar Django, PostgreSQL gerenciado, Redis e Docker "
                    "em free tiers sem comprometer segurança ou confiabilidade."
                ),
                "status": "published",
                "published_at": now - timezone.timedelta(days=2),
                "content_md": p1_pt_content,
            },
        )
        p1_pt.tags.set([created_tags["DevOps"], created_tags["Docker"], created_tags["CI/CD"]])

        # Post 1 (EN translation)
        p1_en_content = (
            "## 01. // The Scarcity Principle\n\n"
            "Designing for free tiers is the ultimate engineering challenge: extracting "
            "maximum stability, automated security, and performance under strict constraints.\n\n"
            "### High-level Topology\n\n"
            "```\n"
            "+-------------------------------------------------------+\n"
            "|  CLIENT BROWSER (HTTPS + HSTS + CSP)                  |\n"
            "+---------------------------+---------------------------+\n"
            "                            |\n"
            "                            v\n"
            "+-------------------------------------------------------+\n"
            "|  RENDER WEB SERVICE (Gunicorn + WhiteNoise + Docker)  |\n"
            "+-------------+---------------------------+-------------+\n"
            "              |                           |\n"
            "              v                           v\n"
            "+---------------------------+ +-------------------------+\n"
            "|  SUPABASE (PostgreSQL 16) | |  UPSTASH (Redis 7)      |\n"
            "|  PgBouncer Pooling        | |  L1 Cache + 8h Sessions |\n"
            "+---------------------------+ +-------------------------+\n"
            "```\n\n"
            "## 02. // Code Sample\n\n"
            "```python\n"
            "from django.db import connection\n"
            "from django.core.cache import cache\n\n"
            "def healthz(request):\n"
            "    db_ok = connection.ensure_connection() is None\n"
            '    cache_ok = cache.set("t", "1", 5) and cache.get("t") == "1"\n'
            "    return JsonResponse({'status': 'ok' if db_ok and cache_ok else 'err'})\n"
            "```\n"
        )
        p1_en, _ = Post.objects.get_or_create(
            slug="resilient-architecture-zero-cost-deployment",
            language="en",
            defaults={
                "title": "Resilient Architecture: Zero-Cost Cloud Deployment",
                "summary": (
                    "How to orchestrate Django, managed PostgreSQL, Redis, and Docker "
                    "on free tiers without sacrificing security or reliability."
                ),
                "status": "published",
                "published_at": now - timezone.timedelta(days=2),
                "translation_of": p1_pt,
                "content_md": p1_en_content,
            },
        )
        p1_en.tags.set([created_tags["DevOps"], created_tags["Docker"]])

        # Post 2 (PT)
        p2_pt_content = (
            "## 01. // Por que abandonar o `/admin/` padrão?\n\n"
            "O Django Admin tradicional é alvo frequente de varreduras automatizadas.\n\n"
            "Nesta aplicação:\n"
            "1. **Sem Django admin**: `admin.site.urls` foi removido do roteador.\n"
            "2. **Rota secreta configurável**: Caminho de gestão via env (`ADMIN_PATH`).\n"
            "3. **Argon2**: Hasher primário de senhas contra ataques por força bruta.\n"
            "4. **Proteção de IP**: `django-axes` bloqueia tentativas sequenciais inválidas.\n"
            "5. **2FA Obrigatório**: Login exige código TOTP sincronizado.\n\n"
            "## 02. // Hasher no Settings\n\n"
            "```python\n"
            "PASSWORD_HASHERS = [\n"
            '    "django.contrib.auth.hashers.Argon2PasswordHasher",\n'
            '    "django.contrib.auth.hashers.PBKDF2PasswordHasher",\n'
            "]\n"
            "```\n"
        )
        p2_pt, _ = Post.objects.get_or_create(
            slug="hardening-seguranca-autenticacao-totp",
            language="pt-br",
            defaults={
                "title": "Hardening no Django: Autenticação Segura com 2FA TOTP",
                "summary": (
                    "Substituindo o painel admin convencional por uma rota secreta "
                    "reforçada com Argon2, django-axes e códigos OTP."
                ),
                "status": "published",
                "published_at": now - timezone.timedelta(days=5),
                "content_md": p2_pt_content,
            },
        )
        p2_pt.tags.set([created_tags["Python"], created_tags["Linux"], created_tags["DevOps"]])

        # Post 3 (PT)
        p3_pt_content = (
            "## 01. // Além dos Templates Genéricos\n\n"
            "Inspirado no design industrial de estúdios como *Base Design* e *Visuelle.co.uk*:\n\n"
            "| Pilar | Abordagem |\n"
            "|---|---|\n"
            "| **Tipografia** | Space Grotesk, Inter e JetBrains Mono |\n"
            "| **Cores** | Fundo abissal `#0A0C10` com acento fosforescente `#00E5CC` |\n"
            "| **Monospace** | Badges bracketed `[ tag ]`, prefixos `//` e footer prompt |\n"
            "| **Contraste** | 100% aderente a WCAG AA em ambos os modos claro e escuro |\n\n"
            "## 02. // Tokens CSS Nativos\n\n"
            "```css\n"
            ":root, :root[data-bs-theme='dark'] {\n"
            "  --bg-void: #0A0C10;\n"
            "  --bg-surface: #12151C;\n"
            "  --text-primary: #E8ECF1;\n"
            "  --accent: #00E5CC;\n"
            "}\n"
            "```\n"
        )
        p3_pt, _ = Post.objects.get_or_create(
            slug="estetica-terminal-e-identidade-retro-futurista",
            language="pt-br",
            defaults={
                "title": "Estética Terminal: Identidade Retrô-Futurista na Web",
                "summary": (
                    "Explorando tipografia de precisão com Space Grotesk e JetBrains Mono, "
                    "paletas escuras abissais e brutalismo funcional."
                ),
                "status": "published",
                "published_at": now - timezone.timedelta(days=8),
                "content_md": p3_pt_content,
            },
        )
        p3_pt.tags.set([created_tags["Arquitetura"], created_tags["Linux"], created_tags["Python"]])

        self.stdout.write(self.style.SUCCESS("✓ 4 Artigos de demonstração criados/atualizados!"))
        self.stdout.write(self.style.SUCCESS("Povoamento de demonstração concluído com êxito!"))
