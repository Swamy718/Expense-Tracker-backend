from fastapi import FastAPI
from .database import collection
from app.auth.auth_routes import user_router
from app.auth.income_routes import income_router
from app.auth.expense_routes import expense_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(user_router)
app.include_router(income_router)
app.include_router(expense_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


