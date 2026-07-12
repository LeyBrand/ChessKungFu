import time


class RealTimeArbiter:
    _instance = None

    def __init__(self):
        # נעילת רגע אמיתי אחד כבסיס - זהו "אפס" המערכת, מעוגן לזמן אמת
        self._base_wall_time_ms = time.time() * 1000
        self._elapsed_virtual_ms = 0

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = RealTimeArbiter()
        return cls._instance

    def now(self):
        # הזמן "הרשמי" הנוכחי - זמן אמת בסיסי + כל מה שקודם דרך wait
        return self._base_wall_time_ms + self._elapsed_virtual_ms

    def advance(self, ms):
        self._elapsed_virtual_ms += ms

    def reset(self):
        self._base_wall_time_ms = time.time() * 1000
        self._elapsed_virtual_ms = 0