# Backup, Restore e Rollback

## Backup do banco (PostgreSQL — Supabase)

### Backup manual via `pg_dump`

```bash
# Substitua a DATABASE_URL pela connection string do Supabase (modo direto, não pooler)
pg_dump "$DATABASE_URL" --format=custom --no-owner --no-acl -f backup_$(date +%Y%m%d_%H%M%S).dump
```

### Backup automático (GitHub Actions)

O workflow `.github/workflows/backup.yml` executa semanalmente (todo domingo às 03:00 UTC):

1. Instala `postgresql-client` no runner.
2. Executa `pg_dump` usando a connection string armazenada em `secrets.DATABASE_URL`.
3. Faz upload do dump como artefato do GitHub Actions (retido por 30 dias).

Para disparar manualmente: vá em **Actions → Backup → Run workflow**.

## Restore do banco

```bash
# Restaurar a partir de um dump
pg_restore --no-owner --no-acl --clean --if-exists \
  -d "$DATABASE_URL" backup_YYYYMMDD_HHMMSS.dump
```

> **Atenção**: o restore sobrescreve dados existentes. Faça backup do estado atual antes de restaurar.

## Export de mídias do Supabase Storage

As mídias ficam no bucket `media` do Supabase Storage. Para exportar:

1. Acesse o painel do Supabase → **Storage** → bucket `media`.
2. Faça download manual dos arquivos necessários.
3. Ou use a CLI do Supabase:

```bash
npx supabase storage ls media --project-ref <project-ref>
npx supabase storage cp -r supabase://media ./media-backup --project-ref <project-ref>
```

## Rollback de deploy no Render

### Opção 1 — Re-deploy de commit anterior

1. No painel do Render → **Events** → clique no deploy anterior que estava funcional.
2. Clique em **Rollback to this deploy**.

### Opção 2 — Re-deploy via GitHub

1. Identifique o commit/tag estável (ex.: `milestone-4`, `v0.4.0-m4`).
2. Faça revert ou force-push na branch `main` para o commit desejado.
3. O CI executará automaticamente e disparará o deploy hook.

### Opção 3 — Deploy manual via hook

```bash
curl -fsSL "$RENDER_DEPLOY_HOOK_URL"
```

## Migrações

As migrações rodam automaticamente no `CMD` do Dockerfile (`python manage.py migrate --noinput`) a cada deploy. Para executar manualmente no Render:

```bash
# Via Render Shell (painel do Render → Shell)
python manage.py migrate
python manage.py showmigrations
```
