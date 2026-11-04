# Security Baseline v0.1

Threat model each user role, book, device, peer-sync channel, assistant prompt and adapter. Preserve confidentiality, integrity and availability.

Controls:
- Encrypt locally stored financial information; hold keys in platform keystore/secure enclave-backed APIs where available. Threat model device compromise and backups.
- Per-book membership authorization in application layer and at sync boundaries. Private books are never exposed to household admins.
- Authenticated, end-to-end encrypted sync with device revocation, key rotation and replay/duplicate protection.
- Untrusted chat/model output is parsed to typed command proposals; explicit confirmation for materially sensitive writes; never direct SQL or privileged code execution.
- Validation, double-entry invariant, idempotent ledger event IDs, append-only audit history and reversal entries.
- Minimize telemetry; no personal financial samples in builds, screenshots, logs, CI artifacts or marketing.
- Dependency scanning, secret scanning, code scanning, signed artifacts, restricted CI permissions, review of third-party changes.
- Recovery and encrypted backup tests are part of release criteria.

Standards to map controls against: OWASP MASVS, OWASP ASVS/API Security Top 10 as relevant, NIST SSDF. Claim no certification without independent assessment.
