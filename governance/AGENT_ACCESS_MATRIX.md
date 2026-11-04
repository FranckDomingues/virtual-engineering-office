# Agent access matrix (default deny)
| Agent | Sources | Write permission | Secrets | Merge/Deploy |
| --- | --- | --- | --- | --- |
| Orchestrator | Issues, approved docs | Draft tasks and plans | None | Never |
| Developer | Assigned project, feature branch | Worktree/feature branch only | None | Never |
| Security/QA | PR diff, tests, sanitized logs | Review report only | None | Never |
| MIRROR | Docs, sanitized telemetry, public sources | Proposals only | None | Never |
| Advocatus Diaboli | Milestone plan, decisions | Critique only | None | Never |
| Red Team | Allowlisted staging URL only | Findings report | Disposable staging login only | Never |
Never use a personal PAT with broad scope as an agent credential. Separate repo rights from local filesystem and network controls. Human reviews all PRs and public releases.
