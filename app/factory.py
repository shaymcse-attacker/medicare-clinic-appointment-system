class AppointmentSpec:
    def __init__(self, type_name, duration_min, fee):
        self.type = type_name
        self.duration_min = duration_min
        self.fee = fee


class AppointmentFactory:
    """Factory Method: creates the spec for each appointment type so the
    duration and fee rules live in exactly one place."""

    _TYPES = {
        "regular": (30, 500.0),
        "follow-up": (15, 300.0),
        "emergency": (45, 1000.0),
    }

    @staticmethod
    def create(type_name):
        if type_name not in AppointmentFactory._TYPES:
            raise ValueError(f"Unknown appointment type: {type_name}")
        duration, fee = AppointmentFactory._TYPES[type_name]
        return AppointmentSpec(type_name, duration, fee)

    @staticmethod
    def available_types():
        return list(AppointmentFactory._TYPES.keys())
