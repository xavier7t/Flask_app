#!/usr/bin/env python3

from flask import Flask, request

app = Flask(__name__)

# landing page – a form with a <select> (drop‑down) widget
@app.route("/")
def main():
    return '''
        <h2>Select a Currency</h2>
        <form action="/echo_user_input" method="POST">
            <!-- Drop-down menu -->
            <select name="currency">
                <option value="USD">USD - US Dollar</option>
                <option value="EUR">EUR - Euro</option>
                <option value="GBP">GBP - British Pound</option>
                <option value="JPY">JPY - Japanese Yen</option>
                <option value="AUD">AUD - Australian Dollar</option>
            </select>

            <input type="submit" value="Submit!">
        </form>
    '''

# Handle the POST – echo the selected currency code
@app.route("/echo_user_input", methods=["POST"])
def echo_input():
    # Grab the value that the user selected
    selected_currency = request.form.get("currency", "")
    return f"You selected: {selected_currency}"