# Engineering Constitution v0.1

1. Architecture: hexagonal boundaries. Domain must not import UI, persistence, LLM, network or payments SDKs.
2. All integrations connect through versioned ports and adapters; replacement by test doubles must be supported.
3. No direct write access to production data from agents or LLMs.
4. Issues and PRs explicitly state milestone, checklist item, objective, acceptance PASS, and out-of-scope.
5. Every code change requires tests, documentation changes where relevant, security review and human approval.
6. Protected `main`: no direct pushes, self-approvals, auto-merge, or bypass by automation identities.
7. Access is least-privilege, temporary where practical, with protected credentials and audit logs.
8. Prefer practical MVPs and verifiable delivery; don't optimize or refactor beyond task scope.
9. No external marketing, demo, press, brand claims or public release before signed Release-to-Public gate.
10. Documentation and tests describe actual implementation; never claim success on unchecked work.
