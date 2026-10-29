import pytest

from app import create_app
from app.database import Database


@pytest.fixture()
def client():
    Database.reset_instance()
    app = create_app(":memory:")
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c
    Database.reset_instance()


def test_home_page_loads(client):
    assert client.get("/").status_code == 200


def test_login_page_loads(client):
    assert b"Login" in client.get("/login").data


def test_register_page_loads(client):
    assert b"Register" in client.get("/register").data


def test_register_then_login_flow(client):
    client.post("/register", data={"name": "Karim", "email": "k@mail.com",
                                   "password": "secret1", "role": "patient"})
    resp = client.post("/login", data={"email": "k@mail.com",
                                       "password": "secret1"},
                       follow_redirects=True)
    assert b"My Appointments" in resp.data


def test_login_with_wrong_password_stays_out(client):
    client.post("/register", data={"name": "Karim", "email": "k@mail.com",
                                   "password": "secret1", "role": "patient"})
    resp = client.post("/login", data={"email": "k@mail.com",
                                       "password": "bad"})
    assert b"Invalid email or password" in resp.data


def test_dashboard_requires_login(client):
    resp = client.get("/dashboard")
    assert resp.status_code == 302


def test_doctors_page_lists_doctor(client):
    client.post("/register", data={"name": "Dr. Rahman", "email": "r@c.com",
                                   "password": "secret1", "role": "doctor",
                                   "specialization": "Cardiology",
                                   "chamber": "Room 5"})
    resp = client.get("/doctors")
    assert b"Dr. Rahman" in resp.data
