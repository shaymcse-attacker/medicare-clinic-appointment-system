# MediCare — Clinic Appointment System

A web-based clinic appointment system built with Flask and SQLite.
Patients register, search doctors by specialization, book appointments
against a doctor's weekly schedule, pay the consultation fee and receive
confirmation notifications. Doctors manage schedules; the admin manages
doctors and reports.

## Features
- Registration and login with hashed passwords (patient / doctor / admin roles)
- Doctor profiles and weekly chamber schedules with slot capacity
- Appointment booking with double-booking prevention
- Three appointment types (regular, follow-up, emergency) via a Factory
- Online payment through a gateway interface (mocked in tests)
- Email/SMS notifications via the Observer pattern
- Patient dashboard with appointment history

## Tech stack
Python 3, Flask, SQLite, PyTest (+ unittest.mock), Selenium (one UI test),
GitHub Actions for CI.

## Setup
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python run.py        # http://127.0.0.1:5000
```

## Run the tests
```bash
pytest --cov=app
```

## Branch naming
- `feature/<short-name>` for new features, e.g. `feature/online-payment`
- `bugfix/<short-name>` for fixes, e.g. `bugfix/slot-validation`
- `docs/<short-name>` for documentation
- Work is merged into `main` only through pull requests with green CI.

## Design patterns
- **Singleton** — `Database` connection manager
- **Factory Method** — `AppointmentFactory` for appointment types
- **Observer** — `NotificationService` with email/SMS observers
