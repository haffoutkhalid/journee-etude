from flask import (
    Flask, render_template, request, jsonify,
    session, redirect, url_for, Response,
)
from datetime import datetime
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "Riyada2026@chadhili@ecole"

# 🔒 إعدادات قاعدة البيانات (تم إصلاح المشكلة هنا)
database_url = os.environ.get('DATABASE_URL', 'sqlite:///inscriptions.db')
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
elif database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

ADMIN_PASSWORD = "Chadhili2026"


# 🔒 تعريف جدول المسجلين في قاعدة البيانات
class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(50))
    full_name = db.Column(db.String(120))
    institution = db.Column(db.String(160))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(30))
    workshop = db.Column(db.String(120))


# إنشاء الجدول عند تشغيل التطبيق
with app.app_context():
    db.create_all()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)

    return wrapped


# ---------------------------------------------------------------------------
# محتوى الصفحة (كما هو)
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

PROGRAM = [
    {"time": "08:30 – 08:50", "title": "الاستقبال والتسجيل", "desc": "استقبال المشاركين ........"},
    {"time": "08:50 – 09:10", "title": "الافتتاح الرسمي", "desc": "كلمة إدارة المدرسة الجماعاتية أبي الحسن الشاذلي ."},
    {"time": "09:10 – 09:40", "title": "الإطار العام لمرحلة الدعم المكثف",
     "desc": "عرض تأطيري للسيد المفتش التربوي أحمد دعلي: الدعم المكثف، الروائز التشخيصية والبعدية، أهداف مدارس الريادة."},
    {"time": "09:40 – 10:25", "title": "تجربة أبي الحسن الشاذلي: سنتان من الممارسة",
     "desc": "عرض محوري للطاقم التربوي: السياق المجالي، التشخيص الموضعي، تجميع المتعلمين حسب المستوى، ونتائج الروائز."},
    {"time": "10:25 – 10:45", "title": "استراحة ونقاش", "desc": "استراحة شاي وتبادل حر حول العرض المحوري."},
    {"time": "10:45 – 12:15", "title": "ورشات عمل موازية", "desc": ".............................. ."},
    {"time": "12:15 – 12:45", "title": "التركيب والتوصيات",
     "desc": "عرض خلاصات الورشات وصياغةتوصيات، بتنسيق الأستاذة لبنى الدراوي."},
    {"time": "12:45 – 13:00", "title": "التقييم والختام", "desc": "تقييم اليوم الدراسي وكلمة ختامية."},
]

GALLERY = [
    {"file": "training3.jpg", "caption": "ورشة تذكيرية لأساتذة مؤسسات الريادة حول برنامج دعم التعلمات الأساس"},
    {"file": "training1.jpg", "caption": "تكوين حول الدعم المكثف من تنظيم مديرية المضيق-الفنيدق"},
    {"file": "classroom_practice.jpg", "caption": "الممارسة الصفية خلال حصص الدعم"},
    {"file": "gallery_visit.jpg", "caption": "مواكبة ميدانية لتجديد الممارسات الصفية"},
]

SPEAKERS = [
    {"initial": "أ", "photo": "speaker_daali.jpg", "name": "السيد أحمد دعلي",
     "role": "مفتش تربوي — تأطير اليوم الدراسي",
     "bio": "يؤطر اليوم الدراسي ويقدم الإطار العام لمرحلة الدعم المكثف بمؤسسات الريادة، من التشخيص الموضعي إلى بناء خطط الدعم."},
    {"initial": "ل", "photo": "speaker_draoui.jpg", "name": "الأستاذة لبنى الدراوي", "role": "تنسيق اليوم الدراسي",
     "bio": "تتولى تنسيق فقرات اليوم الدراسي وتسيير النقاش حول تجربة المدرسة الجماعاتية أبي الحسن الشاذلي."},
    {"initial": "م", "photo": None, "name": "المتدخلون", "role": "حوض الفنيدق",
     "bio": "تقديم مداخلات تتعلق بمرحلة الدعم المكثف."},
]


@app.route("/")
def index():
    return render_template(
        "index.html", event_date_iso=EVENT_DATE_ISO, event_location=EVENT_LOCATION,
        event_directorate=EVENT_DIRECTORATE, proposals_deadline=PROPOSALS_DEADLINE,
        contact_phone=CONTACT_PHONE, program=PROGRAM, speakers=SPEAKERS,
        workshops=WORKSHOPS, gallery=GALLERY,
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
        return jsonify({"ok": False, "error": "الرجاء تعبئة الاسم الكامل والبريد الإلكتروني."}), 400

    new_reg = Registration(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
        full_name=full_name, institution=institution,
        email=email, phone=phone, workshop=workshop
    )
    db.session.add(new_reg)
    db.session.commit()

    return jsonify(
        {"ok": True, "message": f"شكرًا {full_name}، تم تسجيل مشاركتك بنجاح في اليوم الدراسي. نراكم بالموعد!"})


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
    rows = Registration.query.all()
    workshop_counts = {}
    for row in rows:
        key = row.workshop or "(غير محدد)"
        workshop_counts[key] = workshop_counts.get(key, 0) + 1

    formatted_rows = [[r.timestamp, r.full_name, r.institution, r.email, r.phone, r.workshop] for r in rows]

    return render_template("admin.html",
                           headers=["التاريخ والوقت", "الاسم الكامل", "المؤسسة/الوظيفة", "البريد الإلكتروني", "الهاتف",
                                    "الورشة المختارة"], rows=formatted_rows, total=len(rows),
                           workshop_counts=workshop_counts)


@app.route("/admin/delete/<int:row_index>", methods=["POST"])
@login_required
def admin_delete(row_index):
    rows = Registration.query.all()
    if 0 <= row_index < len(rows):
        reg_to_delete = rows[row_index]
        db.session.delete(reg_to_delete)
        db.session.commit()

    return redirect(url_for("admin_dashboard"))


@app.route("/admin/export")
@login_required
def admin_export():
    rows = Registration.query.all()

    def generate():
        yield "\ufeff"
        yield "التاريخ والوقت,الاسم الكامل,المؤسسة/الوظيفة,البريد الإلكتروني,الهاتف,الورشة المختارة\n"
        for r in rows:
            yield f'"{r.timestamp}","{r.full_name}","{r.institution}","{r.email}","{r.phone}","{r.workshop}"\n'

    return Response(generate(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=لائحة_الحضور.csv"})


if __name__ == "__main__":
    app.run(debug=False)