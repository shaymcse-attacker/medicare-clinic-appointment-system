from werkzeug.security import generate_password_hash, check_password_hash


def register_user(conn, name, email, password, role="patient", phone="",
                  specialization="", chamber=""):
    if role not in ("patient", "doctor", "admin"):
        raise ValueError("Invalid role")
    existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    if existing:
        raise ValueError("Email already registered")
    cur = conn.execute(
        "INSERT INTO users (name, email, password_hash, role, phone, specialization, chamber)"
        " VALUES (?, ?, ?, ?, ?, ?, ?)",
        (name, email, generate_password_hash(password), role, phone, specialization, chamber),
    )
    conn.commit()
    return cur.lastrowid


def authenticate(conn, email, password):
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if row is None:
        return None
    if not check_password_hash(row["password_hash"], password):
        return None
    return row


def add_schedule(conn, doctor_id, weekday, start_time, end_time, max_patients):
    cur = conn.execute(
        "INSERT INTO schedules (doctor_id, weekday, start_time, end_time, max_patients)"
        " VALUES (?, ?, ?, ?, ?)",
        (doctor_id, weekday, start_time, end_time, max_patients),
    )
    conn.commit()
    return cur.lastrowid


def search_doctors(conn, specialization=""):
    if specialization:
        rows = conn.execute(
            "SELECT * FROM users WHERE role = 'doctor' AND specialization LIKE ?",
            (f"%{specialization}%",),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM users WHERE role = 'doctor'").fetchall()
    return rows
