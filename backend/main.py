import os
from copy import copy

import uvicorn
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
import psycopg2
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from db_gen import fill_db


def db_request_postgres(query: str, params: tuple):
    con = psycopg2.connect(database="db", user="postgres", host="db",
                           password="postgres", port="5432")
    cur = con.cursor()
    cur.execute(query, params)
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


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates/victim")


@app.get("/filter", response_class=HTMLResponse)
async def use_filter(request: Request, category: str):
    query = "SELECT title, body, image_name FROM news WHERE category=%s AND hidden=0"
    try:
        rows = db_request_postgres(query, (category,))
    except Exception:
        rows = []
    response = templates.TemplateResponse("index.html",
                                          {"request": request, "news_rows": get_news(rows), "category": category})
    return response


@app.get("/", response_class=HTMLResponse)
async def show_all(request: Request):
    query = "SELECT title, body, image_name FROM news WHERE hidden=0"
    rows = db_request_postgres(query, ())
    response = templates.TemplateResponse("index.html",
                                          {"request": request, "news_rows": get_news(rows), "category": "All"})
    return response


@app.get("/image")
async def get_image(image_name: str):
    if ".." in image_name or not os.path.exists(f"Images/{image_name}"):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(f'Images/{image_name}')


@app.get("/login", response_class=HTMLResponse)
async def open_login(request: Request):
    response = templates.TemplateResponse("auth.html", {"request": request})
    return response


@app.post("/auth")
async def login(request: Request, username: str = Form(), password: str = Form()):
    query = "SELECT * FROM users WHERE username=%s AND password=%s"
    rows = db_request_postgres(query, (username, password))
    if len(rows) > 0:
        return 'accepted'
    else:
        return 'wrong username or password'


if __name__ == "__main__":
    try:
        fill_db()
    except Exception:
        print("Error during database creation")
    uvicorn.run(app, host="0.0.0.0", port=8000)
