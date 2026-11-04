#!/usr/bin/env bash
# Read-only, manual, bounded review. No automatic PR/merge or scheduling.
set -euo pipefail
cd "$(dirname "$0")/.."
if ! command -v claude >/dev/null; then echo 'Claude Code CLI not installed. Run static checks instead.' >&2; exit 2; fi
python3 scripts/check_office.py
mkdir -p .local/reports
stamp="$(date +%Y%m%d-%H%M%S)"
# Print mode; tools restricted to read-only utilities. Do not grant unrestricted Bash.
claude -p --max-turns 3 --max-budget-usd 0.50 --tools 'Read,Glob,Grep' --permission-mode dontAsk   --output-format text "Act as the independent Advocatus Diaboli. Review only docs in this working directory. Do not execute code, use network, edit files or propose changes outside OFFICE-00. Provide top 2 risks with evidence, impact and smallest test. Do not include secrets."   > ".local/reports/advocatus-${stamp}.md"
echo "Saved .local/reports/advocatus-${stamp}.md"
