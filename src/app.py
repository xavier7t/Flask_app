#!/usr/bin/env python3
#  Transaction Recorder – Echo back the entered values
from flask import Flask, request, render_template_string

app = Flask(__name__)

# GET /  – Show the form
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
                .echo {margin-top: 1.5rem; padding: 1rem; background:#f9f9f9; border:1px solid #ddd;}
            </style>
        </head>
        <body>
            <h2>Record a Transaction</h2>
            <form action="/echo_user_input" method="POST">
                <label>
                    Description:
                    <input type="text" name="description" required>
                </label>

                <label>
                    Amount:
                    <input type="number" name="amount" step="0.01" required>
                </label>

                <label>
                    Currency:
                    <select name="currency" required>
                        <option value="USD">USD – US Dollar</option>
                        <option value="EUR">EUR – Euro</option>
                        <option value="GBP">GBP – British Pound</option>
                        <option value="JPY">JPY – Japanese Yen</option>
                        <option value="AUD">AUD – Australian Dollar</option>
                        <option value="CAD">CAD – Canadian Dollar</option>
                    </select>
                </label>

                <label>
                    Account / Card #:
                    <input type="text" name="account" required>
                </label>

                <input type="submit" value="Submit!">
            </form>
        </body>
        </html>
    """)
# POST /echo_user_input – Echo back the posted data
@app.route("/echo_user_input", methods=["POST"])
def echo_input():
    # Grab everything the user entered
    description = request.form.get("description", "")
    amount      = request.form.get("amount", "")
    currency    = request.form.get("currency", "")
    account     = request.form.get("account", "")

    # Render a very small response page that simply repeats what was sent
    return render_template_string("""
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <title>Transaction Recorded</title>
            <style>
                body {font-family: Arial, sans-serif; margin: 2rem;}
                .echo {padding: 1rem; background:#e0f7fa; border:1px solid #006064;}
                a {display: inline-block; margin-top: 1rem;}
            </style>
        </head>
        <body>
            <h2>Transaction Recorded</h2>
            <div class="echo">
                <strong>Description:</strong> {{ description }}<br>
                <strong>Amount:</strong> {{ amount }}<br>
                <strong>Currency:</strong> {{ currency }}<br>
                <strong>Account / Card #:</strong> {{ account }}
            </div>
            <a href="/">Record another transaction</a>
        </body>
        </html>
    """, description=description, amount=amount, currency=currency, account=account)