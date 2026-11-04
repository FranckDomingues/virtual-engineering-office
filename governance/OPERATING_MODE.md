# MVP operating mode
Stage 0: documentation + static CI; no live agents or external financial data.
Stage 1: manual agent CLI runs with narrow workspace and sanitized test data.
Stage 2: developer generates proposed PR; human checks branch protections.
Stage 3: schedule limited jobs only after three successful supervised trials.
No autonomous branch merge, release, publication, real payments, or credential changes.
If there is any uncertainty about account privileges, execution environment, billing, or outbound traffic, fail closed.
