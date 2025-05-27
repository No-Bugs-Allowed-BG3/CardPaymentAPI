import uvicorn
from fastapi import FastAPI,APIRouter,HTTPException
from pydantic import BaseModel,Field
from typing import Annotated
from pydantic.types import StringConstraints
from decimal import Decimal
import sqlite3

app = FastAPI()

check_balance_router = APIRouter(prefix="/balance/checks")
withdraw_money_from_card_router = APIRouter(prefix="/cards/withdrawals")
pay_money_to_external_dealer_router = APIRouter(prefix="/payments")

class CardRequest(BaseModel):
    number:Annotated[str,StringConstraints(min_length=16,max_length=16,pattern=r"\d{16}")]
    cvv_code:Annotated[str,StringConstraints(min_length=3,max_length=3,pattern=r"\d{3}")]
    expiry:Annotated[str,StringConstraints(min_length=5,max_length=5,pattern=r"\d{2}/\d{2}")]
    requested_amount:Decimal = Field(gt=0)
    currency:Annotated[str,StringConstraints(min_length=3,max_length=3,pattern=r"[A-Z]{3}")]

class CardRequestIncoming(BaseModel):
    sender:Annotated[str,StringConstraints(min_length=16,max_length=16,pattern=r"\d{16}")]
    number:Annotated[str,StringConstraints(min_length=16,max_length=16,pattern=r"\d{16}")]
    incoming_amount:Decimal = Field(gt=0)
    currency:Annotated[str,StringConstraints(min_length=3,max_length=3,pattern=r"[A-Z]{3}")]

class CardResponse(BaseModel):
    number:Annotated[str,StringConstraints(min_length=16,max_length=16,pattern=r"\d{16}")]
    requested_amount:Decimal = Field(gt=0)
    approved:bool
    currency:Annotated[str,StringConstraints(min_length=3,max_length=3,pattern=r"[A-Z]{3}")]

def get_database_connection()-> sqlite3.Cursor:
    conn = sqlite3.connect("db/cardpayments.db")
    conn.row_factory = sqlite3.Row
    return conn.cursor()

def get_card_balance_query(req:CardRequest)->str:
    db_cursor = get_database_connection()
    query_string = "SELECT `balance` FROM `cards` WHERE `card_number`=? AND `currency`=?"
    query_parameters = (req.number,req.currency)
    query_result = db_cursor.execute(query_string,query_parameters)
    card_result = query_result.fetchone()
    db_cursor.connection.close()
    if not card_result:
        raise HTTPException(status_code=500,detail="Error while retrieving card balance!")
    return str(card_result["balance"])

def get_card_balance_query_incoming(req:CardRequestIncoming)->str:
    db_cursor = get_database_connection()
    query_string = "SELECT `balance` FROM `cards` WHERE `card_number`=? AND `currency`=?"
    query_parameters = (req.number,req.currency)
    query_result = db_cursor.execute(query_string,query_parameters)
    card_result = query_result.fetchone()
    db_cursor.connection.close()
    if not card_result:
        raise HTTPException(status_code=500,detail="Error while retrieving card balance!")
    return str(card_result["balance"])

def check_card_balance_query(req:CardRequest)->CardResponse:
    card_balance = get_card_balance_query(req=req)
    if Decimal(card_balance) >= req.requested_amount:
        approved = True
    else:
        approved = False
    return CardResponse(
        number=req.number,
        requested_amount=req.requested_amount,
        approved=approved,
        currency=req.currency
    )

def withdraw_money_from_card_query(req:CardRequest)->CardResponse:
    card_balance = get_card_balance_query(req=req)
    if Decimal(card_balance) >= req.requested_amount:
        new_card_balance = str(Decimal(card_balance)-req.requested_amount)
        db_cursor = get_database_connection()
        query_string = "UPDATE `cards` SET `balance`=? WHERE `card_number` = ? AND `cvv`=? AND `expiry`=? AND `currency`=?"
        query_parameters = (new_card_balance,req.number,req.cvv_code,req.expiry,req.currency)
        query_result = db_cursor.execute(query_string,query_parameters)
        if not query_result:
            raise HTTPException(status_code=500,detail="Error while withdrawing money!")
        if not query_result.rowcount:
            raise HTTPException(status_code=500,detail="Error while withdrawing money!")
        db_cursor.connection.commit()
        db_cursor.connection.close()
        return CardResponse(
            number=req.number,
            requested_amount=req.requested_amount,
            currency=req.currency,
            approved=True
        )
    else:
        return CardResponse(
            number=req.number,
            requested_amount=req.requested_amount,
            currency=req.currency,
            approved=False
        )

def pay_money_to_external_dealer_query(req:CardRequestIncoming)->bool:
    card_balance = get_card_balance_query_incoming(req=req)
    new_card_balance = str(Decimal(card_balance) + req.incoming_amount)
    db_cursor = get_database_connection()
    query_string = "UPDATE `cards` SET `balance`=? WHERE `card_number` = ? AND `currency`=?"
    query_parameters = (new_card_balance, req.number,req.currency)
    query_result = db_cursor.execute(query_string, query_parameters)
    if not query_result:
        return False
    if not query_result.rowcount:
        return False
    db_cursor.connection.commit()
    db_cursor.connection.close()
    return True

@check_balance_router.post("/")
def _check_balance(req:CardRequest)->CardResponse:
    return check_card_balance_query(req=req)

@withdraw_money_from_card_router.post("/")
def _withdraw_money(req:CardRequest)->CardResponse:
    return withdraw_money_from_card_query(req=req)

@pay_money_to_external_dealer_router.post("/")
def _pay_money(req:CardRequestIncoming)->bool:
    return pay_money_to_external_dealer_query(req=req)

app.include_router(check_balance_router)
app.include_router(withdraw_money_from_card_router)
app.include_router(pay_money_to_external_dealer_router)

if __name__ == "__main__":
    uvicorn.run(app="main:app",host="0.0.0.0",port=8002,reload=False)
