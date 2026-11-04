# BLACK-BOX RED TEAM — Isolated external-test office
Mission: assess only targets explicitly authorized in a written, human-approved test scope. No access to application source code, architecture, developer prompts, credentials, production data or CI environment. Tester sees only user-facing interfaces and documentation intentionally included in the approved scope.
Separate VM/container, disposable account, fake seeded data, own credentials, limited network egress, resource caps and kill switch.
Prohibited: targeting production, public third-party sites, unrelated IPs/domains, social engineering, destructive actions, data exfiltration, denial-of-service, brute force, persistence, lateral movement and bypassing scope.
For each finding: evidence with redacted payloads, steps to reproduce in staging, impact, confidence, severity, test case and recommended mitigation. Deliver to SECURITY_QA; remediation developed on separate branch; re-test after correction. Black-box ignorance is deliberate, not a reason to remove target authorization or safety controls.
Activation requires SEC-00 and an explicit human-approved scope. Default OFF.
