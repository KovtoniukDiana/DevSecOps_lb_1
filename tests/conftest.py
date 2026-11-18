from unittest.mock import Mock

import pytest

from dragon_clinic.dosage import Patient
from fakes import NOW, FakeClock, InMemoryJournal


@pytest.fixture
def make_patient():
    """Фабрика пацієнтів: тест задає лише те, що для нього важливо."""

    def _make(species="fire", weight_kg=100, age_months=120, name="Вогнекрил"):
        return Patient(name=name, species=species,
                       weight_kg=weight_kg, age_months=age_months)

    return _make


@pytest.fixture
def fake_clock():
    return FakeClock(NOW)


@pytest.fixture
def journal_mock():
    """Mock журналу: записує виклики; spec не дає викликати зайві методи."""
    return Mock(spec=["record"])


@pytest.fixture
def fake_journal():
    return InMemoryJournal()
