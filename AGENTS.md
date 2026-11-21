# AGENTS.md — Instruções de Governança para Agentes de IA

> [English Version](AGENTS.en.md) | **Português**

Este documento orienta agentes de IA e desenvolvedores que atuam no projeto **O Último Blog do Mundo**.

---

## 1. Ordem de Leitura Obrigatória

1. `SPEC.md` — Especificação de produto e arquitetura (fonte de verdade).
2. `AGENTS.md` — Regras operacionais e fluxo de trabalho (este arquivo).
3. `CONTRIBUTING.md` — Convenções de branch, commit e estilo.
4. `docs/` — Guias especializados de arquitetura, segurança e operações.

---

## 2. Status do Projeto & Conclusão do Marco Fundacional

O ciclo fundacional inicial do projeto (MVP / versão `v1.0.0`) foi **concluído com sucesso no Milestone 7**:
- **Milestones 1 a 7 concluídos e integrados**.
- Suíte com mais de 100 testes passando e cobertura acima de 90%.
- Infraestrutura completa em nuvem (Render, Supabase Postgres/S3, Upstash Redis) e pipelines CI/CD em produção.
- Identidade visual Cyberpunk Suave / Terminal Retrô-Futurista implementada.

---

## 3. Regras de Trabalho Pós-v1.0.0

A partir da versão `v1.0.0`, o fluxo de trabalho opera sob o modelo **Gitflow Simplificado**:

1. **Ramificação estrita a partir de `develop`**:
   - Todo novo trabalho deve ser desenvolvido em branches criadas a partir de `develop`: `fix/<slug>`, `perf/<slug>`, `feat/<slug>`, `docs/<slug>`.
   - **Proibido commitar diretamente na branch `main`**.
2. **Integração e Testes na `develop`**:
   - Merges do dia a dia entram na `develop` após passarem por lint e testes locais.
3. **Deploy em Produção**:
   - O deploy automático no Render ocorre **exclusivamente no merge para a branch `main`**.
   - A `main` só recebe merge da `develop` quando aprovado pelo usuário para gerar uma release (`v1.x.x`).
4. **Custo zero obrigatório**:
   - Nenhuma decisão pode introduzir custos recorrentes. Qualquer serviço pago deve ser prontamente recusado.
5. **Cobertura de testes**:
   - Manter cobertura mínima de 80% (o CI falha abaixo disso). Novas funcionalidades exigem testes associados.
6. **Segredos**:
   - Nunca commitar segredos. Utilizar variáveis de ambiente no `.env` local e GitHub Secrets no CI.
7. **Sem Django admin**:
   - Manter `admin.site.urls` desativado. Toda funcionalidade de gestão reside no painel customizado sob `ADMIN_PATH`.

---

## 4. Commits e Convenções

- Siga estritamente os Conventional Commits em inglês definidos em `CONTRIBUTING.md`.
- Formato: `<tipo>(<escopo>): <descrição no imperativo>`.
- Commits atômicos, testados e sem mensagens genéricas como `wip` ou `fix stuff`.

---

## 5. Quando Perguntar (e Quando Agir)

- **Pergunte**: Novas dependências externas, mudanças de escopo, decisões de infraestrutura, qualquer ambiguidade arquitetural.
- **Aja diretamente**: Formatação de código conforme convenções do Ruff, correções triviais de digitação, adições de testes complementares.
