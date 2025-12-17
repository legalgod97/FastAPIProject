class ServiceError(Exception):
    """Базовое исключение сервиса"""


class NotFoundError(ServiceError):
    def __init__(self, entity: str):
        self.entity = entity
        super().__init__(f"{entity} not found")