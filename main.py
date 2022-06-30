import random
from copy import copy

import uvicorn
from fastapi import FastAPI, Request, Form, Cookie
from fastapi.responses import FileResponse, HTMLResponse
import psycopg2
import mariadb
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from enum import Enum
import sys


class DataBaseType(Enum):
    POSTGRES = 1
    MARIA = 2


db_type = None


def db_request_postgres(query: str):
    con = psycopg2.connect(database="sql-labs", user="postgres",
                           password="qwerlodaza", host="127.0.0.1", port="5432")
    cur = con.cursor()
    cur.execute(query)
    rows = cur.fetchall()

    cur.close()
    con.close()

    return rows


def db_request_maria(query: str):
    con = mariadb.connect(database="test", user="root",
                           password="qwerlodaza", host="127.0.0.1", port=3306)
    cur = con.cursor()
    cur.execute(query)
    rows = cur.fetchall()

    cur.close()
    con.close()

    return rows


def get_news(rows):
    news_rows = []
    news_row = []
    for i in range(len(rows)):
        news_row.append({'title': rows[i][0], 'text': rows[i][1], 'image_name': rows[i][2]})
        if i % 3 == 2:
            news_rows.append(copy(news_row))
            news_row.clear()
    if len(news_row) != 0:
        news_rows.append(copy(news_row))
    return news_rows


def check_cookie(session):
    cookie_query = f"SELECT * FROM cookies WHERE cookie='{session}'"
    cookie_rows = None
    if db_type == DataBaseType.MARIA:
        cookie_rows = db_request_maria(cookie_query)
    else:
        cookie_rows = db_request_postgres(cookie_query)


def get_new_cookie() -> str:
    cookie_id = random.randint(0, 19)
    cookie_query = f"SELECT cookie FROM cookies WHERE id='{cookie_id}'"
    cookie_rows = None
    if db_type == DataBaseType.MARIA:
        cookie_rows = db_request_maria(cookie_query)
    else:
        cookie_rows = db_request_postgres(cookie_query)
    return cookie_rows[0][0]


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates/victim")


@app.get("/filter", response_class=HTMLResponse)
async def use_filter(request: Request, category: str, session: str = Cookie("")):
    check_cookie(session)
    query = f"SELECT title, body, image_name FROM news WHERE category='{category}' AND hidden=0"
    rows = None
    if db_type == DataBaseType.MARIA:
        rows = db_request_maria(query)
    else:
        rows = db_request_postgres(query)
    response = templates.TemplateResponse("index.html",
                                          {"request": request, "news_rows": get_news(rows), "category": category})
    if not session:
        response.set_cookie("session", get_new_cookie())
    return response


@app.get("/", response_class=HTMLResponse)
async def show_all(request: Request, session: str = Cookie("")):
    check_cookie(session)
    query = f"SELECT title, body, image_name FROM news WHERE hidden=0"
    rows = None
    if db_type == DataBaseType.MARIA:
        rows = db_request_maria(query)
    else:
        rows = db_request_postgres(query)
    response = templates.TemplateResponse("index.html",
                                          {"request": request, "news_rows": get_news(rows), "category": "All"})
    if not session:
        response.set_cookie("session", get_new_cookie())
    return response


@app.get("/passwords")
async def get_passwords():
    return FileResponse("files/passwords_temp.txt")


@app.get("/image/{image_name}")
async def get_image(image_name: str):
    return FileResponse(f'Images/{image_name}')


@app.get("/login", response_class=HTMLResponse)
async def open_login(request: Request, session: str = Cookie("")):
    response = templates.TemplateResponse("auth.html", {"request": request})
    if not session:
        response.set_cookie("session", get_new_cookie())
    return response


@app.post("/auth")
async def login(request: Request, username: str = Form(), password: str = Form()):
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    rows = None
    if db_type == DataBaseType.MARIA:
        rows = db_request_maria(query)
    else:
        rows = db_request_postgres(query)
    if len(rows) > 0:
        return 1
    else:
        return 0


if __name__ == "__main__":
    if sys.argv[1] == 'postgres':
        db_type = DataBaseType.POSTGRES
        uvicorn.run(app, host="127.0.0.1", port=8000)
    elif sys.argv[1] == 'maria':
        db_type = DataBaseType.MARIA
        uvicorn.run(app, host="127.0.0.1", port=8001)
