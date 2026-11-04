# Human Approval Policy

Only an authorized human Product Owner can approve a PR, merge to protected main, authorize a distribution release or authorize a public post. Agents may author and review but not approve their own work. Agents cannot expand permissions or disable release checks.

Review packet: milestone and checklist item, summary, files changed, demo evidence, tests + logs, security impact, data migrations, compatibility and rollback, unresolved risks, OUT OF SCOPE.

PR state: Draft -> CI -> Security/QA -> Ready for owner -> Approved or Changes requested. Release separately requires recorded approval.
