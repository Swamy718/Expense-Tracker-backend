from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models import User, UserCreate
from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError
import os
from dotenv import load_dotenv
from database import collection
load_dotenv()

user_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def is_username_exist(username: str):
    if collection.find_one({"username": username}):
        return True
    else:
        return False

def is_email_exist(email: str):
    if collection.find_one({"email": email}):
        return True
    else:
        return False


@user_router.post("/register", status_code=201)
def create_user(user: UserCreate):
    if is_username_exist(user.username):
        raise HTTPException(status_code=400, detail="Username already exist")
    if is_email_exist(user.email):
        raise HTTPException(status_code=400, detail="Email already exist")

    hashed_pass = pwd_context.hash(user.password)
    new_user = User(
        username=user.username, email=user.email, hashed_password=hashed_pass
    )
    collection.insert_one(new_user.model_dump())
    return {"message": "User Created Successfully"}


@user_router.post("/token", status_code=200)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = collection.find_one({"username": form_data.username})
    if not user:
        user = collection.find_one({"email": form_data.username})

    if not user or not pwd_context.verify(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    token = create_access_token({"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}


def create_access_token(dic: dict):
    dc = dic.copy()
    expire_time = datetime.now(timezone.utc) + timedelta(
        minutes=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))
    )
    dc["exp"] = expire_time
    return jwt.encode(dc, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))


@user_router.get("/verify-token")
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="UnAuthorized")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return username


@user_router.get("/profile")
def get_curr_user(username: str = Depends(verify_token)):
    user = collection.find_one({"username": username})
    return {"username": username, "email": user["email"]}


@user_router.get("/info")
def get_user_info(username: str = Depends(verify_token)):
    user = collection.find_one({"username": username})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    ti = 0
    te = 0
    for income in user["income_list"]:
        ti += income["amount"]
    for expense in user["expense_list"]:
        te += expense["amount"]
    return {"income": ti, "expense": te}


@user_router.get("/recent-trans")
def get_recent_trans(username: str = Depends(verify_token)):
    user = collection.find_one({"username": username})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    lst = []
    for income in user["income_list"]:
        dct = income.copy()
        dct["type"] = "income"
        lst.append(dct)
    for expense in user["expense_list"]:
        dct = expense.copy()
        dct["type"] = "expense"
        lst.append(dct)
    lst.sort(
        key=lambda x: (
            x["source_date"]
            if isinstance(x["source_date"], datetime)
            else datetime.fromisoformat(x["source_date"])
        ),
        reverse=True,
    )
    return {"view": lst[0:5]}
