from unittest.mock import Mock

from app.booking import book_appointment, cancel_appointment

MONDAY = "2026-11-02"   # a Monday, matches the doctor fixture schedule
TUESDAY = "2026-11-03"  # doctor has no schedule on Tuesday


def test_booking_success(conn, doctor, patient, gateway_ok):
    result = book_appointment(conn, patient, doctor, MONDAY, "10:00",
                              "regular", gateway_ok)
    assert result.status == "Confirmed"
    assert result.fee == 500.0
    gateway_ok.charge.assert_called_once_with(500.0)


def test_booking_followup_fee(conn, doctor, patient, gateway_ok):
    result = book_appointment(conn, patient, doctor, MONDAY, "10:00",
                              "follow-up", gateway_ok)
    assert result.status == "Confirmed" and result.fee == 300.0


def test_booking_doctor_unavailable_day(conn, doctor, patient, gateway_ok):
    result = book_appointment(conn, patient, doctor, TUESDAY, "10:00",
                              "regular", gateway_ok)
    assert result.status == "DoctorUnavailable"
    gateway_ok.charge.assert_not_called()


def test_booking_slot_full_rejected(conn, doctor, patient, gateway_ok):
    # schedule capacity is 2 for the slot
    p2 = patient + 100  # ids need not exist for the count logic
    book_appointment(conn, patient, doctor, MONDAY, "10:00", "regular", gateway_ok)
    book_appointment(conn, p2, doctor, MONDAY, "10:00", "regular", gateway_ok)
    third = book_appointment(conn, p2 + 1, doctor, MONDAY, "10:00",
                             "regular", gateway_ok)
    assert third.status == "SlotFull"


def test_booking_other_slot_still_free(conn, doctor, patient, gateway_ok):
    book_appointment(conn, patient, doctor, MONDAY, "10:00", "regular", gateway_ok)
    book_appointment(conn, patient, doctor, MONDAY, "10:00", "regular", gateway_ok)
    other = book_appointment(conn, patient, doctor, MONDAY, "11:00",
                             "regular", gateway_ok)
    assert other.status == "Confirmed"


def test_booking_payment_failure(conn, doctor, patient, gateway_fail):
    result = book_appointment(conn, patient, doctor, MONDAY, "10:00",
                              "regular", gateway_fail)
    assert result.status == "PaymentFailed"
    row = conn.execute("SELECT status FROM appointments WHERE id = ?",
                       (result.appointment_id,)).fetchone()
    assert row["status"] == "PaymentFailed"
    pay = conn.execute("SELECT status FROM payments WHERE appointment_id = ?",
                       (result.appointment_id,)).fetchone()
    assert pay["status"] == "Failed"


def test_failed_payment_does_not_consume_slot(conn, doctor, patient,
                                             gateway_fail, gateway_ok):
    book_appointment(conn, patient, doctor, MONDAY, "10:00", "regular", gateway_fail)
    ok = book_appointment(conn, patient, doctor, MONDAY, "10:00",
                          "regular", gateway_ok)
    assert ok.status == "Confirmed"


def test_booking_sends_notifications(conn, doctor, patient, gateway_ok):
    notifier = Mock()
    book_appointment(conn, patient, doctor, MONDAY, "10:00", "regular",
                     gateway_ok, notifier)
    assert notifier.notify.call_count == 2  # patient and doctor


def test_cancel_appointment(conn, doctor, patient, gateway_ok):
    result = book_appointment(conn, patient, doctor, MONDAY, "10:00",
                              "regular", gateway_ok)
    assert cancel_appointment(conn, result.appointment_id) is True
    row = conn.execute("SELECT status FROM appointments WHERE id = ?",
                       (result.appointment_id,)).fetchone()
    assert row["status"] == "Cancelled"


def test_cancel_unknown_appointment(conn):
    assert cancel_appointment(conn, 9999) is False


def test_cancelled_slot_can_be_rebooked(conn, doctor, patient, gateway_ok):
    r1 = book_appointment(conn, patient, doctor, MONDAY, "10:00", "regular", gateway_ok)
    book_appointment(conn, patient, doctor, MONDAY, "10:00", "regular", gateway_ok)
    cancel_appointment(conn, r1.appointment_id)
    again = book_appointment(conn, patient, doctor, MONDAY, "10:00",
                             "regular", gateway_ok)
    assert again.status == "Confirmed"
