"""System clock adapter for locally timestamped records."""
from datetime import UTC, datetime


class SystemClock:
    def now(self) -> str:
        return datetime.now(UTC).isoformat(timespec="seconds")
