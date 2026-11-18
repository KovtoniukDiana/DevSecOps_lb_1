from datetime import datetime

import pytest

from dragon_clinic.dosage import Prescription, PrescriptionService
from fakes import NOW, FakeClock


def test_prescribe_records_entry_with_correct_data(
    make_patient, fake_clock, journal_mock
):
    service = PrescriptionService(fake_clock, journal_mock)

    service.prescribe(make_patient(), "Протизапальне")

    journal_mock.record.assert_called_once_with(
        Prescription("Вогнекрил", "Протизапальне", 200.0, NOW)
    )


def test_prescribe_returns_the_recorded_entry(make_patient, fake_clock, journal_mock):
    service = PrescriptionService(fake_clock, journal_mock)

    entry = service.prescribe(make_patient(), "Протизапальне")

    assert entry is journal_mock.record.call_args.args[0]


def test_prescribe_records_capped_dose(make_patient, fake_clock, journal_mock):
    service = PrescriptionService(fake_clock, journal_mock)

    entry = service.prescribe(make_patient(weight_kg=5000), "Знеболювальне")

    assert entry.dose_mg == 4000.0   # у журнал іде обмежена доза


def test_prescribe_records_half_dose_for_hatchling(
    make_patient, fake_clock, journal_mock
):
    service = PrescriptionService(fake_clock, journal_mock)

    entry = service.prescribe(make_patient(species="ice", age_months=12), "Вітаміни")

    assert entry.dose_mg == 75.0     # 100 кг * 1,5 мг/кг / 2


@pytest.mark.parametrize(
    "bad_patient",
    [
        pytest.param(dict(weight_kg=9), id="weight-too-small"),
        pytest.param(dict(species="earth"), id="unknown-species"),
        pytest.param(dict(age_months=-1), id="negative-age"),
    ],
)
def test_invalid_patient_is_not_written_to_journal(
    make_patient, fake_clock, journal_mock, bad_patient
):
    service = PrescriptionService(fake_clock, journal_mock)

    with pytest.raises(ValueError):
        service.prescribe(make_patient(**bad_patient), "Протизапальне")

    journal_mock.record.assert_not_called()


@pytest.mark.parametrize(
    "moment",
    [datetime(2026, 1, 1, 0, 0), datetime(2026, 12, 31, 23, 59)],
    ids=["new-year", "year-end"],
)
def test_entry_time_comes_from_clock(make_patient, journal_mock, moment):
    service = PrescriptionService(FakeClock(moment), journal_mock)

    entry = service.prescribe(make_patient(), "Протизапальне")

    assert entry.prescribed_at == moment


def test_fake_journal_keeps_prescriptions_in_order(
    make_patient, fake_clock, fake_journal
):
    service = PrescriptionService(fake_clock, fake_journal)

    service.prescribe(make_patient(name="Вогнекрил"), "Протизапальне")
    service.prescribe(make_patient(name="Льодовик", species="ice"), "Вітаміни")
    service.prescribe(make_patient(name="Вогнекрил"), "Знеболювальне")

    assert [e.drug for e in fake_journal.entries] == [
        "Протизапальне", "Вітаміни", "Знеболювальне"]
    assert [e.drug for e in fake_journal.for_patient("Вогнекрил")] == [
        "Протизапальне", "Знеболювальне"]


def test_failed_prescription_leaves_fake_journal_unchanged(
    make_patient, fake_clock, fake_journal
):
    service = PrescriptionService(fake_clock, fake_journal)
    service.prescribe(make_patient(), "Протизапальне")

    with pytest.raises(ValueError):
        service.prescribe(make_patient(weight_kg=5001), "Знеболювальне")

    assert len(fake_journal.entries) == 1
