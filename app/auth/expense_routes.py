from fastapi import APIRouter, HTTPException, Depends
from .auth_routes import verify_token
from app.models import Expense, ExpenseCreate
from app.database import collection
from datetime import datetime, time

expense_router = APIRouter()


@expense_router.post("/expense", status_code=201)
def add_expense(expense: ExpenseCreate, username: str = Depends(verify_token)):
    expense_to_add = Expense(
        amount=expense.amount,
        category=expense.category,
        subcategory=expense.subcategory,
        emoji=expense.emoji,
        source_date=datetime.combine(expense.source_date, time.min),
    )
    result = collection.update_one(
        {"username": username}, {"$push": {"expense_list": expense_to_add.model_dump()}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Expense added successfully"}


@expense_router.delete("/expense")
def delete_expense(expense_id: str, username: str = Depends(verify_token)):
    result = collection.update_one(
        {"username": username}, {"$pull": {"expense_list": {"id": expense_id}}}
    )
    if result.modified_count == 0:
        raise HTTPException(
            status_code=404, detail="Expense not found or already deleted"
        )
    return {"message": "Expense deleted successfully"}


@expense_router.get("/expensebymonth")
def get_expense(month: int, username: str = Depends(verify_token)):
    user = collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    expenses = user.get("expense_list", [])
    filtered_expenses = []
    for expense in expenses:
        if expense["source_date"].month == month:
            filtered_expenses.append(
                {
                    "amount": expense["amount"],
                    "category": expense["category"],
                    "subcategory": expense["subcategory"],
                    "emoji": expense["emoji"],
                    "date": expense["source_date"],
                }
            )
    return {"expenses": filtered_expenses}


@expense_router.get("/expense")
def get_expenses(username: str = Depends(verify_token)):
    user = collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    expenses = user.get("expense_list", [])
    filtered_expenses = []
    for expense in expenses:
        dt_obj = expense["source_date"]
        date_str = dt_obj.strftime("%Y-%m-%d")
        filtered_expenses.append(
            {
                "amount": expense["amount"],
                "source": expense["category"],
                "emoji": expense["emoji"],
                "date": date_str,
                "id": expense["id"],
            }
        )
    return {"expenses": filtered_expenses}


@expense_router.get("/expense/last10days")
def get_ten_expenses(username: str = Depends(verify_token)):
    user = collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    expenses = user.get("expense_list", [])
    daily_expense_list = {}
    for expense in expenses:
        dt_obj = expense["source_date"]
        date_str = dt_obj.strftime("%Y-%m-%d")
        daily_expense_list[date_str] = (
            daily_expense_list.get(date_str, 0) + expense["amount"]
        )

    sorted_items = sorted(daily_expense_list.items())

    last_10 = sorted_items[-10:]

    dates = [item[0] for item in last_10]
    expenses_list = [item[1] for item in last_10]

    return {"dates": dates, "expenses": expenses_list}


@expense_router.get("/recent-expenses")
def get_recent_expenses(username: str = Depends(verify_token)):
    user = collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    expenses = user.get("expense_list", [])
    expenses.sort(
        key=lambda x: (
            x["source_date"]
            if isinstance(x["source_date"], datetime)
            else datetime.fromisoformat(x["source_date"])
        ),
        reverse=True,
    )
    return {"expenses": expenses[0:5]}


@expense_router.get("/expense/subcategory")
def get_subcategory_expenses(username: str = Depends(verify_token)):
    user = collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    expenses = user.get("expense_list", [])
    dct = {}
    for expense in expenses:
        dct[expense["subcategory"]] = (
            dct.get(expense["subcategory"], 0) + expense["amount"]
        )

    return {"expenses": dct}

