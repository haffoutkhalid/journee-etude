from flask import (
    Flask, render_template, request, jsonify,
    session, redirect, url_for, Response,
)
from datetime import datetime, timezone, timedelta
from functools import wraps
from urllib.parse import quote
from filelock import FileLock
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash
import csv
import io
import os
import re

app = Flask(__name__)

# ---------------------------------------------------------------------------
# 🔒 الإعدادات الحساسة (قيم افتراضية مدمجة لتعمل على Render مباشرة)
# ---------------------------------------------------------------------------
app.secret_key = os.environ.get("SECRET_KEY", "Riyada2026@SecretKey123")

# كلمة السر الافتراضية هي: Chadhili2026
ADMIN_PASSWORD_HASH = os.environ.get(
    "ADMIN_PASSWORD_HASH",
    "pbkdf2:sha256:600000$X8bN9sK1w2L5p4Q3$3a6e8d2f4c1b9a7e5d3f1c8b6a4e2d0f9c7b5a3e1d8f6c4b2a0e9d7f5c3b1a"
)

# 🔒 كوكي الجلسة محصّن + مدة صلاحية محدودة
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=os.environ.get("FLASK_ENV") == "production",
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=timedelta(hours=2),
    WTF_CSRF_TIME_LIMIT=None,
)

csrf = CSRFProtect(app)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["120/minute"],
    storage_uri="memory://",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "inscriptions.csv")
DATA_LOCK = FileLock(DATA_FILE + ".lock", timeout=10)

CSV_HEADERS = [
    "التاريخ والوقت", "الاسم الكامل", "المؤسسة/الوظيفة",
    "البريد الإلكتروني", "الهاتف", "الإطار",
]

MAX_LEN = {"full_name": 120, "institution": 160, "email": 254, "phone": 30}
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^[0-9+\-\s()]{6,20}$")


# ---------------------------------------------------------------------------
# 🔒 أدوات مساعدة
# ---------------------------------------------------------------------------
def sanitize_cell(value) -> str:
    if value is None:
        return ""
    v = str(value).replace("\r", " ").replace("\n", " ").replace("\t", " ").strip()
    if v and v[0] in ("=", "+", "-", "@"):
        v = "'" + v
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
        if not os.path.isfile(DATA_FILE):
            return []
        with open(DATA_FILE, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.reader(f))
    return rows[1:] if rows else []


# ---------------------------------------------------------------------------
# محتوى الصفحة
# ---------------------------------------------------------------------------
EVENT_DATE_ISO = "2026-11-07T09:00:00"
EVENT_LOCATION = "المدرسة الجماعاتية أبي الحسن الشاذلي — العالم القروي"
EVENT_DIRECTORATE = "المديرية الإقليمية الفنيدق المضيق"
PROPOSALS_DEADLINE = "30 أكتوبر 2026"
CONTACT_PHONE = "0694896173"

WORKSHOPS = [
    "أستاذ التعليم الإبتدائي",
    "متصرف تربوي",
    "مفتش تربوي",
]
WORKSHOPS_NORMALIZED = {w.strip() for w in WORKSHOPS}

def validate_registration(full_name, institution, email, phone, workshop):
    if not full_name:
        return "الرجاء إدخال الاسم الكامل."
    if not email:
        return "الرجاء إدخال البريد الإلكتروني."
    if len(full_name) > MAX_LEN["full_name"]:
        return "الاسم الكامل طويل جدًا."
    if len(institution) > MAX_LEN["institution"]:
        return "اسم المؤسسة طويل جدًا."
    if len(email) > MAX_LEN["email"]:
        return "البريد الإلكتروني طويل جدًا."
    if len(phone) > MAX_LEN["phone"]:
        return "رقم الهاتف طويل جدًا."
    if not EMAIL_RE.match(email):
        return "صيغة البريد الإلكتروني غير صحيحة."
    if phone and not PHONE_RE.match(phone):
        return "صيغة رقم الهاتف غير صحيحة."
    if workshop and workshop.strip() not in WORKSHOPS_NORMALIZED:
        return "الإطار المختار غير صحيح."
    return None


PROGRAM = [
    {"time": "08:30 – 08:50", "title": "الاستقبال والتسجيل",
     "desc": "استقبال المشاركين ........"},
    {"time": "08:50 – 09:10", "title": "الافتتاح الرسمي",
     "desc": "كلمة إدارة المدرسة الجماعاتية أبي الحسن الشاذلي ."},
    {"time": "09:10 – 09:40", "title": "الإطار العام لمرحلة الدعم المكثف",
     "desc": "عرض تأطيري للسيد المفتش التربوي أحمد دعلي: الدعم  المكثف، الروائز التشخيصية والبعدية، أهداف مدارس الريادة."},
    {"time": "09:40 – 10:25", "title": "تجربة أبي الحسن الشاذلي: سنتان من الممارسة",
     "desc": "عرض محوري للطاقم التربوي: السياق المجالي، التشخيص الموضعي، تجميع المتعلمين حسب المستوى، ونتائج الروائز."},
    {"time": "10:25 – 10:45", "title": "استراحة ونقاش",
     "desc": "استراحة شاي وتبادل حر حول العرض المحوري."},
    {"time": "10:45 – 12:15", "title": "ورشات عمل موازية",
     "desc": ".............................. ."},
    {"time": "12:15 – 12:45", "title": "التركيب والتوصيات",
     "desc": "عرض خلاصات الورشات وصياغةتوصيات، بتنسيق الأستاذة لبنى الدراوي."},
    {"time": "12:45 – 13:00", "title": "التقييم والختام",
     "desc": "تقييم اليوم الدراسي وكلمة ختامية."},
]

GALLERY = [
    {"file": "training3.jpg", "caption": "ورشة تذكيرية لأساتذة مؤسسات الريادة حول برنامج دعم التعلمات الأساس"},
    {"file": "training1.jpg", "caption": "تكوين حول الدعم المكثف من تنظيم مديرية المضيق-الفنيدق"},
    {"file": "classroom_practice.jpg", "caption": "الممارسة الصفية خلال حصص الدعم"},
    {"file": "gallery_visit.jpg", "caption": "مواكبة ميدانية لتجديد الممارسات الصفية"},
]

SPEAKERS = [
    {"initial": "أ", "photo": "speaker_daali.jpg",
     "name": "السيد أحمد دعلي",
     "role": "مفتش تربوي — تأطير اليوم الدراسي",
     "bio": "يؤطر اليوم الدراسي ويقدم الإطار العام لمرحلة الدعم المكثف بمؤسسات الريادة، من التشخيص الموضعي إلى بناء خطط الدعم."},
    {"initial": "ل", "photo": "speaker_draoui.jpg",
     "name": "الأستاذة لبنى الدراوي",
     "role": "تنسيق اليوم الدراسي",
     "bio": "تتولى تنسيق فقرات اليوم الدراسي وتسيير النقاش حول تجربة المدرسة الجماعاتية أبي الحسن الشاذلي."},
    {"initial": "م", "photo": None,
     "name": "المتدخلون",
     "role": "حوض الفنيدق",
     "bio": "تقديم  مداخلات تتعلق بمرحلة  الدعم المكثف."},
]


# ---------------------------------------------------------------------------
# المسارات
# ---------------------------------------------------------------------------
@app.after_request
def security_headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "same-origin"
    resp.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "img-src 'self' data:; "
        "style-src 'self' 'unsafe-inline'; "
        "script-src 'self'; "
        "form-action 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'"
    )
    return resp


@app.route("/")
def index():
    return render_template(
        "index.html",
        event_date_iso=EVENT_DATE_ISO,
        event_location=EVENT_LOCATION,
        event_directorate=EVENT_DIRECTORATE,
        proposals_deadline=PROPOSALS_DEADLINE,
        contact_phone=CONTACT_PHONE,
        program=PROGRAM,
        speakers=SPEAKERS,
        workshops=WORKSHOPS,
        gallery=GALLERY,
    )


@app.route("/register", methods=["POST"])
@limiter.limit("5/minute")
@csrf.exempt
def register():
    data = request.get_json(silent=True)
    if data is None:
        data = request.form

    full_name = (data.get("full_name") or "").strip()
    institution = (data.get("institution") or "").strip()
    email = (data.get("email") or "").strip()
    phone = (data.get("phone") or "").strip()
    workshop = (data.get("workshop") or "").strip()

    err = validate_registration(full_name, institution, email, phone, workshop)
    if err:
        return jsonify({"ok": False, "error": err}), 400

    row = [
        datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        full_name, institution, email, phone, workshop,
    ]
    row = [sanitize_cell(c) for c in row]

    with DATA_LOCK:
        file_exists = os.path.isfile(DATA_FILE)
        with open(DATA_FILE, "a", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(CSV_HEADERS)
            writer.writerow(row)

    return jsonify({
        "ok": True,
        "message": "تم تسجيل مشاركتك بنجاح في اليوم الدراسي. نراكم بالموعد!",
    })


@app.route("/admin/login", methods=["GET", "POST"])
@limiter.limit("5/minute", methods=["POST"])
def admin_login():
    error = None
    if request.method == "POST":
        password = request.form.get("password", "")
        if check_password_hash(ADMIN_PASSWORD_HASH, password):
            session.permanent = True
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
    workshop_counts = {}
    for row in rows:
        if len(row) >= 6:
            key = row[5] or "(غير محدد)"
            workshop_counts[key] = workshop_counts.get(key, 0) + 1
    return render_template(
        "admin.html",
        headers=CSV_HEADERS,
        rows=rows,
        total=len(rows),
        workshop_counts=workshop_counts,
    )


@app.route("/admin/export")
@login_required
def admin_export():
    rows = read_registrations()

    buf = io.StringIO()
    buf.write("\ufeff")
    writer = csv.writer(buf)
    writer.writerow(CSV_HEADERS)
    for row in rows:
        writer.writerow([sanitize_cell(c) for c in row])

    ascii_name = "attendance.csv"
    utf8_name = quote("لائحة_الحضور.csv")
    return Response(
        buf.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={
            "Content-Disposition":
                f"attachment; filename={ascii_name}; filename*=UTF-8''{utf8_name}",
        },
    )


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
