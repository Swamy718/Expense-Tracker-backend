from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date
from typing import List, Literal
import uuid

ExpenseCategory = Literal[
    "Housing",
    "Food",
    "Transportation",
    "Utilities",
    "Healthcare",
    "Entertainment",
    "Others",
]


class Expense(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    amount: float
    category: str
    subcategory: ExpenseCategory
    emoji: str
    source_date: datetime
    created_at: datetime = Field(default_factory=datetime.now)


class ExpenseCreate(BaseModel):
    amount: float
    category: str
    subcategory: ExpenseCategory
    emoji: str
    source_date: date


class Income(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    amount: float
    source: str
    emoji: str
    source_date: datetime
    created_at: datetime = Field(default_factory=datetime.now)


class IncomeCreate(BaseModel):
    amount: float
    source: str
    emoji: str
    source_date: date


class User(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.now)
    income_list: List[Income] = Field(default_factory=list)
    expense_list: List[Expense] = Field(default_factory=list)


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
