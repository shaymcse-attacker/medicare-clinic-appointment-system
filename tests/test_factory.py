import pytest

from app.factory import AppointmentFactory


@pytest.mark.parametrize("type_name,duration,fee", [
    ("regular", 30, 500.0),
    ("follow-up", 15, 300.0),
    ("emergency", 45, 1000.0),
])
def test_factory_creates_correct_spec(type_name, duration, fee):
    spec = AppointmentFactory.create(type_name)
    assert spec.duration_min == duration
    assert spec.fee == fee


def test_factory_rejects_unknown_type():
    with pytest.raises(ValueError):
        AppointmentFactory.create("yearly-checkup")


def test_factory_lists_all_types():
    assert set(AppointmentFactory.available_types()) == {
        "regular", "follow-up", "emergency"}
