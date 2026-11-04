from pathlib import Path

root = Path(__file__).resolve().parents[1]
required = [
    "README.md", "pyproject.toml", "src/veo/domain/models.py",
    "src/veo/application/ports.py", "src/veo/application/use_cases.py",
    "src/veo/adapters/json_repository.py", "tests/test_domain.py",
    "docs/ARCHITECTURE.md", "governance/SECURITY_BASELINE.md",
    "agents/ADVOCATUS_DIABOLI.md", "agents/BLACKBOX_REDTEAM.md",
]
missing = [name for name in required if not (root / name).is_file()]
if missing:
    raise SystemExit(f"FAIL missing files: {missing}")
print("PASS: OFFICE-01.1 static structure")
