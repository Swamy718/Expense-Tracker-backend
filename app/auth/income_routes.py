from fastapi import APIRouter, HTTPException, Depends
from .auth_routes import verify_token
from models import Income, IncomeCreate
from database import collection
from datetime import datetime, time

income_router = APIRouter()


@income_router.post("/income")
def add_income(income: IncomeCreate, username: str = Depends(verify_token)):
    income_to_add = Income(
        amount=income.amount,
        source=income.source,
        emoji=income.emoji,
        source_date=datetime.combine(income.source_date, time.min),
    )
    result = collection.update_one(
        {"username": username}, {"$push": {"income_list": income_to_add.model_dump()}}
    )
    if result.modified_count == 0:
        raise HTTPException(
            status_code=404, detail="User not found or income not added"
        )
    return {"message": "Income added successfully"}


@income_router.delete("/income")
def delete_income(income_id: str, username: str = Depends(verify_token)):
    result = collection.update_one(
        {"username": username}, {"$pull": {"income_list": {"id": income_id}}}
    )
    if result.modified_count == 0:
        raise HTTPException(
            status_code=404, detail="Income not found or already deleted"
        )
    return {"message": "Income deleted successfully"}


@income_router.get("/incomebymonth")
def get_income(month: int, username: str = Depends(verify_token)):
    user = collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    incomes = user.get("income_list", [])
    filtered_incomes = []
    for income in incomes:
        if income["source_date"].month == month:
            filtered_incomes.append(
                {
                    "amount": income["amount"],
                    "source": income["source"],
                    "emoji": income["emoji"],
                    "date": income["source_date"],
                }
            )
    return {"incomes": filtered_incomes}


@income_router.get("/income/last10days")
def get_ten_incomes(username: str = Depends(verify_token)):
    user = collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    incomes = user.get("income_list", [])
    daily_income_list = {}
    for income in incomes:
        dt_obj = income["source_date"]
        date_str = dt_obj.strftime("%Y-%m-%d")
        daily_income_list[date_str] = (
            daily_income_list.get(date_str, 0) + income["amount"]
        )

    sorted_items = sorted(daily_income_list.items())

    last_10 = sorted_items[-10:]

    dates = [item[0] for item in last_10]
    incomes_list = [item[1] for item in last_10]

    return {"dates": dates, "incomes": incomes_list}


@income_router.get("/income/last5days")
def get_five_incomes(username: str = Depends(verify_token)):
    user = collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    incomes = user.get("income_list", [])
    daily_income_list = {}
    for income in incomes:
        dt_obj = income["source_date"]
        date_str = dt_obj.strftime("%Y-%m-%d")
        daily_income_list[date_str] = (
            daily_income_list.get(date_str, 0) + income["amount"]
        )

    sorted_items = sorted(daily_income_list.items())

    last_10 = sorted_items[-5:]

    dates = [item[0] for item in last_10]
    incomes_list = [item[1] for item in last_10]

    return {"dates": dates, "incomes": incomes_list}


@income_router.get("/income")
def get_incomes(username: str = Depends(verify_token)):
    user = collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    incomes = user.get("income_list", [])
    filtered_incomes = []
    for income in incomes:
        dt_obj = income["source_date"]
        date_str = dt_obj.strftime("%Y-%m-%d")
        filtered_incomes.append(
            {
                "amount": income["amount"],
                "source": income["source"],
                "emoji": income["emoji"],
                "date": date_str,
                "id": income["id"],
            }
        )
    return {"incomes": filtered_incomes}


@income_router.get("/recent-incomes")
def get_recent_incomes(username: str = Depends(verify_token)):
    user = collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    incomes = user.get("income_list", [])
    incomes.sort(
        key=lambda x: (
            x["source_date"]
            if isinstance(x["source_date"], datetime)
            else datetime.fromisoformat(x["source_date"])
        ),
        reverse=True,
    )
    return {"incomes": incomes[0:5]}
