# Virtual Engineering Office (VEO)

Public, portfolio-safe starter for an **offline-first, hexagonal engineering office**.

## Working now
- Python `veo` CLI for recording well-scoped tasks locally.
- Local human-supervised task lifecycle with Markdown handoff for manual VS Code use.
- Domain/Application/Adapters separated by ports.
- Local JSON storage; no GitHub or LLM credentials required.
- CI, unit tests, architecture and security policy documentation.
- Generic agent role descriptions are **specifications**, not running agents.

## Architecture
The project follows a hexagonal dependency direction: the domain defines the
work-item model, the application layer contains use cases and repository ports,
and adapters provide local JSON persistence and the CLI. The domain does not
depend on storage, GitHub, or model SDKs. The current adapter stores a local task
queue atomically under `.veo/`; supervised task state is stored in
`.veo/agent-tasks.json`, with generated handoffs under `handoffs/`. Neither is a
financial ledger or a remote service.

## Human-supervised agent task workflow

The local runtime records task intent and execution/review status. It does not
run an agent, make an LLM request, or control Copilot/4Geeks. A person must
manually inspect and use the Markdown handoff in VS Code, then report what
happened and perform the final review. Task output references must remain inside
the workspace and under the task's declared allowed paths.

```bash
# Create a draft task with explicit scope, paths, pass criteria, and restrictions.
veo task create --task-id OFFICE-02.1 --title 'Bounded implementation' \
	--milestone OFFICE-02.1 --objective 'Implement the approved change' \
	--scope 'Only the listed source and test paths' \
	--allowed-path src/veo --allowed-path tests \
	--pass-criteria 'Ruff and deterministic tests pass' \
	--restrictions 'No shell commands, network, credentials, approval, or merge' \
	--role developer

# Prepare a Markdown prompt; this does not start a model or execute anything.
veo task prepare OFFICE-02.1

# In VS Code, a human opens handoffs/OFFICE-02.1.md, reviews the restrictions,
# and manually copies the prompt into the approved 4Geeks/Copilot agent. The
# human checks proposed edits and any tool requests before acting on them.
# No direct 4Geeks API integration is provided or assumed.

# After the manual work, record a summary and workspace-relative output paths.
veo task report OFFICE-02.1 --summary 'Implemented and checked locally' \
	--output-reference src/veo/application/agent_use_cases.py

# A named human must explicitly approve or reject the reported work.
veo task review OFFICE-02.1 --decision approve --reviewer 'Human reviewer' \
	--notes 'Diff and test evidence reviewed'
veo tasks
```

Lifecycle is `DRAFT -> READY -> IN_PROGRESS -> REVIEW -> APPROVED` or
`REJECTED`. Approval/rejection is only available after a reported execution;
the reviewer name is mandatory. Review state is a local record, not a GitHub
approval, merge, deployment, or permission grant. Use `veo --help` and
`veo task --help` for CLI options. `--state PATH` can select a local state file;
the default `.veo/agent-tasks.json` and default `handoffs/` directory are ignored
by Git. The legacy `veo status` and `veo add-task` commands remain available.

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
The initial local runtime is not a hardened multi-user or sandboxed agent
execution environment. Keep all agent-executed writes, command execution,
network access, external integrations, approval automation, and merge/deploy
actions disabled unless a separately reviewed milestone explicitly introduces
and tests them.

## Branch and PR flow
Use a feature branch and submit changes through a pull request to the project's
default branch. Remote publication and merges require explicit human approval.
Only reusable office code, generic technical/agent documentation, security
standards, tests, and CI belong in this public repository; project-specific
product plans and marketing materials are maintained separately.
