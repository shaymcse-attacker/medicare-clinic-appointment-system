from abc import ABC, abstractmethod


class PaymentGateway(ABC):
    """Interface for external payment services. Unit tests replace this
    with a mock so no real money is ever charged."""

    @abstractmethod
    def charge(self, amount, method="card"):
        raise NotImplementedError


class ManualGateway(PaymentGateway):
    """Default gateway used by the web app (pay at clinic / manual verify)."""

    def charge(self, amount, method="card"):
        return amount > 0
