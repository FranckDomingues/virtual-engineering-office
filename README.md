# Virtual Engineering Office (VEO)

Public, portfolio-safe starter for an **offline-first, hexagonal engineering office**.

## Working now
- Python `veo` CLI for recording well-scoped tasks locally.
- Domain/Application/Adapters separated by ports.
- Local JSON storage; no GitHub or LLM credentials required.
- CI, unit tests, architecture and security policy documentation.
- Generic agent role descriptions are **specifications**, not running agents.

## Architecture
The project follows a hexagonal dependency direction: the domain defines the
work-item model, the application layer contains use cases and repository ports,
and adapters provide local JSON persistence and the CLI. The domain does not
depend on storage, GitHub, or model SDKs. The current adapter stores a local task
queue atomically under `.veo/`; it is not a financial ledger or a remote service.

## Security and limitations
The current CLI is offline-first: it has no GitHub writes, network integrations,
LLM calls, agent tool execution, merge/deploy actions, authentication, encryption,
or multi-user access control. Local task records are not intended for secrets or
personal/financial data. `.veo/`, virtual environments, environment files,
credentials, local databases, logs, reports, and machine-specific editor files
are ignored by Git, but ignore rules are not a substitute for reviewing the
actual staged files. Human review remains required for changes and publication.

This is an early engineering-office starter, not a production-ready task
management or accounting system. The agent documents describe proposed operating
roles; they do not implement or enable autonomous execution.

## Quickstart (macOS / VS Code)
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
ruff check src tests
pytest -q
veo status
veo add-task --task-id OFFICE-01.1 --title 'Bootstrap' --milestone OFFICE-01 --objective 'Validate starter' --pass-criteria 'CI green' --out-of-scope 'No autonomous access'
veo status
```

## Security gates
No automated GitHub writes, merges, deployments, red-team attacks, agent tool execution or outbound network calls in this starter.
Never commit secrets, private data, production URLs, tokens or personal identifiers. See the generic policies in `governance/`.

## Next milestone
`OFFICE-01.2`: prepare a public repository and its first CI workflow. A read-only
GitHub adapter, if later approved, is not implemented in this starter. Keep all
agent-executed writes disabled until a human approves policies and CI protections.

## Branch and PR flow
Use a feature branch and submit changes through a pull request to the project's
default branch. Remote publication and merges require explicit human approval.
Only reusable office code, generic technical/agent documentation, security
standards, tests, and CI belong in this public repository; project-specific
product plans and marketing materials are maintained separately.
