from flask import Flask, render_template, request, jsonify, session, redirect, url_for, Response
from datetime import datetime, timezone, timedelta
from functools import wraps
from urllib.parse import quote
from filelock import FileLock
import csv
import io
import os
import re

app = Flask(__name__)
app.secret_key = "Riyada2026@SecretKey123"

# إعدادات الجلسة
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=False,  # مهم: جعلناها False لأننا قد نكون في بيئة اختبار
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=timedelta(hours=2),
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "inscriptions.csv")
DATA_LOCK = FileLock("/tmp/inscriptions.lock", timeout=10)

CSV_HEADERS = ["التاريخ والوقت", "الاسم الكامل", "المؤسسة/الوظيفة", "البريد الإلكتروني", "الهاتف", "الإطار"]


def sanitize_cell(value) -> str:
    if value is None: return ""
    v = str(value).replace("\r", " ").replace("\n", " ").replace("\t", " ").strip()
    if v and v[0] in ("=", "+", "-", "@"): v = "'" + v
    return v


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)

    return wrapped


def read_registrations():
    with DATA_LOCK:
        if not os.path.isfile(DATA_FILE): return []
        with open(DATA_FILE, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.reader(f))
    return rows[1:] if rows else []


@app.route("/")
def index():
    return render_template("index.html", event_date_iso="2026-11-07T09:00:00", event_location="المدرسة", program=[],
                           speakers=[], workshops=[], gallery=[])


@app.route("/register", methods=["POST"])
def register():
    return jsonify({"ok": True, "message": "تم التسجيل"})


# --- صفحة الدخول ---
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        password = request.form.get("password", "")

        if password == "Chadhili2026":
            session["is_admin"] = True
            return redirect(url_for("admin_dashboard"))

        error = "كلمة السر غير صحيحة."
    return render_template("admin_login.html", error=error)


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("admin_login"))


@app.route("/admin")
@login_required
def admin_dashboard():
    rows = read_registrations()
    return render_template("admin.html", headers=CSV_HEADERS, rows=rows, total=len(rows), workshop_counts={})


if __name__ == "__main__":
    app.run(debug=True)