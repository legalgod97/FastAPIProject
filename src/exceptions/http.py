from fastapi.responses import UJSONResponse
from starlette import status
from src.exceptions.common import NotFoundError, ValidationError


def register_exception_handlers(app):
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request, exc: NotFoundError):
        return UJSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "detail": f"{exc.entity} not found",
            },
        )


    @app.exception_handler(ValidationError)
    async def validation_handler(request, exc: ValidationError):
        return UJSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": f"{exc.entity} validation failed"},
        )