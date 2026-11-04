# Token and operational budgets
Initial conservative operating policy (editable after measurement):
- Orchestrator: 1 focused planning run/task, max 3 turns, max $0.50 API-equivalent ceiling.
- Developer: 1 narrow task/feature, max 8 turns, max $3.00 API-equivalent ceiling.
- Security reviewer: max 4 turns, max $1.00 API-equivalent ceiling.
- MIRROR and Advocatus: demand-driven or scheduled once/day, max $0.50 each.
- Red Team: OFF until human authorization, separate limits.
- Daily budget guard: $5 total across invoked agents; weekly operating target: $20 until results justify more.
API billing and subscription usage may differ. CLI cost limits are *not* bank-enforced spending caps. Track actual usage using provider billing telemetry; hard-stop the launcher once logged daily budget is consumed. No model invocation by default; only explicit operator command.
Principles: smallest context, scoped file lists, diff instead of full repo, cache static prompts where available, stop on failed gates, one retry maximum, prefer local/static linters before tokens. Never send secrets or real financial data to cloud models.
