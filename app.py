import sqlite3
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = "change-this-development-secret-before-deployment"

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "finance.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_table():
    with get_db_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                amount_kobo INTEGER NOT NULL CHECK (amount_kobo > 0),
                category TEXT NOT NULL,
                transaction_type TEXT NOT NULL
                    CHECK (transaction_type IN ('income', 'expense')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def naira_to_kobo(amount_text):
    """Validate a Naira amount and convert it to an integer number of kobo."""
    try:
        amount = Decimal(amount_text)
    except (InvalidOperation, TypeError):
        raise ValueError("Enter a valid amount.")

    if not amount.is_finite() or amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    amount = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return int(amount * 100)


def format_naira(amount_kobo):
    amount = Decimal(amount_kobo) / Decimal(100)
    return f"{amount:,.2f}"


@app.template_filter("naira")
def naira_filter(amount_kobo):
    return format_naira(amount_kobo)


@app.route("/")
def home():
    with get_db_connection() as connection:
        income = connection.execute("""
            SELECT COALESCE(SUM(amount_kobo), 0)
            FROM transactions
            WHERE transaction_type = 'income'
        """).fetchone()[0]

        expenses = connection.execute("""
            SELECT COALESCE(SUM(amount_kobo), 0)
            FROM transactions
            WHERE transaction_type = 'expense'
        """).fetchone()[0]

        transactions = connection.execute("""
            SELECT id, description, amount_kobo, category,
                   transaction_type, created_at
            FROM transactions
            ORDER BY created_at DESC, id DESC
            LIMIT 20
        """).fetchall()

    balance = income - expenses

    return render_template(
        "index.html",
        total_income=income,
        total_expenses=expenses,
        total_balance=balance,
        transactions=transactions,
    )


@app.route("/add-transaction", methods=["POST"])
def add_transaction():
    description = request.form.get("description", "").strip()
    category = request.form.get("category", "").strip()
    transaction_type = request.form.get("transaction_type", "").strip()
    amount_text = request.form.get("amount", "").strip()

    allowed_categories = {
        "Salary", "Business", "Food", "Transport",
        "Shopping", "Bills", "Education", "Health", "Other"
    }

    if not description or len(description) > 100:
        flash("Enter a description of 1 to 100 characters.", "error")
        return redirect(url_for("home"))

    if category not in allowed_categories:
        flash("Choose a valid category.", "error")
        return redirect(url_for("home"))

    if transaction_type not in {"income", "expense"}:
        flash("Choose Income or Expense.", "error")
        return redirect(url_for("home"))

    try:
        amount_kobo = naira_to_kobo(amount_text)
    except ValueError as error:
        flash(str(error), "error")
        return redirect(url_for("home"))

    with get_db_connection() as connection:
        connection.execute("""
            INSERT INTO transactions
                (description, amount_kobo, category, transaction_type)
            VALUES (?, ?, ?, ?)
        """, (description, amount_kobo, category, transaction_type))

    flash("Transaction added successfully.", "success")
    return redirect(url_for("home"))


if __name__ == "__main__":
    create_table()
    app.run(debug=True)
