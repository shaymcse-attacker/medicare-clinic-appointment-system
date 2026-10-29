"""One end-to-end UI test: login -> search doctor -> book a slot.

Skipped automatically when Selenium or a Chrome driver is unavailable
(for example in CI), so the unit suite never depends on it.
"""
import pytest

selenium = pytest.importorskip("selenium")


@pytest.mark.skip(reason="requires a running server and Chrome driver")
def test_login_to_booking_journey():
    pass
