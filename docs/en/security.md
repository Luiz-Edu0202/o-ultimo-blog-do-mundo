# 🔒 Security Policies & Hardening — The Last Blog in the World

> **English** | [Versão em Português](../security.md)

This document details the threat model, defensive controls, and automated auditing implemented in **The Last Blog in the World**.

---

## 1. Production Defensive Controls

### 1.1 Authentication & Access Control
- **Primary Password Hasher**: **Argon2** (`argon2-cffi`), winner of the Password Hashing Competition, resilient against dedicated ASIC and GPU hardware-cracking attacks.
  ```python
  PASSWORD_HASHERS = [
      "django.contrib.auth.hashers.Argon2PasswordHasher",
      "django.contrib.auth.hashers.PBKDF2PasswordHasher",
      "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
      "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
  ]
  ```
- **Mandatory Two-Factor Authentication (2FA TOTP)**:
  - All administrative access requires a time-based 6-digit one-time passcode (RFC 6238), compatible with Google Authenticator, Bitwarden, Authy, and 1Password.
  - Setup via encrypted QR code upon initial operator onboarding.
- **Secret Administrative Path**:
  - Standard Django admin (`/admin/`) is disabled and removed from the URL configuration.
  - The custom dashboard operates exclusively under the path defined by the `ADMIN_PATH` environment variable (randomized in production).
  - Explicitly disallowed in `robots.txt` to prevent indexing by crawlers.
- **Brute-Force Attack Defense**:
  - Integration with **`django-axes`**: monitors failed login attempts and automatically blocks attacker IP addresses upon reaching threshold limits.

### 1.2 Session Isolation & Cookie Security
- **Session Storage**: Admin sessions are decoupled from the database and stored in Redis with an 8-hour lifetime.
- **Production Cookie Flags**:
  - `SESSION_COOKIE_SECURE = True` (HTTPS only)
  - `SESSION_COOKIE_HTTPONLY = True` (inaccessible to JavaScript document.cookie)
  - `SESSION_COOKIE_SAMESITE = "Lax"` (Cross-Site Request Forgery mitigation)
  - `CSRF_COOKIE_SECURE = True`
  - `CSRF_COOKIE_HTTPONLY = True`

### 1.3 HTTP Security Headers
- **Mandatory HTTPS**: `SECURE_SSL_REDIRECT = True` redirects all insecure HTTP traffic to HTTPS.
- **HSTS (HTTP Strict Transport Security)**:
  ```python
  SECURE_HSTS_SECONDS = 31536000  # 1 year
  SECURE_HSTS_INCLUDE_SUBDOMAINS = True
  SECURE_HSTS_PRELOAD = True
  ```
- **Anti-Clickjacking**: `X_FRAME_OPTIONS = "DENY"`, preventing embedding inside malicious iframes.
- **Referrer Policy**: `SECURE_REFERRER_POLICY = "same-origin"`.
- **Content Security Policy (CSP)**: Restrictive policy permitting assets exclusively from same-origin (WhiteNoise) and local WOFF2 fonts.

### 1.4 Strict Markdown Sanitization (XSS Defense)
All Markdown content rendered to HTML is sanitized using **`nh3`** (backed by the Rust `ammonia` engine):
- Allowed tags strictly limited to standard formatting elements (`p`, `h1`-`h6`, `code`, `pre`, `blockquote`, `ul`, `ol`, `li`, `table`, etc.).
- Tags such as `<script>`, `<iframe>`, `<object>`, `<embed>`, and DOM event handlers (`onclick`, `onload`, `onerror`) are stripped out.

---

## 2. Automated CI/CD Auditing

The GitHub Actions pipeline (`.github/workflows/ci.yml`) runs static security analysis on every push:

1. **`pip-audit`**:
   - Audits all Python dependencies against the PyPA advisory database.
   - The build fails if any known CVE is discovered.
2. **Trivy (Security Scanner)**:
   - **Filesystem Scan**: Detects leaked secrets and misconfigurations.
   - **Container Image Scan**: Scans the multi-stage Docker image before pushing to GHCR (`ghcr.io`).
3. **Dependabot**:
   - Automated weekly vulnerability updates for Python (`pip`), GitHub Actions, and Docker base images.

---

## 3. Justifiably Out-of-Scope Items

To remain compliant with zero operating cost for a single-author personal blog:
- **Paid Enterprise WAF**: Expensive enterprise edge firewalls are unnecessary given robust application-layer controls (CSRF, axes, nh3, headers).
- **Integrated SIEM**: Monitoring relies on structured Gunicorn/Render logs and the `/healthz` healthcheck endpoint.
- **Enterprise SSO (OAuth2 / SAML)**: Incompatible with the single-operator 2FA TOTP model.
