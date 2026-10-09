from flask import Flask, render_template, request, redirect
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


def get_db_connection():
    return psycopg.connect(
        dbname="wishlist",
        user="postgres",
        password=os.getenv("DB_PASSWORD"),
        row_factory=dict_row
    )


@app.route("/")
def home():
    conn = get_db_connection()
    cur = conn.cursor()
    selected_category = request.args.get("category")

    if selected_category:
        cur.execute(
            "SELECT * FROM wishlist_items WHERE category = %s ORDER BY id",
            (selected_category,)
        )
    else:
        cur.execute("SELECT * FROM wishlist_items ORDER BY id")

    wishlist = cur.fetchall()
    cur.execute("SELECT name AS category FROM categories ORDER BY name")
    categories = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "index.html", 
        wishlist=wishlist, 
        categories=categories,
        selected_category=selected_category
        )

@app.route("/add", methods=["GET", "POST"])
def add_item():
    if request.method == "POST":
        name = request.form["name"]
        category = request.form["category"]

        if category == "__new__":
            category = request.form["new_category"].strip()

        if category:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO categories (name)
                VALUES (%s)
                ON CONFLICT (name) DO NOTHING
                """,
                (category,)
            )
            conn.commit()
            cur.close()
            conn.close()
        price = request.form["price"]
        priority = request.form["priority"]
        url = request.form["url"]
        description = request.form["description"]

        conn = get_db_connection()

        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO wishlist_items
            (name, category, price, currency, priority, url, description)
            VALUES (%s, %s, %s, 'CZK', %s, %s, %s)
            """,
            (name, category, price, priority, url, description)
        )

        conn.commit()
        cur.close()
        conn.close()

        return redirect("/")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT name AS category FROM categories ORDER BY name")
    categories = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("add_item.html", categories=categories)

@app.route("/edit/<int:item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    conn = get_db_connection()

    cur = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        category = request.form["category"]
        price = request.form["price"]
        priority = request.form["priority"]
        url = request.form["url"]
        description = request.form["description"]

        cur.execute(
            """
            UPDATE wishlist_items
            SET name = %s,
                category = %s,
                price = %s,
                priority = %s,
                url = %s,
                description = %s
            WHERE id = %s
            """,
            (name, category, price, priority, url, description, item_id)
        )

        conn.commit()
        cur.close()
        conn.close()

        return redirect("/")

    cur.execute(
        "SELECT * FROM wishlist_items WHERE id = %s",
        (item_id,)
    )
    item = cur.fetchone()
    cur.execute("SELECT name AS category FROM categories ORDER BY name")
    categories = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("edit_item.html", item=item, categories=categories)

@app.route("/delete/<int:item_id>", methods=["POST"])
def delete_item(item_id):
    conn = get_db_connection()

    cur = conn.cursor()

    cur.execute(
        "DELETE FROM wishlist_items WHERE id = %s",
        (item_id,)
    )

    conn.commit()
    cur.close()
    conn.close()

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)