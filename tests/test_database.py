from app.database import Database


def test_singleton_returns_same_instance(conn):
    assert Database.getInstance() is Database.getInstance()


def test_singleton_connection_is_shared(conn):
    assert Database.getInstance().get_connection() is conn
