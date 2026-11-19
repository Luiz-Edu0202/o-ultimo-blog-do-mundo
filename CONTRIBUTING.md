# Contributing

## Conventional Commits

Formato: `<tipo>(<escopo>): <descrição>`

Tipos aceitos:

- `feat` — nova funcionalidade
- `fix` — correção de bug
- `docs` — documentação
- `style` — formatação (sem mudança de lógica)
- `refactor` — refatoração sem mudança de comportamento
- `test` — testes
- `chore` — tarefas de manutenção
- `ci` — mudanças no CI/CD
- `build` — Docker, dependências, build

Escopos:

- `m1`..`m6` — número do milestone
- `blog`, `dashboard`, `core`, `ci`, `docker`, `docs` — módulo

Exemplos válidos:

- `feat(m2): add slug generation for posts`
- `ci(m1): cache pip dependencies`
- `docs(m4): document docker-compose usage`

## Branches

- `main` — protegida, sempre deployável.
- `milestone/<n>-<slug>` — uma por milestone.
- `fix/<slug>` e `chore/<slug>` — correções pontuais fora de milestone.

## Estilo de código

- Python: Ruff (lint + format). Configuração em `pyproject.toml`.
- Markdown: linha em branco ao final, sem trailing whitespace.
- Commits: inglês. Código e comentários: inglês. Documentação para usuários: PT-BR (com tradução EN quando aplicável).

## Pull Requests

- Título segue Conventional Commits.
- Descrição inclui: o que mudou, como testar, checklist dos critérios de aceite do milestone.
- CI deve passar antes do merge.
- Merge com `--no-ff` para preservar histórico do milestone.

## Versionamento

- Tags por milestone: `milestone-<n>` e `v0.<n>.0-m<n>`.
- Versão final: `v1.0.0`.
