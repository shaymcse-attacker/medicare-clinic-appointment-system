import os
import sys
from unittest.mock import Mock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import Database
from app.services import register_user, add_schedule


@pytest.fixture()
def conn():
    Database.reset_instance()
    Database.configure(":memory:")
    c = Database.getInstance().get_connection()
    yield c
    Database.reset_instance()


@pytest.fixture()
def doctor(conn):
    doc_id = register_user(conn, "Dr. Rahman", "rahman@clinic.com", "secret1",
                           role="doctor", specialization="Cardiology",
                           chamber="Room 5")
    # 2026-11-02 is a Monday
    add_schedule(conn, doc_id, "Monday", "09:00", "13:00", 2)
    return doc_id


@pytest.fixture()
def patient(conn):
    return register_user(conn, "Karim", "karim@mail.com", "secret1",
                         role="patient", phone="01700000000")
