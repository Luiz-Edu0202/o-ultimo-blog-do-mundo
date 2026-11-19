# AGENTS.md — Instruções para o agente

## Ordem de leitura

1. `SPEC.md` — o que construir (fonte de verdade de produto).
2. `AGENTS.md` — como trabalhar (este arquivo).
3. `CONTRIBUTING.md` — convenções de commit, branch e estilo.

## Regras gerais

- Não implemente nada fora do escopo do `SPEC.md` sem perguntar.
- Custo zero obrigatório. Se algo exigir serviço pago, pare e pergunte.
- Nunca commite segredos. Use `.env` local, GitHub Secrets e env do host.
- Escreva testes junto com cada funcionalidade. Cobertura mínima 80%.
- Se a spec for ambígua, pergunte antes de codar.
- Atualize o `README.md` ao final de cada milestone (não deixe para o final).

## Milestones

- Trabalhe um milestone por vez, na ordem definida na seção 15 do `SPEC.md`.
- Ao final de cada milestone, entregue ao usuário:
  1. Resumo do que foi feito.
  2. Como testar localmente.
  3. O que ficou pendente ou decisões em aberto.
  4. Link para o commit/tag do milestone.
- **Não avance para o próximo milestone sem aprovação explícita do usuário.**

## Commits e branches

Siga a especificação de Conventional Commits em `CONTRIBUTING.md`.

- **Branch de trabalho por milestone**: `milestone/<n>-<slug>`
  - Ex.: `milestone/1-fundacao`, `milestone/2-dominio-publico`
- **Commits pequenos e atômicos** dentro do milestone. Cada commit deve compilar e passar lint/testes localmente.
- **Formato**: `<tipo>(<escopo>): <descrição no imperativo>`
  - Escopo obrigatório e relacionado ao milestone ou módulo: `m1`, `m2`... ou `blog`, `dashboard`, `ci`, `docker`.
  - Exemplos:
    - `feat(m1): initialize django project structure`
    - `chore(m1): configure ruff and pre-commit`
    - `ci(m1): add lint and test workflows skeleton`
    - `feat(m2): add Post and Tag models with migrations`
    - `test(m2): cover post publication rules`
    - `fix(m3): enforce 2FA on dashboard login`
- **Idioma do commit**: inglês (padrão de mercado, facilita buscas e portfólio).
- **Proibido**: commits do tipo `wip`, `update`, `fix stuff`, ou commits gigantes sem escopo. Se precisar, use `--fixup`/rebase interativo antes de abrir o PR (não commite fixups no branch final).

### Fechamento de cada milestone

1. Garantir que lint, testes e build passam localmente.
2. Atualizar `README.md` com a seção correspondente ao milestone.
3. Adicionar entrada em `CHANGELOG.md` no formato Keep a Changelog.
4. Criar **tag anotada**: `milestone-<n>` e `v0.<n>.0-m<n>` (ex.: `milestone-1`, `v0.1.0-m1`).
5. Abrir Pull Request do branch `milestone/<n>-<slug>` para `main` **apenas se o usuário pedir revisão**. Caso contrário, mescle com `--no-ff` para preservar o histórico do milestone.
6. Aguardar aprovação do usuário antes do próximo milestone.

## Fechamento do projeto (após Milestone 6)

1. Garantir `README.md` completo conforme seção 13 do `SPEC.md`.
2. Finalizar `CHANGELOG.md` com entrada `v1.0.0`.
3. Criar tag anotada `v1.0.0` no commit final.
4. Se `gh` estiver autenticado, rodar:
   - `gh repo edit --description "<descrição>" --homepage "<url-da-demo>"`
   - `gh release create v1.0.0 --notes-file CHANGELOG.md`
5. Se `gh` não estiver disponível, **gerar um arquivo `REPO_DESCRIPTION.md`** com a descrição sugerida e o comando exato para o usuário executar.
6. Entregar ao usuário um resumo final: URL da demo, link da release, e checklist dos critérios de aceite.

## Quando perguntar (e quando não perguntar)

- **Pergunte**: dependência nova fora da stack, mudança de escopo, decisão de infraestrutura com custo, qualquer ambiguidade na spec.
- **Não pergunte**: escolhas triviais de implementação já cobertas por convenções (ex.: nome de variável, formatação de código).
- Sempre registre as decisões relevantes no `CHANGELOG.md` ou em uma seção “Decisões” do `README.md`.

## Anti-padrões proibidos

- Commitar direto na `main` sem passar pelo branch do milestone.
- Deixar `DEBUG=True` em arquivos versionados.
- Hardcodar `SECRET_KEY`, `ADMIN_PATH` ou credenciais.
- Expor o Django admin.
- Instalar dependências fora da seção 3 do `SPEC.md` sem perguntar.
- Pular testes “porque o milestone é pequeno”.
