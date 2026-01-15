from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import UJSONResponse
from session import settings
from exceptions.http import register_exception_handlers
from messaging.kafka.producer import KafkaProducer
from src.routes.users_profiles import router as users_profiles_router
from src.routes.roles_comments import router as roles_comments_router
from src.routes.posts_orders import router as posts_orders_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    producer = KafkaProducer(settings)
    await producer.start()

    app.state.kafka_producer = producer

    try:
        yield
    finally:
        await producer.stop()


def get_app() -> FastAPI:
    app = FastAPI(
        docs_url="/docs",
        openapi_url="/openapi.json",
        default_response_class=UJSONResponse,
        lifespan=lifespan,  # ← ВОТ ЭТО ЕДИНСТВЕННОЕ ДОБАВЛЕНИЕ
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    app.include_router(users_profiles_router, prefix="api")
    app.include_router(roles_comments_router, prefix="api")
    app.include_router(posts_orders_router, prefix="api")

    return app


