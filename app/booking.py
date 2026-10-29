from datetime import datetime

from .factory import AppointmentFactory


class BookingResult:
    def __init__(self, status, appointment_id=None, fee=0.0):
        self.status = status
        self.appointment_id = appointment_id
        self.fee = fee


def _slot_capacity(conn, doctor_id, date_str):
    weekday = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")
    row = conn.execute(
        "SELECT max_patients FROM schedules WHERE doctor_id = ? AND weekday = ?",
        (doctor_id, weekday),
    ).fetchone()
    return None if row is None else row["max_patients"]


def _booked_count(conn, doctor_id, date_str, time_slot):
    row = conn.execute(
        "SELECT COUNT(*) AS n FROM appointments"
        " WHERE doctor_id = ? AND date = ? AND time_slot = ? AND status = 'Confirmed'",
        (doctor_id, date_str, time_slot),
    ).fetchone()
    return row["n"]


def book_appointment(conn, patient_id, doctor_id, date_str, time_slot,
                     appt_type, gateway, notifier=None):
    spec = AppointmentFactory.create(appt_type)

    capacity = _slot_capacity(conn, doctor_id, date_str)
    if capacity is None:
        return BookingResult("DoctorUnavailable")
    if _booked_count(conn, doctor_id, date_str, time_slot) >= capacity:
        return BookingResult("SlotFull")

    cur = conn.execute(
        "INSERT INTO appointments (patient_id, doctor_id, date, time_slot, type,"
        " duration_min, fee, status) VALUES (?, ?, ?, ?, ?, ?, ?, 'Pending')",
        (patient_id, doctor_id, date_str, time_slot, spec.type,
         spec.duration_min, spec.fee),
    )
    conn.commit()
    appt_id = cur.lastrowid

    paid = gateway.charge(spec.fee)
    pay_status = "Paid" if paid else "Failed"
    conn.execute(
        "INSERT INTO payments (appointment_id, amount, method, status) VALUES (?, ?, 'card', ?)",
        (appt_id, spec.fee, pay_status),
    )
    if not paid:
        conn.execute("UPDATE appointments SET status = 'PaymentFailed' WHERE id = ?", (appt_id,))
        conn.commit()
        return BookingResult("PaymentFailed", appt_id, spec.fee)

    conn.execute("UPDATE appointments SET status = 'Confirmed' WHERE id = ?", (appt_id,))
    conn.commit()

    if notifier is not None:
        msg = (f"Appointment #{appt_id} confirmed for {date_str} at {time_slot} "
               f"({spec.type}, fee {spec.fee:.0f}).")
        notifier.notify(patient_id, msg)
        notifier.notify(doctor_id, msg)
    return BookingResult("Confirmed", appt_id, spec.fee)


def cancel_appointment(conn, appointment_id):
    row = conn.execute("SELECT status FROM appointments WHERE id = ?",
                       (appointment_id,)).fetchone()
    if row is None:
        return False
    conn.execute("UPDATE appointments SET status = 'Cancelled' WHERE id = ?",
                 (appointment_id,))
    conn.commit()
    return True
