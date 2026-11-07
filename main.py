from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from secrets import token_urlsafe
from typing import Literal
from datetime import datetime

app = FastAPI()
users = {}
balances = {}

class UserRegisterResponse(BaseModel):
    id: UUID
    name: str
    role: Literal["USER", "ADMIN"]
    api_key: str

class DepositBody(BaseModel):
    user_id: UUID
    ticker: str
    amount: int = Field(gt=0)

class UserRegisterRequest(BaseModel):
    name: str = Field(min_length=3)

class InstrumentResponse(BaseModel):
    name: str
    ticker: str = Field(pattern=r"^[A-Z]{2,10}$")

class InstrumentCreateRequest(BaseModel):
    name: str
    ticker: str = Field(pattern=r"^[A-Z]{2,10}$")

class InstrumentCreateResponse(BaseModel):
    success: Literal[True] = True

class InstrumentDeleteResponse(BaseModel):
    success: Literal[True] = True

class OrderBookLevelResponse(BaseModel):
    price: int
    qty: int

class OrderBookResponse(BaseModel):
    bid_levels: list[OrderBookLevelResponse]
    ask_levels: list[OrderBookLevelResponse]

class TransactionResponse(BaseModel):
    ticker: str
    amount: int
    price: int
    timestamp: datetime

@app.get("/")
def home():
    return{"msg": "Биржа работает"}

@app.post("/api/v1/public/register", response_model=UserRegisterResponse, tags=["public"])
def register(user: UserRegisterResponse):
    new_user =  {"id": str(uuid4()), 
            "name": user.name, 
            "role": "USER", 
            "api_key": token_urlsafe(32)}
    users[new_user["id"]] = new_user
    balances[new_user["id"]] = {"RUB": 0}
    return new_user

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

def get_current_user(authorization: str | None = Depends(api_key_header)):
    if authorization is None or not authorization.startswith("TOKEN "):
        raise HTTPException(status_code=401, detail="Неверный формат авторизации")
    
    token = authorization.removeprefix("TOKEN ")

    for saved_user in users.values():
        if token == saved_user["api_key"]:
            return saved_user
        
    raise HTTPException(status_code=401, detail="Неверный токен")

@app.get("/api/v1/balance")
def get_balance(current_user: dict = Depends(get_current_user)):
    return balances[current_user["id"]]

def get_admin(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "ADMIN":
        raise HTTPException(status_code=403,detail="Недостаточно прав")

    return current_user

@app.post("/api/v1/admin/balance/deposit")
def deposit(body: DepositBody, admin: dict = Depends(get_admin)):
    user_id = str(body.user_id)
    if user_id not in users:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    balances[user_id][body.ticker] = (balances[user_id].get(body.ticker, 0) + body.amount)
    return {"success": True}

@app.get("/api/v1/public/instrument", response_model=list[InstrumentResponse],tags=["public"])
def list_instruments():
    raise HTTPException(status_code=501, detail="Метод пока не реализован")

@app.post("/api/v1/admin/instrument", response_model=InstrumentCreateResponse)
def add_instrument(body: InstrumentCreateRequest):
    raise HTTPException(status_code=501, detail="Метод пока не реализован")

@app.delete("/api/v1/admin/instrument/{ticker}", response_model=InstrumentDeleteResponse)
def delete_instrument(ticker:str):
    raise HTTPException(status_code = 501, detail="Метод пока не реализован")

@app.get("/api/v1/public/orderbook/{ticker}", response_model=OrderBookResponse, tags=["public"])
def get_orderbook(ticker: str, limit: int = Query(default=10, le=25)):
    raise HTTPException(status_code=501, detail="Метод пока не реализован")

@app.get("/api/v1/public/transactions/{ticker}", response_model = list[TransactionResponse])
def history_transactions(ticker: str, limit: int = Query(default=10, le=100)):
    raise HTTPException(status_code=501, detail="Метод пока не реализован")