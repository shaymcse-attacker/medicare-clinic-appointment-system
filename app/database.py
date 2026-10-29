import sqlite3


class Database:
    """Singleton: the whole application shares one connection manager."""

    _instance = None
    _path = "medicare.db"

    def __init__(self):
        self._conn = sqlite3.connect(self._path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._create_tables()

    @classmethod
    def configure(cls, path):
        cls._path = path

    @classmethod
    def getInstance(cls):
        if cls._instance is None:
            cls._instance = Database()
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """Used by tests so each test run starts from a clean database."""
        if cls._instance is not None:
            cls._instance._conn.close()
        cls._instance = None

    def get_connection(self):
        return self._conn

    def _create_tables(self):
        cur = self._conn.cursor()
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                phone TEXT DEFAULT '',
                specialization TEXT DEFAULT '',
                chamber TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doctor_id INTEGER NOT NULL,
                weekday TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                max_patients INTEGER NOT NULL DEFAULT 10
            );
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                doctor_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                time_slot TEXT NOT NULL,
                type TEXT NOT NULL,
                duration_min INTEGER NOT NULL,
                fee REAL NOT NULL,
                status TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                method TEXT NOT NULL,
                status TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                channel TEXT NOT NULL,
                message TEXT NOT NULL
            );
            """
        )
        self._conn.commit()
