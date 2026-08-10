from fastapi import FastAPI

# from sqlalchemy import text
# from app.db.database import engine
from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as users_router
from app.api.routes.permissions import router as permissions_router
from app.api.routes.category import router as category_router
from app.api.routes.platform import router as platform_router


app = FastAPI(
    title="Influencer & Creator Management System",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


# @app.get("/health/db")
# def database_health_check():
#     with engine.connect() as connection:
#         result = connection.execute(text("SELECT 1"))
#         value = result.scalar()

#     return {
#         "status": "ok",
#         "database": "connected",
#         "result": value,
#     }

routers = [
    auth_router,
    users_router,
    permissions_router,
    platform_router,
    category_router,
]
for router in routers:
    app.include_router(
        router,
        prefix="/api/v1",
    )
