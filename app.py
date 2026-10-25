from flask import (
    Flask, render_template, request, jsonify,
    session, redirect, url_for, Response,
)
from datetime import datetime
from functools import wraps
import csv
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "Riyada2026@chadhili@ecole")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "inscriptions.csv")

# كلمة سر فضاء الإدارة — يفضّل ضبطها عبر متغير بيئة قبل النشر الفعلي
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Chadhili2026")

CSV_HEADERS = [
    "التاريخ والوقت", "الاسم الكامل", "المؤسسة/الوظيفة",
    "البريد الإلكتروني", "الهاتف", "الورشة المختارة",
]


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)
    return wrapped


def read_registrations():
    if not os.path.isfile(DATA_FILE):
        return []
    with open(DATA_FILE, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        rows = list(reader)
    return rows[1:] if rows else []  # تجاوز سطر العناوين

# ---------------------------------------------------------------------------
# محتوى الصفحة (عدّل هذه القيم بما يناسب التاريخ والمتدخلين الفعليين)
# ---------------------------------------------------------------------------

EVENT_DATE_ISO = "2026-11-07T09:00:00"   # السبت 07 نونبر 2026
EVENT_LOCATION = "المدرسة الجماعاتية أبي الحسن الشاذلي — العالم القروي"
EVENT_DIRECTORATE = "المديرية الإقليمية الفنيدق المضيق"
PROPOSALS_DEADLINE = "30 أكتوبر 2026"
CONTACT_PHONE = "0694896173"

WORKSHOPS = [
    "أستاذ التعليم الإبتدائي ",
    "متصرف تربوي",
    "مفتش تربوي",
]

PROGRAM = [
    {
        "time": "08:30 – 08:50",
        "title": "الاستقبال والتسجيل",
        "desc": "استقبال المشاركين ........",
    },
    {
        "time": "08:50 – 09:10",
        "title": "الافتتاح الرسمي",
        "desc": "كلمة إدارة المدرسة الجماعاتية أبي الحسن الشاذلي .",
    },
    {
        "time": "09:10 – 09:40",
        "title": "الإطار العام لمرحلة الدعم المكثف",
        "desc": "عرض تأطيري للسيد المفتش التربوي أحمد دعلي: الدعم  المكثف، الروائز التشخيصية والبعدية، أهداف مدارس الريادة.",
    },
    {
        "time": "09:40 – 10:25",
        "title": "تجربة أبي الحسن الشاذلي: سنتان من الممارسة",
        "desc": "عرض محوري للطاقم التربوي: السياق المجالي، التشخيص الموضعي، تجميع المتعلمين حسب المستوى، ونتائج الروائز.",
    },
    {
        "time": "10:25 – 10:45",
        "title": "استراحة ونقاش",
        "desc": "استراحة شاي وتبادل حر حول العرض المحوري.",
    },
    {
        "time": "10:45 – 12:15",
        "title": "ورشات عمل موازية",
        "desc": ".............................. .",
    },
    {
        "time": "12:15 – 12:45",
        "title": "التركيب والتوصيات",
        "desc": "عرض خلاصات الورشات وصياغةتوصيات، بتنسيق الأستاذة لبنى الدراوي.",
    },
    {
        "time": "12:45 – 13:00",
        "title": "التقييم والختام",
        "desc": "تقييم اليوم الدراسي وكلمة ختامية.",
    },
]

GALLERY = [
    {"file": "training2.jpg", "caption": "ورشة تذكيرية لأساتذة مؤسسات الريادة حول برنامج دعم التعلمات الأساس"},
    {"file": "training1.jpg", "caption": "تكوين حول الدعم المكثف من تنظيم مديرية المضيق-الفنيدق"},
    {"file": "classroom_practice.jpg", "caption": "الممارسة الصفية خلال حصص الدعم"},
    {"file": "gallery_visit.jpg", "caption": "مواكبة ميدانية لتجديد الممارسات الصفية"},
]

SPEAKERS = [
    {
        "initial": "أ",
        "photo": "speaker_daali.jpg",
        "name": "السيد أحمد دعلي",
        "role": "مفتش تربوي — تأطير اليوم الدراسي",
        "bio": "يؤطر اليوم الدراسي ويقدم الإطار العام لمرحلة الدعم المكثف بمؤسسات الريادة، من التشخيص الموضعي إلى بناء خطط الدعم.",
    },
    {
        "initial": "ل",
        "photo": "speaker_draoui.jpg",
        "name": "الأستاذة لبنى الدراوي",
        "role": "تنسيق اليوم الدراسي",
        "bio": "تتولى تنسيق فقرات اليوم الدراسي وتسيير النقاش حول تجربة المدرسة الجماعاتية أبي الحسن الشاذلي.",
    },
    {
        "initial": "م",
        "photo": None,
        "name": "المتدخلون",
        "role": "حوض الفنيدق",
        "bio": "تقديم  مداخلات تتعلق بمرحلة  الدعم المكثف.",
    },
]


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
def register():
    data = request.get_json(silent=True) or request.form

    full_name = (data.get("full_name") or "").strip()
    institution = (data.get("institution") or "").strip()
    email = (data.get("email") or "").strip()
    phone = (data.get("phone") or "").strip()
    workshop = (data.get("workshop") or "").strip()

    if not full_name or not email:
        return jsonify({
            "ok": False,
            "error": "الرجاء تعبئة الاسم الكامل والبريد الإلكتروني."
        }), 400

    file_exists = os.path.isfile(DATA_FILE)
    with open(DATA_FILE, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(CSV_HEADERS)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            full_name, institution, email, phone, workshop,
        ])

    return jsonify({
        "ok": True,
        "message": f"شكرًا {full_name}، تم تسجيل مشاركتك بنجاح في اليوم الدراسي. نراكم بالموعد!",
    })


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        password = request.form.get("password", "")
        if password == ADMIN_PASSWORD:
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
            workshop_counts[row[5]] = workshop_counts.get(row[5], 0) + 1
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

    def generate():
        yield "\ufeff"  # BOM ليُفتح الملف بشكل صحيح في Excel مع النص العربي
        yield ",".join(CSV_HEADERS) + "\n"
        for row in rows:
            yield ",".join(f'"{cell}"' for cell in row) + "\n"

    return Response(
        generate(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=لائحة_الحضور.csv"},
    )


if __name__ == "__main__":
    app.run(debug=False)
