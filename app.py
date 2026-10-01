from flask import Flask, render_template
import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

conn = psycopg.connect(
    dbname="wishlist",
    user="postgres",
    password=os.getenv("DB_PASSWORD"),
    row_factory=dict_row
)

print("Database connection successful!")
conn.close()

app = Flask(__name__)


@app.route("/")
def home():
    conn = psycopg.connect(
        dbname="wishlist",
        user="postgres",
        password=os.getenv("DB_PASSWORD"),
        row_factory=dict_row
    )

    cur = conn.cursor()
    cur.execute("SELECT * FROM wishlist_items ORDER BY id")
    wishlist = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("index.html", wishlist=wishlist)


if __name__ == "__main__":
    app.run(debug=True)