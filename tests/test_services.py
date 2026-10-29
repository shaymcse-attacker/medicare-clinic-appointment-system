import pytest

from app.services import register_user, authenticate, add_schedule, search_doctors


def test_register_and_authenticate(conn, patient):
    user = authenticate(conn, "karim@mail.com", "secret1")
    assert user is not None and user["id"] == patient


def test_authenticate_wrong_password(conn, patient):
    assert authenticate(conn, "karim@mail.com", "wrong") is None


def test_authenticate_unknown_email(conn):
    assert authenticate(conn, "nobody@mail.com", "x") is None


def test_password_is_stored_hashed(conn, patient):
    row = conn.execute("SELECT password_hash FROM users WHERE id = ?",
                       (patient,)).fetchone()
    assert row["password_hash"] != "secret1"


def test_register_duplicate_email_rejected(conn, patient):
    with pytest.raises(ValueError):
        register_user(conn, "Other", "karim@mail.com", "secret1")


def test_register_invalid_role_rejected(conn):
    with pytest.raises(ValueError):
        register_user(conn, "X", "x@mail.com", "secret1", role="superuser")


def test_search_doctors_by_specialization(conn, doctor):
    assert len(search_doctors(conn, "Cardiology")) == 1
    assert len(search_doctors(conn, "Dermatology")) == 0


def test_search_doctors_returns_all(conn, doctor):
    register_user(conn, "Dr. Ayesha", "ayesha@clinic.com", "secret1",
                  role="doctor", specialization="Medicine")
    assert len(search_doctors(conn)) == 2


def test_add_schedule_stores_capacity(conn, doctor):
    row = conn.execute("SELECT * FROM schedules WHERE doctor_id = ?",
                       (doctor,)).fetchone()
    assert row["weekday"] == "Monday" and row["max_patients"] == 2
