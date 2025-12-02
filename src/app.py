#!/usr/bin/env python3
from flask import Flask, request, render_template_string
from flask_sqlalchemy import SQLAlchemy
import requests
from datetime import datetime

app = Flask(__name__)

# -----------------------------
# DATABASE SETUP
# -----------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transactions.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Transaction(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount      = db.Column(db.Float, nullable=False)
    currency    = db.Column(db.String(10), nullable=False)
    usd_rate    = db.Column(db.Float, nullable=False)
    usd_amount  = db.Column(db.Float, nullable=False)
    account     = db.Column(db.String(100), nullable=False)
    timestamp   = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()


# -----------------------------
# CURRENCY RATE FETCHER (NO API KEY NEEDED)
# -----------------------------
def fetch_usd_rate(currency_code):
    """
    Fetch currency → USD rate from open.er-api.com
    Returns 1.0 for USD or if request fails.
    """
    if currency_code == "USD":
        return 1.0

    url = f"https://open.er-api.com/v6/latest/{currency_code}"

    try:
        r = requests.get(url, timeout=4)
        data = r.json()

        # Validate API success
        if data.get("result") != "success":
            return 1.0

        rates = data.get("rates", {})
        usd_rate = rates.get("USD")

        if usd_rate:
            return float(usd_rate)

    except Exception as e:
        print("Exchange rate fetch failed:", e)

    return 1.0  # fallback


# -----------------------------
# ROUTE: FORM PAGE
# -----------------------------
@app.route("/", methods=["GET"])
def form():
    return render_template_string("""
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <title>Record a Transaction</title>
            <style>
                body {font-family: Arial, sans-serif; margin: 2rem;}
                label {display: block; margin-top: 0.75rem;}
                input, select {width: 300px; padding: 0.4rem;}
            </style>
        </head>
        <body>
            <h2>Record a Transaction</h2>
            <form action="/echo_user_input" method="POST">
                <label>Description:
                    <input type="text" name="description" required>
                </label>

                <label>Amount:
                    <input type="number" name="amount" step="0.01" required>
                </label>

                <label>Currency:
                    <select name="currency" required>
                        <option value="USD">USD – US Dollar</option>
                        <option value="EUR">EUR – Euro</option>
                        <option value="GBP">GBP – British Pound</option>
                        <option value="JPY">JPY – Japanese Yen</option>
                        <option value="AUD">AUD – Australian Dollar</option>
                        <option value="CAD">CAD – Canadian Dollar</option>
                    </select>
                </label>

                <label>Account / Card #:
                    <input type="text" name="account" required>
                </label>

                <input type="submit" value="Submit!">
            </form>
        </body>
        </html>
    """)


# -----------------------------
# ROUTE: PROCESS FORM SUBMISSION
# -----------------------------
@app.route("/echo_user_input", methods=["POST"])
def echo_input():
    description = request.form.get("description", "")
    amount      = float(request.form.get("amount", "0"))
    currency    = request.form.get("currency", "")
    account     = request.form.get("account", "")

    # Convert currency → USD
    usd_rate   = fetch_usd_rate(currency)
    usd_amount = amount * usd_rate

    # Save transaction in database
    entry = Transaction(
        description=description,
        amount=amount,
        currency=currency,
        usd_rate=usd_rate,
        usd_amount=usd_amount,
        account=account,
    )
    db.session.add(entry)
    db.session.commit()

    # Calculate total USD across all transactions
    total_usd = db.session.query(db.func.sum(Transaction.usd_amount)).scalar() or 0

    return render_template_string("""
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <title>Transaction Recorded</title>
            <style>
                body {font-family: Arial, sans-serif; margin: 2rem;}
                .echo {padding: 1rem; background:#e0f7fa; border:1px solid #006064;}
                .summary {margin-top:1rem; padding:1rem; background:#fff3cd; border:1px solid #856404;}
            </style>
        </head>
        <body>
            <h2>Transaction Recorded</h2>
            <div class="echo">
                <strong>Description:</strong> {{ description }}<br>
                <strong>Amount:</strong> {{ amount }} {{ currency }}<br>
                <strong>USD Conversion Rate:</strong> {{ usd_rate }}<br>
                <strong>Value in USD:</strong> {{ usd_amount }} USD<br>
                <strong>Account / Card #:</strong> {{ account }}<br>
            </div>

            <div class="summary">
                <strong>Total USD expense so far:</strong> {{ total_usd }} USD
            </div>

            <a href="/">Record another transaction</a>
        </body>
        </html>
    """,
    description=description,
    amount=amount,
    currency=currency,
    usd_rate=round(usd_rate, 6),
    usd_amount=round(usd_amount, 2),
    account=account,
    total_usd=round(total_usd, 2)
    )


# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
