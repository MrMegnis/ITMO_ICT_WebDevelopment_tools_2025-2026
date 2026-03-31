from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.budgets import router as budgets_router
from app.routers.categories import router as categories_router
from app.routers.goals import router as goals_router
from app.routers.reports import router as reports_router
from app.routers.tags import router as tags_router
from app.routers.transactions import router as transactions_router
from app.routers.users import router as users_router

app = FastAPI(title="Lab 1 - Personal Finance API")

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(categories_router)
app.include_router(tags_router)
app.include_router(transactions_router)
app.include_router(budgets_router)
app.include_router(goals_router)
app.include_router(reports_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Personal Finance API is running"}

