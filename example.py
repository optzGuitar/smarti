from smarti import autowired


@autowired(db_default="main")
class ServiceA:
    def __init__(self, db: str) -> None:
        pass


class ServiceB:
    def __init__(self, serviceA: ServiceA) -> None:
        pass


class ServiceC:
    pass


@autowired
class MainService:
    def __init__(self, serviceB: ServiceB, serviceC: ServiceC) -> None:
        self.serviceB = serviceB
        self.serviceC = serviceC


service = MainService()
