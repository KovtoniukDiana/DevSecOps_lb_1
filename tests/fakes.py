from datetime import datetime

NOW = datetime(2026, 11, 17, 10, 0)   # «зараз» для тестів


class FakeClock:
    """Заглушка (stub) годинника: «зараз» задає тест."""

    def __init__(self, now: datetime):
        self._now = now

    def now(self) -> datetime:
        return self._now


class InMemoryJournal:
    """Фейк (fake) журналу призначень: проста робоча реалізація в пам'яті."""

    def __init__(self):
        self.entries = []

    def record(self, entry) -> None:
        self.entries.append(entry)

    def for_patient(self, name: str) -> list:
        return [e for e in self.entries if e.patient == name]
