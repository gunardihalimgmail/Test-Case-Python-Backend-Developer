# app/main.py
from fastapi import FastAPI
from app.auth import routes as auth_routes
from app.tasks import routes as task_routes


app = FastAPI(title="Mini Task Manager API")
app.include_router(auth_routes.router)
app.include_router(task_routes.router)

# uvicorn app.main:app --reload