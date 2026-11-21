# 🔒 Políticas & Hardening de Segurança — O Último Blog do Mundo

> [English Version](en/security.md) | **Português**

Este documento detalha o modelo de segurança, os controles defensivos e as auditorias automatizadas implementadas no **O Último Blog do Mundo**.

---

## 1. Controles Defensivos em Produção

### 1.1 Autenticação & Gestão de Acessos
- **Hasher de Senhas Primário**: **Argon2** (`argon2-cffi`), vencedor da Password Hashing Competition, resistente a ataques acelerados por hardware dedicado (ASICs/GPUs).
  ```python
  PASSWORD_HASHERS = [
      "django.contrib.auth.hashers.Argon2PasswordHasher",
      "django.contrib.auth.hashers.PBKDF2PasswordHasher",
      "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
      "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
  ]
  ```
- **Autenticação em Duas Etapas Obrigatória (2FA TOTP)**:
  - Todo acesso administrativo exige validação de código de 6 dígitos baseado em tempo (RFC 6238), compatível com Google Authenticator, Bitwarden, Authy e 1Password.
  - Configuração via QR Code criptografado na primeira ativação do operador.
- **Rota Secreta de Gestão**:
  - O Django admin convencional (`/admin/`) foi desativado e removido do roteador de URLs.
  - O painel customizado atende exclusivamente no caminho definido pela variável de ambiente `ADMIN_PATH` (em produção com valor aleatorizado).
  - Bloqueio explícito em `robots.txt` para impedir indexação por mecanismos de busca.
- **Defesa Contra Ataques de Força Bruta**:
  - Integração com **`django-axes`**: monitora tentativas falhas de login e bloqueia automaticamente o endereço IP do atacante após exceder o limite de tentativas.

### 1.2 Isolamento de Sessões & Proteção de Cookies
- **Armazenamento de Sessões**: As sessões administrativas são desacopladas do banco de dados e armazenadas no Redis, com expiração estrita de 8 horas.
- **Flags de Cookies de Produção**:
  - `SESSION_COOKIE_SECURE = True` (trafegado exclusivamente via HTTPS)
  - `SESSION_COOKIE_HTTPONLY = True` (inacessível para scripts JavaScript no navegador)
  - `SESSION_COOKIE_SAMESITE = "Lax"` (proteção contra vazamentos Cross-Site)
  - `CSRF_COOKIE_SECURE = True`
  - `CSRF_COOKIE_HTTPONLY = True`

### 1.3 Cabeçalhos de Proteção HTTP (Headers)
- **HTTPS Obrigatório**: `SECURE_SSL_REDIRECT = True` redireciona todo tráfego HTTP inseguro para HTTPS.
- **HSTS (HTTP Strict Transport Security)**:
  ```python
  SECURE_HSTS_SECONDS = 31536000  # 1 ano
  SECURE_HSTS_INCLUDE_SUBDOMAINS = True
  SECURE_HSTS_PRELOAD = True
  ```
- **Anti-Clickjacking**: `X_FRAME_OPTIONS = "DENY"`, impedindo que a aplicação seja renderizada dentro de `<iframe>` de domínios maliciosos.
- **Referrer Policy**: `SECURE_REFERRER_POLICY = "same-origin"`.
- **Content Security Policy (CSP)**: Políticas restritivas permitindo carregamento de recursos estáticos apenas da mesma origem (WhiteNoise) e das fontes WOFF2 servidas localmente.

### 1.4 Sanitização Estrita de Markdown (Proteção XSS)
Todo o conteúdo escrito em Markdown é convertido para HTML e imediatamente submetido à biblioteca **`nh3`** (baseada na engine de sanitização segura em Rust `ammonia`):
- Tags permitidas estritamente limitadas a elementos semânticos de formatação (`p`, `h1`-`h6`, `code`, `pre`, `blockquote`, `ul`, `ol`, `li`, `table`, etc.).
- Tags `<script>`, `<iframe>`, `<object>`, `<embed>` e atributos de manipulação DOM (`onclick`, `onload`, `onerror`) são sumariamente eliminados.

---

## 2. Auditoria e Varreduras Automatizadas no Pipeline CI/CD

O pipeline no GitHub Actions (`.github/workflows/ci.yml`) inclui etapas de verificação estática de segurança:

1. **`pip-audit`**:
   - Escaneia toda a árvore de dependências do Python contra a base de dados oficial de CVEs (PyPA Advisory Database).
   - O pipeline falha imediatamente caso qualquer vulnerabilidade conhecida seja identificada.
2. **Trivy (Security Scanner)**:
   - **Filesystem Scan**: Analisa o código-fonte e arquivos de configuração em busca de más práticas e segredos versionados.
   - **Container Image Scan**: Analisa a imagem Docker multi-stage construída antes de permitir o push para o GitHub Container Registry (`ghcr.io`).
3. **Dependabot**:
   - Monitoramento semanal automatizado para dependências Python (`pip`), GitHub Actions e imagens base Docker.

---

## 3. O que Ficou Justificadamente Fora de Escopo

Para manter a conformidade com a premissa de custo zero e a natureza de um blog pessoal de autor único:
- **WAF de Borda Corporativo Pago**: Dispensa-se soluções empresariais caras; as proteções nativas no nível de aplicação (CSRF, axes, nh3, headers) são suficientes.
- **SIEM / SOC Integrado**: O monitoramento é realizado via logs estruturados do Gunicorn/Render e endpoint de healthcheck `/healthz`.
- **SSO Corporativo (OAuth2 / SAML)**: Incompatível com o modelo de operador único com 2FA TOTP.
