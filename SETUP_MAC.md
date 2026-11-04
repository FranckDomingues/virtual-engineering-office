# macOS setup

From the project root, create and activate a virtual environment, install the
development dependencies, and run the local checks:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
ruff check src tests
pytest -q
python scripts/check_office.py
veo status
```

The CLI stores its local queue under `.veo/`, which is ignored by Git. Do not put
credentials, personal data, or production information in local task records.
This project does not require GitHub credentials, external services, or an agent
runtime. Review the staged file list before committing or publishing changes.
