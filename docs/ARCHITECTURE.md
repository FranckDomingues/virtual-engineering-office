# Architecture — OFFICE-01.1

Dependency rule: `domain <- application <- adapters/cli`.
- **Domain** contains immutable WorkItem and TaskStatus; no third-party SDKs.
- **Application** holds WorkRepository protocol and OfficeService use cases.
- **Adapters** implement local storage; GitHub and LLM adapters are deferred.
- **Entry points** expose CLI interfaces and never bypass application services.

Security: work items remain in local `.veo/` (gitignored); no private data in version control. Future tools will use explicitly reviewed scopes and typed permission boundaries.

Decision ADR-0001: Begin with manual orchestration, not an autonomous daemon. All PRs require owner review. Do not activate untrusted skills or offensive testing before explicit scope authorization.
