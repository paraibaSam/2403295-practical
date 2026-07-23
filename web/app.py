from flask import Flask, render_template, request, Response
import psycopg2
import re
import os
import time
from datetime import datetime
from functools import wraps

app = Flask(__name__)

MIN_LENGTH = 1
MAX_LENGTH = 100

DB_HOST = os.environ.get("DB_HOST", "db")
DB_NAME = os.environ.get("DB_NAME", "searchdb")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")
ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
if not ADMIN_PASSWORD:
    raise RuntimeError("ADMIN_PASSWORD environment variable must be set")

# OWASP C3 LF#5: allow-list rather than deny-list
ALLOWED_PATTERN = re.compile(r'^[a-zA-Z0-9 ]*$')

def check_auth(username, password):
    return username == ADMIN_USER and password == ADMIN_PASSWORD

def authenticate():
    return Response(
        "Login required", 401, {"WWW-Authenticate": 'Basic realm="Restricted"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def is_attack(search_term):
    """Backend validation - OWASP C3: allow-list of characters."""
    if len(search_term) < MIN_LENGTH or len(search_term) > MAX_LENGTH:
        return True
    return not bool(ALLOWED_PATTERN.match(search_term))

def get_connection():
    retries = 10
    while retries > 0:
        try:
            return psycopg2.connect(
                host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
            )
        except psycopg2.OperationalError:
            retries -= 1
            print(f"Database not ready, retrying... ({retries} left)")
            time.sleep(3)
    raise Exception("Could not connect to database after multiple retries")

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS "2403295" (id SERIAL PRIMARY KEY, query TEXT, query_time TIMESTAMP)')
    conn.commit()
    cur.close()
    conn.close()

def log_search(term):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO "2403295" (query, query_time) VALUES (%s, %s)', (term, datetime.now()))
    conn.commit()
    cur.close()
    conn.close()

@app.route("/", methods=["GET", "POST"])
@requires_auth
def home():
    if request.method == "POST":
        term = request.form.get("search_term", "")
        log_search(term)
        if is_attack(term):
            return render_template("index.html", error="Invalid input detected.")
        return render_template("result.html", term=term)
    return render_template("index.html", error=None)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=443, ssl_context=("certs/server.crt", "certs/server.key"))