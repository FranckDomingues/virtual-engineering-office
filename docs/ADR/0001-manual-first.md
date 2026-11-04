# ADR-0001: Manual-first, minimal hexagonal bootstrap
Status: Accepted as initial implementation proposal; repository review pending.
Decision: Python stdlib + pytest + ruff, CLI with local storage. No LLM automation.
Rationale: verify modularity, security boundaries and CI before unattended execution.
Consequences: no overnight PR generation yet; later GitHub and LLM adapters must respect ports and governance.
