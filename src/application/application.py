from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import UJSONResponse

from src.routes.users_profiles import router as users_profiles_router
from src.routes.roles_comments import router as roles_comments_router
from src.routes.posts_orders import router as posts_orders_router

def get_app() -> FastAPI:
    app = FastAPI(
        docs_url="/docs",
        openapi_url="/openapi.json",
        default_response_class=UJSONResponse,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(users_profiles_router)
    app.include_router(roles_comments_router)
    app.include_router(posts_orders_router)

    return app
