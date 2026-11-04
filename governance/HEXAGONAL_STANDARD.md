# Hexagonal Architecture Standard

Dependencies point inward: adapters -> application -> domain. Domain defines business invariants and entities; application defines use cases and ports. Infrastructure implements outbound ports. Entrypoints (mobile UI, chat, CLI) call inbound use cases. Bindings are performed at composition root.

## Mandatory tests
- Unit tests for domain invariants without any plugin.
- Port contract tests reused by all adapter implementations.
- Adapter integration tests with fake and controlled network services.
- No UI, SQL library, LLM SDK or vendor import inside domain.

An adapter may be disabled only if use cases handle its absence safely. Data migrations and cryptographic key changes require separate reversible/forward-recovery plans.
