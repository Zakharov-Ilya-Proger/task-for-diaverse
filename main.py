import os
from datetime import datetime
from re import match
from typing import Annotated
from starlette.middleware.cors import CORSMiddleware
from uvicorn import run
from fastapi import FastAPI, HTTPException, Header
from create_jwt import create_access_token, decode_token
from models.models import Login
from paterns import email_pattern
from workWithDb import get_login, get_all_books, is_booked, book_the_book, my_books

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def passer():
    pass


@app.post("/login")
async def loginer(person: Login):
    if not match(email_pattern, person.email):
        raise HTTPException(status_code=400, detail="Email is invalid")
    return create_access_token(await get_login(person))


@app.get("/all/books")
async def get_books():
    response = await get_all_books()
    return response


@app.get("/book/booking/{book_id}/{date}")
async def booking_the_book(book_id: int, date: datetime, authorization: Annotated[str | None, Header()] = None):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header not found or empty")
    if await is_booked(book_id, decode_token(authorization.split(" ")[1])["id"]):
        raise HTTPException(status_code=409, detail="Book already booked")
    if await book_the_book(decode_token(authorization.split(" ")[1])["id"], book_id, date):
        raise HTTPException(status_code=200, detail="It's your book")
    raise HTTPException(status_code=404, detail="BooBoo")


@app.get("/my/books")
async def get_my_books(authorization: Annotated[str | None, Header()] = None):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header not found or empty")
    response = my_books(decode_token(authorization.split(" ")[1]))
    return response


if __name__ == '__main__':
    port = int(os.getenv("PORT", 8000))
    run(app, host="0.0.0.0", port=port)
