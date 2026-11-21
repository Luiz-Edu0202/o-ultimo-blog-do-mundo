# 🛠️ Operações, Resiliência & Recuperação de Desastres — O Último Blog do Mundo

> [English Version](en/operations.md) | **Português**

Este manual operacional reúne todos os procedimentos de backup, restauração de desastre, rollback de deploy e estratégias de mitigação das limitações dos provedores de nuvem gratuitos.

---

## 1. Limitações Conhecidas dos Free Tiers & Mitigações

Operar uma aplicação moderna com **custo zero absoluto** exige contornar as políticas de uso dos provedores gratuitos:

| Provedor | Limitação do Free Tier | Impacto no Projeto | Mitigação Implementada |
|---|---|---|---|
| **Render** | Spin-down após 15 min sem tráfego HTTP | Cold start de ~45s na primeira requisição após dormência | Workflow agendado `.github/workflows/keep_alive.yml` executa um ping a cada 3h |
| **Supabase** | Pausa do banco após 7 dias contínuos sem comandos | Banco entra em dormência e requer despausa manual | O ping do keep-alive consulta `/healthz` e a rotina `backup.yml` executa queries semanais |
| **Render** | Disco local do container é 100% efêmero | Arquivos gravados localmente são perdidos no reinício | Todo upload de mídia é gravado diretamente no Supabase Storage via S3 |

### Funcionamento do Keep-Alive (`.github/workflows/keep_alive.yml`)
- Executado automaticamente a cada 3 horas via cron do GitHub Actions (e disparável manualmente).
- Realiza uma requisição HTTP `GET` no endpoint `/healthz`.
- O endpoint valida ativamente a conectividade com o PostgreSQL (`SELECT 1`) e com o Redis (`SET/GET`), garantindo que ambos os provedores permaneçam ativos.

---

## 2. Rotinas de Backup

### 2.1 Backup Automatizado Semanal (`.github/workflows/backup.yml`)
O repositório possui uma rotina agendada aos domingos (03:00 UTC) no GitHub Actions que:
1. Conecta-se com segurança ao PostgreSQL do Supabase via secret `DATABASE_URL`.
2. Executa `pg_dump` em formato binário comprimido (`-Fc`).
3. Faz upload do artefato criptografado para o GitHub Actions com retenção configurada para **30 dias**.

### 2.2 Backup Manual do Banco de Dados
Para extrair um dump local instantâneo:

```bash
# Definir a URL do banco do Supabase (obtida no painel)
export DATABASE_URL="postgresql://postgres.<ref>:<password>@aws-0-us-east-1.pooler.supabase.com:5432/postgres"

# Criar pasta local de backups (ignorada pelo Git)
mkdir -p backups

# Gerar dump consistente com carimbo de data/hora
pg_dump "$DATABASE_URL" \
  --format=custom \
  --no-owner \
  --no-privileges \
  --file="backups/backup_$(date +%Y%m%d_%H%M%S).dump"
```

---

## 3. Restauração de Desastre (Disaster Recovery)

Para restaurar um backup existente em uma nova instância do PostgreSQL:

```bash
# 1. Obter a URL da instância de destino
export TARGET_DATABASE_URL="postgresql://postgres.<new-ref>:<password>@aws-0-us-east-1.pooler.supabase.com:5432/postgres"

# 2. Executar restauração via pg_restore
pg_restore \
  --clean \
  --if-exists \
  --no-owner \
  --no-privileges \
  --dbname="$TARGET_DATABASE_URL" \
  backups/backup_YYYYMMDD_HHMMSS.dump

# 3. Aplicar migrações do Django para validar schema
python manage.py migrate
```

---

## 4. Backup & Exportação de Mídia (Supabase Storage)

Como as capas de posts e mídias ficam armazenadas em bucket S3 no Supabase, a sincronização pode ser realizada com qualquer cliente S3 ou AWS CLI:

```bash
# Configurar credenciais do Supabase S3
export AWS_ACCESS_KEY_ID="<SUPABASE_S3_ACCESS_KEY>"
export AWS_SECRET_ACCESS_KEY="<SUPABASE_S3_SECRET_KEY>"
export AWS_ENDPOINT_URL="https://<project-ref>.supabase.co/storage/v1/s3"

# Sincronizar todos os arquivos de mídia para uma pasta local
aws s3 sync s3://media ./backups/media/
```

---

## 5. Procedimentos de Rollback de Deploy no Render

Caso uma nova versão introduza um comportamento inesperado em produção:

1. **Reverter via GitHub Container Registry (GHCR)**:
   - A cada commit na `main`, o CI publica uma imagem com tag imutável do SHA do commit (`ghcr.io/luiz-edu0202/o-ultimo-blog-do-mundo:sha-<commit>`).
   - No painel do Render, vá em **Settings** > **Image URL** e aponte para a tag SHA da versão anterior estável.
2. **Reverter via Git**:
   ```bash
   # Reverter o commit problemático na branch main
   git revert <commit-hash>
   git push origin main
   # O CI executará os testes e disparará o deploy hook da imagem corrigida
   ```
