import csv
from flask import Flask, render_template, request, redirect, url_for, session, flash
from helpers import login_required
import os
import requests
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "myshelf_secret_2025"


def get_db_connection():
    conn = sqlite3.connect('myshelf.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        session.clear()
        username = request.form.get("username").strip()
        password = request.form.get("password")

        if not username or not password:
            flash("All fields are required", "danger")
            return redirect(url_for("login"))

        with get_db_connection() as conn:
            db = conn.cursor()
            db.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = db.fetchone()

        if row is None:
            flash("Invalid username", "danger")
            return redirect(url_for("login"))

        if not check_password_hash(row["hash"], password):
            flash("Invalid password", "danger")
            return redirect(url_for("login"))

        session["user_id"] = row["id"]

        flash("Logged in successfully!", "success")
        return redirect(url_for("index"))

    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        username = request.form.get("username").strip()
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or not password or not confirmation:
            flash("All fields are required", "danger")
            return redirect(url_for("register"))

        if password != confirmation:
            flash("Passwords must match", "danger")
            return redirect(url_for("register"))

        with get_db_connection() as conn:
            db = conn.cursor()
            db.execute("SELECT * FROM users WHERE username = ?", (username,))
            existing = db.fetchone()

            if existing:
                flash("Username already taken", "danger")
                return redirect(url_for("register"))

            hashed = generate_password_hash(password)
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hashed))
            conn.commit()

            user_id = db.lastrowid
            session["user_id"] = user_id

        flash("Registered successfully!", "success")
        return redirect(url_for("index"))

    else:
        return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/books", methods=["GET", "POST"])
def books():
    query = request.args.get("q", "")
    try:
        page = int(request.args.get("page", 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    max_results = 12
    start_index = (page - 1) * max_results

    books = []

    if query:
        api_url = "https://www.googleapis.com/books/v1/volumes"
        params = {
            "q": query,
            "startIndex": start_index,
            "maxResults": max_results
        }

        try:
            response = requests.get(api_url, params=params, timeout=5)
            response.raise_for_status()
        except requests.RequestException:
            flash("Could not fetch books. Please try again later.", "danger")
            return render_template("books.html", books=[], query=query, page=page)

        if response.status_code == 200:
            data = response.json()
            for item in data.get("items", []):
                volume_info = item.get("volumeInfo", {})
                books.append({
                    "title": volume_info.get("title", "No title"),
                    "author": ", ".join(volume_info.get("authors", [])),
                    "thumbnail": volume_info.get("imageLinks", {}).get("thumbnail", ""),
                    "google_id": item.get("id")
                })
        else:
            flash("Could not fetch books.", "danger")

    return render_template("books.html", books=books, query=query, page=page)


@app.route("/figures")
def figures():
    with get_db_connection() as conn:
        db = conn.cursor()
        db.execute("SELECT * FROM items WHERE category = 'figure' ORDER BY series")
        figures = db.fetchall()
    return render_template("figures.html", figures=figures)


@app.route("/funkos")
def funkos():
    with get_db_connection() as conn:
        db = conn.cursor()
        db.execute("SELECT * FROM items WHERE category = 'funko'")
        funkos = db.fetchall()
    return render_template("funkos.html", funkos=funkos)


@app.route("/profile", methods=["GET"])
@login_required
def profile():
    user_id = session["user_id"]

    sort = request.args.get("sort", "date_added")
    category_filter = request.args.get("category", "all")

    with get_db_connection() as conn:
        db = conn.cursor()

        query = """
                SELECT
                    item_id,
                    google_id,
                    COALESCE(items.category, collections.category) AS category,
                    title,
                    author,
                    COALESCE(items.image, '') as image,
                    items.series,
                    items.description,
                    COUNT(*) as quantity,
                    MIN(date_added) as date_added
                FROM collections
                LEFT JOIN items ON collections.item_id = items.id
                WHERE user_id = ?
                """

        params = [user_id]

        if category_filter != "all":
            query += " AND COALESCE(items.category, collections.category) = ?"
            params.append(category_filter)

        query += " GROUP BY item_id, google_id"

        if sort == "alpha":
            query += " ORDER BY title COLLATE NOCASE ASC"
        elif sort == "noalpha":
            query += " ORDER BY title COLLATE NOCASE DESC"
        elif sort == "date_added":
            query += " ORDER BY date_added DESC"
        elif sort == "oldest":
            query += " ORDER BY date_added ASC"
        elif sort == "category":
            query += " ORDER BY category COLLATE NOCASE ASC"
        elif sort == "series":
            query += " ORDER BY series COLLATE NOCASE ASC"
        else:
            query += " ORDER BY date_added DESC"

        db.execute(query, params)
        items = db.fetchall()

    return render_template("profile.html", items=items, sort=sort, category=category_filter)


@app.route("/add", methods=["POST"])
@login_required
def add_to_collection():
    user_id = session["user_id"]
    item_id = request.form.get("item_id")
    google_id = request.form.get("google_id")
    from_page = request.form.get("from_page")
    q = request.form.get("q", "")
    page = request.form.get("page", "")

    with get_db_connection() as conn:
        db = conn.cursor()

        if item_id:
            db.execute("SELECT * FROM items WHERE id = ?", (item_id,))
            item = db.fetchone()

            if item is None:
                flash("Item not found.", "danger")
                return redirect(url_for("index"))

            db.execute("""
                SELECT COUNT(*) FROM collections WHERE user_id = ? AND item_id = ?
            """, (user_id, item["id"]))
            exists = db.fetchone()[0]

            db.execute("""
                INSERT INTO collections (user_id, item_id, category, title, image, date_added)
                VALUES (?, ?, ?, ?, ?, datetime('now'))
            """, (user_id, item["id"], item["category"], item["name"], item["image"]))

            conn.commit()

            if exists > 0:
                flash("You already have this item — another one was added.", "warning")
            else:
                flash("Item added to your collection!", "success")

        elif google_id:
            title = request.form.get("title")
            author = request.form.get("author")
            image = request.form.get("image")

            if not title or not google_id:
                flash("Invalid book data.", "danger")
                return redirect(url_for("index"))

            db.execute("""
                SELECT COUNT(*) FROM collections WHERE user_id = ? AND google_id = ?
            """, (user_id, google_id))
            exists = db.fetchone()[0]

            db.execute("""
                INSERT INTO collections (user_id, category, title, author, image, google_id, date_added)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            """, (user_id, "book", title, author, image, google_id))

            conn.commit()

            if exists > 0:
                flash("You already have this book — another one was added.", "warning")
            else:
                flash("Book added to your collection!", "success")

        else:
            flash("No item specified.", "danger")
            return redirect(url_for("index"))


    if from_page == "books":
        return redirect(url_for("books", q=q, page=page))
    elif from_page:
        return redirect(url_for(from_page))
    else:
        return redirect(url_for("index"))


@app.route("/remove", methods=["POST"])
@login_required
def remove_from_collection():
    user_id = session["user_id"]
    item_id = request.form.get("item_id")
    google_id = request.form.get("google_id")

    with get_db_connection() as conn:
        db = conn.cursor()

        if item_id:
            db.execute("""
                DELETE FROM collections WHERE id = (
                    SELECT id FROM collections WHERE user_id = ? AND item_id = ? LIMIT 1
                )
            """, (user_id, item_id))
        elif google_id:
            db.execute("""
                DELETE FROM collections WHERE id = (
                    SELECT id FROM collections WHERE user_id = ? AND google_id = ? LIMIT 1
                )
            """, (user_id, google_id))

        conn.commit()

    flash("Item removed.", "success")
    return redirect(url_for("profile"))
