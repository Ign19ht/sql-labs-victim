import string

import psycopg2
from faker import Faker
import os
import random


def generate_pass() -> str:
    symbols = string.ascii_letters + string.digits
    return ''.join(random.sample(symbols, 8))


news_types = ['Animals', 'IT', 'Innopolis', 'Recent']


def fill_db():
    con = psycopg2.connect(database="db", user="postgres", host="db",
                           password="postgres", port="5432")

    print("Database opened successfully")
    cur = con.cursor()
    cur.execute('''CREATE TABLE news
           (id int PRIMARY KEY     NOT NULL,
           category text,
           hidden int NOT NULL,
           title text,
           image_name text,
           body text);''')
    cur.execute('''CREATE TABLE users
           (id int PRIMARY KEY     NOT NULL,
           username text,
           password text);''')
    print("Tables created successfully")
    fake = Faker()
    for i in range(24):
        cur.execute(f"INSERT INTO users VALUES ({i}, '{fake.unique.first_name()}', '{generate_pass()}')")
        text = fake.text()
        title = text.split('.')[0]
        news_type = random.choice(news_types)
        image_name = random.randint(1, 5)
        extension = 'jfif' if news_type == 'Animals' else 'jpg'
        cur.execute(f"INSERT INTO news VALUES ({i} , '{news_type}' , {random.choices([0, 1], [9, 1])[0]} , '{title}' , '{news_type}_{image_name}.{extension}' , '{text}')")

    cur.execute(f"INSERT INTO users VALUES (24, 'administrator', '{generate_pass()}')")

    con.commit()
    print("DB generation complete")
