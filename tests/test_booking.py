from unittest.mock import Mock

from app.booking import book_appointment, cancel_appointment

MONDAY = "2026-11-02"   # a Monday, matches the doctor fixture schedule
TUESDAY = "2026-11-03"  # doctor has no schedule on Tuesday


def test_booking_success(conn, doctor, patient):
    result = book_appointment(conn, patient, doctor, MONDAY, "10:00", "regular")
    assert result.status == "Confirmed"
    assert result.fee == 500.0


def test_booking_followup_fee(conn, doctor, patient):
    result = book_appointment(conn, patient, doctor, MONDAY, "10:00", "follow-up")
    assert result.status == "Confirmed" and result.fee == 300.0


def test_booking_doctor_unavailable_day(conn, doctor, patient):
    result = book_appointment(conn, patient, doctor, TUESDAY, "10:00", "regular")
    assert result.status == "DoctorUnavailable"


def test_booking_slot_full_rejected(conn, doctor, patient):
    # schedule capacity is 2 for the slot
    book_appointment(conn, patient, doctor, MONDAY, "10:00", "regular")
    book_appointment(conn, patient, doctor, MONDAY, "10:00", "regular")
    third = book_appointment(conn, patient, doctor, MONDAY, "10:00", "regular")
    assert third.status == "SlotFull"


def test_booking_other_slot_still_free(conn, doctor, patient):
    book_appointment(conn, patient, doctor, MONDAY, "10:00", "regular")
    book_appointment(conn, patient, doctor, MONDAY, "10:00", "regular")
    other = book_appointment(conn, patient, doctor, MONDAY, "11:00", "regular")
    assert other.status == "Confirmed"


def test_booking_sends_notifications(conn, doctor, patient):
    notifier = Mock()
    book_appointment(conn, patient, doctor, MONDAY, "10:00", "regular", notifier)
    assert notifier.notify.call_count == 2  # patient and doctor


def test_cancel_appointment(conn, doctor, patient):
    result = book_appointment(conn, patient, doctor, MONDAY, "10:00", "regular")
    assert cancel_appointment(conn, result.appointment_id) is True
    row = conn.execute("SELECT status FROM appointments WHERE id = ?",
                       (result.appointment_id,)).fetchone()
    assert row["status"] == "Cancelled"


def test_cancel_unknown_appointment(conn):
    assert cancel_appointment(conn, 9999) is False


def test_cancelled_slot_can_be_rebooked(conn, doctor, patient):
    r1 = book_appointment(conn, patient, doctor, MONDAY, "10:00", "regular")
    book_appointment(conn, patient, doctor, MONDAY, "10:00", "regular")
    cancel_appointment(conn, r1.appointment_id)
    again = book_appointment(conn, patient, doctor, MONDAY, "10:00", "regular")
    assert again.status == "Confirmed"
