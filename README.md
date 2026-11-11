# Smart Finance

A beginner-friendly Flask and SQLite personal finance tracker.

## Features

- Record income and expenses.
- Calculate balance, income, and expenses from saved transactions.
- Store transactions in a local SQLite database.
- View the 20 most recent transactions.
- Validate transaction details on the server.

## Run locally

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 in your browser.

The `finance.db` database is created automatically when the app starts.
It is intentionally excluded from Git because it can contain private financial data.

## Important

This is a learning prototype, not production-ready financial software. Before public deployment,
add user authentication, CSRF protection, secure secret management, HTTPS, backups, and
production server configuration. Do not enter sensitive real banking credentials.
