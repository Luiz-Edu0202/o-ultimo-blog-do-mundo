# 🚀 Publicação da Release v1.0.0 — O Último Blog do Mundo

Este arquivo contém a descrição recomendada do repositório, metadados e os comandos prontos para publicar a release **v1.0.0** no GitHub.

---

## 📌 Metadados Recomendados para o Repositório

- **Descrição (About)**:  
  `Blog pessoal de engenharia técnica & portfólio DevOps/Back-end com Django 6, Docker, CI/CD, 2FA e custo zero em nuvem.`
- **Website / Homepage**:  
  `https://o-ultimo-blog-do-mundo.onrender.com`
- **Tópicos (Topics)**:  
  `django`, `python`, `devops`, `docker`, `ci-cd`, `github-actions`, `postgresql`, `redis`, `cyberpunk`, `terminal-ui`, `portfolio`

---

## ⚡ Comandos para Executar via GitHub CLI (`gh`)

Caso tenha o `gh` instalado e autenticado na sua máquina:

```bash
# 1. Enviar os commits e tags para o GitHub
git push origin main --tags

# 2. Atualizar a descrição e homepage do repositório
gh repo edit \
  --description "Blog pessoal de engenharia técnica & portfólio DevOps/Back-end com Django 6, Docker, CI/CD, 2FA e custo zero em nuvem." \
  --homepage "https://o-ultimo-blog-do-mundo.onrender.com"

# 3. Publicar o GitHub Release v1.0.0 com as notas do CHANGELOG
gh release create v1.0.0 \
  --title "v1.0.0 — O Último Blog do Mundo" \
  --notes-file CHANGELOG.md
```

---

## 🌐 Publicação Manual pelo Navegador

Se preferir fazer diretamente pela interface web do GitHub:

1. **Enviar as tags locais**:
   ```bash
   git push origin main --tags
   ```
2. Acesse a aba de Releases:  
   `https://github.com/Luiz-Edu0202/o-ultimo-blog-do-mundo/releases/new`
3. Selecione a tag: **`v1.0.0`**
4. Título da Release: **`v1.0.0 — O Último Blog do Mundo (Lançamento Oficial)`**
5. Cole as notas de lançamento abaixo:

```markdown
## O Último Blog do Mundo — Versão 1.0.0

Lançamento oficial do projeto **O Último Blog do Mundo**, um blog pessoal de artigos técnicos de autor único e projeto completo de portfólio para vagas sênior de DevOps e Back-end.

### Destaques da Release:
- **Linguagem & Framework**: Python 3.12 + Django 6.1.x
- **Infraestrutura em Nuvem (Custo Zero)**: Supabase PostgreSQL 16 (PgBouncer), Supabase Storage (S3), Upstash Redis 7 e Render Web Service
- **Identidade Visual**: Cyberpunk Suave / Terminal Retrô-Futurista com fontes locais (Space Grotesk, Inter, JetBrains Mono) e tema claro/escuro nativo
- **Segurança Reforçada**: Argon2, 2FA TOTP obrigatório, bloqueio de força bruta com django-axes, headers HSTS/CSP, sem Django admin exposto
- **Acessibilidade**: 100% aderente a WCAG AA com suporte a prefers-reduced-motion e contraste validado
- **DevOps & CI/CD**: Pipeline automatizado no GitHub Actions com pytest (104 testes, 92.7% de cobertura), scans de vulnerabilidade (Trivy + pip-audit), build multi-stage para GHCR e deploy hook no Render
- **Rotinas Operacionais**: Scripts de backup semanal, restore documentado e workflow keep-alive contra dormência de free tiers

Consulte o [README.md](https://github.com/Luiz-Edu0202/o-ultimo-blog-do-mundo/blob/main/README.md) e o [CHANGELOG.md](https://github.com/Luiz-Edu0202/o-ultimo-blog-do-mundo/blob/main/CHANGELOG.md) para a documentação completa.
```
