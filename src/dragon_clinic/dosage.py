"""Розрахунок разової дози ліків для драконів і журнал призначень."""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

DOSE_PER_KG = {"fire": 2.0, "ice": 1.5}  # доза, мг на кг ваги
MIN_WEIGHT_KG = 10                       # допустима вага, включно
MAX_WEIGHT_KG = 5000                     # допустима вага, включно
HATCHLING_BELOW_MONTHS = 36              # дитинча: молодше 3 років (< 36 міс.)
HATCHLING_FACTOR = 0.5                   # дитинчатам — половина дози
MAX_SINGLE_DOSE_MG = 4000                # максимальна разова доза, мг
DECIMALS = 2                             # точність дози: 0,01 мг


def calculate_dose_mg(species: str, weight_kg: float, age_months: int) -> float:
    """Разова доза в міліграмах для дракона заданого виду, ваги і віку.

    Максимум застосовують до остаточної дози, тобто після зменшення вдвічі
    для дитинчат: жоден дракон не отримує понад MAX_SINGLE_DOSE_MG.
    """
    if species not in DOSE_PER_KG:
        raise ValueError(f"Невідомий вид дракона: {species!r}")
    if not MIN_WEIGHT_KG <= weight_kg <= MAX_WEIGHT_KG:
        raise ValueError(
            f"Вага {weight_kg} кг поза допустимим діапазоном "
            f"{MIN_WEIGHT_KG}–{MAX_WEIGHT_KG} кг"
        )
    if age_months < 0:
        raise ValueError(f"Вік не може бути від'ємним: {age_months} міс.")

    dose = weight_kg * DOSE_PER_KG[species]
    if age_months < HATCHLING_BELOW_MONTHS:
        dose *= HATCHLING_FACTOR
    dose = min(dose, MAX_SINGLE_DOSE_MG)
    return round(dose, DECIMALS)


@dataclass(frozen=True)
class Patient:
    name: str
    species: str        # "fire" або "ice"
    weight_kg: float
    age_months: int


@dataclass(frozen=True)
class Prescription:
    patient: str
    drug: str
    dose_mg: float
    prescribed_at: datetime


class Clock(Protocol):
    def now(self) -> datetime: ...


class PrescriptionJournal(Protocol):
    def record(self, entry: Prescription) -> None: ...


class PrescriptionService:
    """Призначає ліки: рахує дозу і записує призначення в журнал."""

    def __init__(self, clock: Clock, journal: PrescriptionJournal):
        self.clock = clock
        self.journal = journal

    def prescribe(self, patient: Patient, drug: str) -> Prescription:
        # спочатку розрахунок: для некоректного пацієнта запису в журналі не буде
        dose = calculate_dose_mg(patient.species, patient.weight_kg, patient.age_months)
        entry = Prescription(patient.name, drug, dose, self.clock.now())
        self.journal.record(entry)
        return entry
