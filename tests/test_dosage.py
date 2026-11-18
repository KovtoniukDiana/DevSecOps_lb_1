import pytest

from dragon_clinic.dosage import MAX_SINGLE_DOSE_MG, calculate_dose_mg

ADULT = 120      # місяців, доросла особина
HATCHLING = 12   # місяців, дитинча


@pytest.mark.parametrize(
    "weight_kg, expected",
    [
        pytest.param(10, 20.0, id="min-weight-10"),          # межа: мінімальна вага
        pytest.param(11, 22.0, id="above-min-11"),           # межа: поруч із мінімумом
        pytest.param(100, 200.0, id="typical-100"),          # типове значення
        pytest.param(1999, 3998.0, id="below-cap-1999"),     # межа: ще під максимумом
        pytest.param(2000, 4000.0, id="exactly-cap-2000"),   # межа: рівно максимум
        pytest.param(2001, 4000.0, id="capped-2001"),        # межа: 4002 -> 4000
        pytest.param(5000, 4000.0, id="max-weight-5000"),    # межа: максимальна вага
    ],
)
def test_fire_adult_dose_by_weight(weight_kg, expected):
    assert calculate_dose_mg("fire", weight_kg, ADULT) == expected


@pytest.mark.parametrize(
    "weight_kg, expected",
    [
        pytest.param(10, 15.0, id="min-weight-10"),          # межа: мінімальна вага
        pytest.param(100, 150.0, id="typical-100"),          # типове значення
        pytest.param(2666, 3999.0, id="below-cap-2666"),  # межа: 3999, ще під максимумом
        pytest.param(2667, 4000.0, id="capped-2667"),        # межа: 4000,5 -> 4000
        pytest.param(5000, 4000.0, id="max-weight-5000"),    # межа: максимальна вага
    ],
)
def test_ice_adult_dose_by_weight(weight_kg, expected):
    assert calculate_dose_mg("ice", weight_kg, ADULT) == expected


@pytest.mark.parametrize(
    "age_months, expected",
    [
        pytest.param(0, 100.0, id="newborn-0"),  # межа: найменший допустимий вік
        pytest.param(35, 100.0, id="last-hatchling-35"),     # межа: ще немає 3 років
        pytest.param(36, 200.0, id="exactly-3-years-36"),  # межа: рівно 3 роки, повна доза
        pytest.param(37, 200.0, id="above-3-years-37"),      # межа: поруч зверху
    ],
)
def test_hatchling_gets_half_dose_until_three_years(age_months, expected):
    assert calculate_dose_mg("fire", 100, age_months) == expected


@pytest.mark.parametrize(
    "weight_kg, expected",
    [
        pytest.param(3999, 3999.0, id="below-cap-3999"),  # половина дози під максимумом
        pytest.param(4000, 4000.0, id="exactly-cap-4000"),   # половина дози = максимум
        pytest.param(4001, 4000.0, id="capped-4001"),        # 4001 -> 4000
        # 5000 -> 4000, а не 2000, як було б при обмеженні ДО зменшення вдвічі
        pytest.param(5000, 4000.0, id="max-weight-5000"),
    ],
)
def test_hatchling_cap_applies_after_halving(weight_kg, expected):
    assert calculate_dose_mg("fire", weight_kg, HATCHLING) == expected


@pytest.mark.parametrize(
    "weight_kg, expected",
    [pytest.param(10, 7.5, id="min-weight-10"),
     pytest.param(5000, 3750.0, id="max-weight-5000")],      # максимум недосяжний
)
def test_ice_hatchling_never_reaches_cap(weight_kg, expected):
    assert calculate_dose_mg("ice", weight_kg, HATCHLING) == expected


@pytest.mark.parametrize(
    "weight_kg",
    [
        pytest.param(9.99, id="just-below-min"),             # межа: трохи менше 10
        pytest.param(0, id="zero"),
        pytest.param(-1, id="negative"),
        pytest.param(5000.01, id="just-above-max"),          # межа: трохи більше 5000
        pytest.param(float("inf"), id="infinity"),
        pytest.param(float("nan"), id="nan"),  # NaN не порівнюється з числами
    ],
)
def test_weight_outside_range_raises(weight_kg):
    with pytest.raises(ValueError, match="поза допустимим діапазоном"):
        calculate_dose_mg("fire", weight_kg, ADULT)


@pytest.mark.parametrize(
    "species",
    [pytest.param("", id="empty"),
     pytest.param("Fire", id="wrong-case"),
     pytest.param("fire ", id="trailing-space"),
     pytest.param("earth", id="unknown-species")],
)
def test_unknown_species_raises(species):
    with pytest.raises(ValueError, match="Невідомий вид дракона"):
        calculate_dose_mg(species, 100, ADULT)


def test_negative_age_raises():
    with pytest.raises(ValueError, match="Вік не може бути від'ємним"):
        calculate_dose_mg("fire", 100, -1)


@pytest.mark.parametrize(
    "species, weight_kg, expected",
    [
        pytest.param("fire", 10.333, 20.67, id="fire-round-up"),    # 20,666 -> 20,67
        pytest.param("fire", 10.004, 20.01, id="fire-round-up-2"),  # 20,008 -> 20,01
        pytest.param("ice", 10.3, 15.45, id="ice-float-noise"),     # 15.450000000000001
    ],
)
def test_dose_is_rounded_to_hundredths(species, weight_kg, expected):
    # дробові числа порівнюємо через approx, а не ==
    assert calculate_dose_mg(species, weight_kg, ADULT) == pytest.approx(expected)


@pytest.mark.parametrize("weight_kg", [10, 5000])
@pytest.mark.parametrize("age_months", [0, 120])
@pytest.mark.parametrize("species", ["fire", "ice"])
def test_dose_is_positive_and_within_max(species, age_months, weight_kg):
    dose = calculate_dose_mg(species, weight_kg, age_months)
    assert 0 < dose <= MAX_SINGLE_DOSE_MG
