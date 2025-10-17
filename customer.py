import requests
import csv
import threading
import time
from flask import Flask, render_template_string, request, redirect, url_for, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow requests from anywhere (for dev; restrict in prod if desired)

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR1l2CD7aX4_5qHwkQRRHD3ntTyOTOSfB-1jAsBP9J_TdSkyQGdc8qCjO1-GOgXysUdvkG6HQ4LuCov/pub?gid=0&single=true&output=csv"

fraud_list = []
phone_entries = {}    # phone -> [list of entries]
customer_id_to_phone = {}  # customer_id -> phone
data_lock = threading.Lock()

def normalize_phone(phone):
    phone = str(phone).strip()
    if phone.startswith('0') and len(phone) == 11:
        return phone[1:]
    return phone

def parse_customer_ids(cell):
    cell = cell.strip().strip("[]").replace('\n', ' ').replace(',', ' ')
    return [cid for cid in cell.split() if cid]

def fetch_and_parse_csv():
    response = requests.get(CSV_URL)
    response.raise_for_status()
    lines = response.content.decode('utf-8').splitlines()
    reader = csv.DictReader(lines)
    temp_fraud_list = []
    temp_phone_entries = {}
    temp_customer_id_to_phone = {}
    for row in reader:
        phone = row['Phone'].strip()
        ids = parse_customer_ids(row['customer_ids'])
        entry = {
            "phone": phone,
            "state": row['State'].strip(),
            "city": row['City'].strip(),
            "zone": row['Zone'].strip(),
            "distinct_customers": row['distinct_customers'].strip(),
            "customer_ids": ids
        }
        temp_fraud_list.append(entry)
        temp_phone_entries.setdefault(phone, []).append(entry)
        for cid in ids:
            temp_customer_id_to_phone[cid] = phone
    with data_lock:
        fraud_list.clear()
        fraud_list.extend(temp_fraud_list)
        phone_entries.clear()
        phone_entries.update(temp_phone_entries)
        customer_id_to_phone.clear()
        customer_id_to_phone.update(temp_customer_id_to_phone)

def sync_csv_background():
    while True:
        try:
            fetch_and_parse_csv()
            print("CSV refreshed.")
        except Exception as e:
            print(f"CSV fetch error: {e}")
        time.sleep(600)

sync_thread = threading.Thread(target=sync_csv_background, daemon=True)
sync_thread.start()

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Fraud Customer Checker</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
    <style>
        html, body { height: 100%; min-height: 100vh; }
        body {
            font-family: 'Inter', Arial, sans-serif;
            margin: 0;
            color: #212325;
            background: linear-gradient(135deg, #e0ecff 0%, #eafffa 100%);
            position: relative;
            overflow-x: hidden;
        }
        body::before {
            content: "";
            position: fixed;
            inset: 0;
            z-index: 0;
            pointer-events: none;
            background:
                radial-gradient(circle at 20% 30%, rgba(120,170,255,0.08) 0%, rgba(255,255,255,0) 60%),
                radial-gradient(circle at 80% 70%, rgba(120,190,220,0.08) 0%, rgba(255,255,255,0) 60%),
                radial-gradient(circle at 50% 90%, rgba(170,200,255,0.06) 0%, rgba(255,255,255,0) 60%);
        }
        .main { display: flex; flex-direction: column; align-items: center; min-height: 100vh; }
        .glass-dashboard {
            margin-top: 36px;
            width: 98vw;
            max-width: 1200px;
            border-radius: 22px;
            padding: 38px 32px 38px 32px;
            box-shadow: 0 8px 48px rgba(60, 80, 180, 0.07);
            background: linear-gradient(135deg, rgba(255,255,255,0.9) 40%, rgba(220,235,255,0.8) 100%);
            backdrop-filter: blur(14px);
            border: 1.5px solid rgba(180,200,255,0.27);
            position: relative;
            z-index: 1;
            text-align: center;
        }
        .title {
            font-size: 2.6em;
            font-weight: 700;
            margin-bottom: 22px;
            color: #1e2f4d;
            letter-spacing: -1px;
            text-align: center;
        }
        .search-bar-wrap { display: flex; flex-direction: column; align-items: center; margin-bottom: 14px; }
        .search-form {
            display: flex; gap: 8px; width: 600px; margin-bottom: 0; justify-content: center;
        }
        input[type="text"] {
            flex: 1 1 auto;
            font-size: 1.18em;
            padding: 15px 18px;
            border-radius: 9px;
            border: 1.5px solid #d9dfe6;
            background: rgba(255,255,255,0.7);
            transition: border 0.2s;
            box-shadow: 0 2px 12px #e2eafc55;
        }
        input[type="text"]:focus {
            border: 1.7px solid #2563eb;
            outline: none;
        }
        button {
            font-size: 1.13em;
            padding: 0 38px;
            background: linear-gradient(90deg,#2563eb 70%,#4bbfda 100%);
            color: #fff;
            font-family: 'Inter', Arial, sans-serif;
            border: none;
            border-radius: 9px;
            cursor: pointer;
            font-weight: 700;
            box-shadow: 0 2px 8px #2563eb44;
            transition: background 0.2s;
        }
        button:hover { background: linear-gradient(90deg,#4bbfda 10%,#2563eb 90%);}
        .search-input-value {
            margin-top: 10px;
            font-size: 1.18em;
            color: #2563eb;
            font-weight: 700;
            background: rgba(220,235,255,0.5);
            border-radius: 8px;
            padding: 5px 20px;
            display: inline-block;
            box-shadow: 0 1px 6px #c8eaff33;
            margin-bottom: 0px;
            text-align: center;
        }
        .status-bar {
            margin: 26px auto 0 auto;
            font-size: 1.18em;
            font-weight: 700;
            text-align: center;
            padding: 13px 0;
            border-radius: 12px;
            max-width: 600px;
            border: 2px solid #e2eaf6;
            box-shadow: 0 2px 12px #e2eafc33;
        }
        .fraud-status {
            background: linear-gradient(90deg,#ffe5e5 70%,#ffbcbc 100%);
            color: #c20000;
            border: 2px solid #ff6c6c;
        }
        .genuine-status {
            background: linear-gradient(90deg,#e5ffe8 70%,#baffcd 100%);
            color: #008c3a;
            border: 2px solid #6cff8c;
        }
        .results-table-wrap {
            width: 100%;
            margin: 30px 0 0 0;
            display: flex;
            justify-content: center;
        }
        table.results-table {
            width: 98%;
            margin: 0 auto;
            background: rgba(255,255,255,0.72);
            border-radius: 18px;
            box-shadow: 0 2px 16px rgba(56, 65, 82, 0.10);
            border-collapse: separate;
            border-spacing: 0;
            overflow: hidden;
            text-align: center;
        }
        table.results-table th, table.results-table td {
            padding: 18px 16px;
            text-align: center;
            vertical-align: top;
        }
        table.results-table th {
            font-size: 1.17em;
            font-weight: 700;
            color: #1e2f4d;
            border-bottom: 2px solid #e2eaf6;
            background: rgba(240,250,255,0.7);
        }
        table.results-table tr {
            background: rgba(240,250,255,0.82);
        }
        table.results-table tr.even {
            background: rgba(220,235,255,0.75);
        }
        table.results-table td {
            background: inherit;
            font-size: 1.12em;
            border-bottom: 1px solid #e2eaf6;
            text-align: center;
        }
        table.results-table td:not(:last-child) {
            border-right: 1.2px solid #e2eaf6;
        }
        .loc-num { font-weight: 700; color: #2563eb; margin-right: 7px; }
        .loc-data { font-size: 1.11em; color: #2b3245; }
        .custid-val { font-size: 1.23em; color: #1a2c42; font-weight: 700; padding-left: 0px; }
        .idlist-row {
            display: flex;
            flex-wrap: wrap;
            gap: 9px;
            justify-content: center;
            align-items: flex-start;
        }
        .customer-id {
            background: linear-gradient(135deg,#e8f1ff 60%, #d7f8ff 100%);
            color: #233a53;
            border-radius: 10px;
            padding: 7px 14px;
            font-size: 1.07em;
            border: 1px solid #d9dfe6;
            font-weight: 500;
            margin-bottom: 4px;
            box-shadow: 0 1px 6px #e2eafc33;
        }
        @media (max-width: 1100px) {
            .glass-dashboard { max-width: 99vw; padding: 12px 5vw; }
            .search-form { width: 99vw; }
            table.results-table th, table.results-table td { padding: 10px 6px;}
        }
        @media (max-width: 700px) {
            .glass-dashboard { max-width: 99vw; padding: 8px 1vw;}
            .title { font-size: 1.12em;}
            .search-form { width: 97vw; }
            table.results-table th, table.results-table td { padding: 7px 3px;}
        }
    </style>
</head>
<body>
    <div class="main">
        <div class="glass-dashboard">
            <div class="title">Fraud Customer Checker</div>
            <div class="search-bar-wrap">
                <form method="post" class="search-form" autocomplete="off" action="/search">
                    <input type="text" name="query" id="query" placeholder="Phone Number or Customer ID" required value="{{ search_value|default('') }}">
                    <button type="submit">Search</button>
                </form>
                {% if search_value %}
                    <div class="search-input-value">{{ search_value }}</div>
                {% endif %}
            </div>
            {% if result %}
                <div class="status-bar {% if result.status == 'fraud' %}fraud-status{% else %}genuine-status{% endif %}">
                    {% if result.status == 'fraud' %}
                        Status: Fraud Customer
                    {% else %}
                        Status: Genuine Customer Not A Fraud
                    {% endif %}
                </div>
            {% endif %}
            {% if result and result.locations and result.status == 'fraud' %}
            <div class="results-table-wrap">
                <table class="results-table">
                    <thead>
                        <tr>
                            <th style="width:30%; text-align:center;">Location</th>
                            <th style="width:14%; text-align:center;">Distinct Customer ID</th>
                            <th style="text-align:center;">Customer ID List</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for loc in result.locations %}
                        <tr class="{% if loop.index % 2 == 0 %}even{% endif %}">
                            <td>
                                <span class="loc-num">{{ loop.index }}.</span>
                                <span class="loc-data">{{ loc.state }}, {{ loc.city }}, {{ loc.zone }}</span>
                            </td>
                            <td>
                                <span class="custid-val">{{ loc.distinct_customers }}</span>
                            </td>
                            <td>
                                <div class="idlist-row">
                                    {% for cid in loc.customer_ids %}
                                    <span class="customer-id">{{ cid }}</span>
                                    {% endfor %}
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(TEMPLATE, result=None)

def get_query_result(query):
    display_phone = query
    phone = None
    norm_query = normalize_phone(query)
    with data_lock:
        if norm_query in phone_entries:
            phone = norm_query
        elif query in customer_id_to_phone:
            phone = customer_id_to_phone[query]
        if phone and phone in phone_entries:
            entries = phone_entries[phone]
            locations = []
            for entry in entries:
                locations.append({
                    "state": entry["state"],
                    "city": entry["city"],
                    "zone": entry["zone"],
                    "distinct_customers": entry["distinct_customers"],
                    "customer_ids": entry["customer_ids"],
                })
            search_display = display_phone
            if len(phone) == 10:
                search_display = '0' + phone
            result = {
                "status": "fraud",
                "phone": search_display,
                "locations": locations,
            }
        else:
            search_display = display_phone
            if len(query) == 10:
                search_display = '0' + query
            result = {
                "status": "notfraud",
                "phone": search_display,
                "locations": [],
            }
    return result, search_display

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "GET":
        return redirect(url_for("index"))
    query = request.form["query"].strip()
    result, search_display = get_query_result(query)
    return render_template_string(TEMPLATE, result=result, search_value=search_display)

# Added: JSON API endpoint for future/faster Chrome extension integration
@app.route("/api/search", methods=["POST"])
def api_search():
    query = request.form.get("query", "").strip()
    result, search_display = get_query_result(query)
    # Add search_value to result for convenience
    result['search_value'] = search_display
    return jsonify(result)

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if __name__ == "__main__":
    fetch_and_parse_csv()
    app.run(debug=True)