from datetime import date, datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = "change-me"  # replace for production

# In-memory demo data. Replace with a database later.
students = [
    {"id": 1, "name": "Ram", "roll_no": "101", "clazz": "CSE"},
    {"id": 2, "name": "Sita", "roll_no": "102", "clazz": "ECE"},
    {"id": 3, "name": "Aman", "roll_no": "103", "clazz": "ME"},
]

# Timetable derived from the provided weekly schedule.
timetable = {
    "Mon": [
        {"period": 1, "subject": "23IIC5M06", "room": "SRB221", "teacher": "Mr. K Durga Charan"},
        {"period": 2, "subject": "23MAT108", "room": "SRB221", "teacher": "Dr. Sangeetha Dawan"},
        {"period": 3, "subject": "23CSD106", "room": "SRB221", "teacher": "Dr. K. Nirmala Devi"},
        {"period": 4, "subject": "23CSD103", "room": "SRB221", "teacher": "Dr. P. Ramanathan"},
        {"period": 5, "subject": "23CSD203", "room": "SRB219", "teacher": ""},
        {"period": 6, "subject": "SRB219", "room": "SRB219", "teacher": "RD / TB / AP"},
        {"period": 7, "subject": "SRB219", "room": "SRB219", "teacher": "RD / TB / AP"},
    ],
    "Tue": [
        {"period": 1, "subject": "23IIC5M03", "room": "SRB221", "teacher": "Mr. A Kalyan Kumar"},
        {"period": 2, "subject": "SRB221", "room": "SRB221", "teacher": ""},
        {"period": 3, "subject": "TT", "room": "SRB221", "teacher": "Mrs. Anuradha Prudhivi"},
        {"period": 4, "subject": "23CSD603", "room": "SRB221", "teacher": ""},
        {"period": 5, "subject": "SRB219", "room": "SRB219", "teacher": "NBV / AA / RD"},
        {"period": 6, "subject": "HA", "room": "", "teacher": ""},
        {"period": 7, "subject": "HA", "room": "", "teacher": ""},
    ],
    "Wed": [
        {"period": 1, "subject": "23CSD204", "room": "SRB221", "teacher": ""},
        {"period": 2, "subject": "23CSD204", "room": "SRB221", "teacher": ""},
        {"period": 3, "subject": "23CSD204", "room": "SRB221", "teacher": ""},
        {"period": 4, "subject": "23CSD105", "room": "SRB221", "teacher": "Mr. Rantu Das"},
        {"period": 5, "subject": "23CHE901", "room": "SRB221", "teacher": "Dr. K. V. Vivekananda"},
        {"period": 6, "subject": "23CSD103", "room": "SRB221", "teacher": "Dr. P. Ramanathan"},
        {"period": 7, "subject": "MM", "room": "SRB221", "teacher": ""},
    ],
    "Thu": [
        {"period": 1, "subject": "23CSD105", "room": "SRB221", "teacher": "Mr. Rantu Das"},
        {"period": 2, "subject": "23CSD103", "room": "SRB221", "teacher": "Dr. P. Ramanathan"},
        {"period": 3, "subject": "23MAT108", "room": "SRB221", "teacher": "Dr. Sangeetha Dawan"},
        {"period": 4, "subject": "23CSD106", "room": "SRB221", "teacher": "Dr. K. Nirmala Devi"},
        {"period": 5, "subject": "SS", "room": "SRB221", "teacher": "Dr. Anusha Bharath"},
        {"period": 6, "subject": "HA", "room": "", "teacher": ""},
        {"period": 7, "subject": "HA", "room": "", "teacher": ""},
    ],
    "Fri": [
        {"period": 1, "subject": "23MAT108", "room": "SRB221", "teacher": "Dr. Sangeetha Dawan"},
        {"period": 2, "subject": "CT", "room": "SRB221", "teacher": "Dr. S. Gopala Krishnan"},
        {"period": 3, "subject": "23CSD106", "room": "SRB221", "teacher": "Dr. K. Nirmala Devi"},
        {"period": 4, "subject": "23IIC5M06", "room": "SRB221", "teacher": "Mr. K Durga Charan"},
        {"period": 5, "subject": "APS", "room": "SRB221", "teacher": "Mr. Chollangi Venkata Ramu"},
        {"period": 6, "subject": "23CSD105", "room": "SRB221", "teacher": "Mr. Rantu Das"},
        {"period": 7, "subject": "23CHE901", "room": "SRB221", "teacher": "Dr. K. V. Vivekananda"},
    ],
    "Sat": [
        {"period": 1, "subject": "23CSD603", "room": "SRB221", "teacher": "Mr. N Bhargav Krishna"},
        {"period": 2, "subject": "23IIC5M03", "room": "SRB221", "teacher": "Mr. A Kalyan Kumar"},
        {"period": 3, "subject": "23CSD106", "room": "SRB221", "teacher": "Dr. K. Nirmala Devi"},
        {"period": 4, "subject": "23CSD106", "room": "SRB221", "teacher": "Dr. K. Nirmala Devi"},
        {"period": 5, "subject": "23CSD106", "room": "SRB221", "teacher": "Dr. K. Nirmala Devi"},
        {"period": 6, "subject": "HA", "room": "", "teacher": ""},
        {"period": 7, "subject": "HA", "room": "", "teacher": ""},
    ],
}

# Period timings (start - end)
period_times = {
    1: "09:10 - 10:10",
    2: "10:10 - 11:10",
    3: "11:10 - 12:10",
    # Lunch 12:10 - 13:00
    4: "13:00 - 14:00",
    5: "14:00 - 15:00",
    6: "15:00 - 16:00",
    7: "16:00 - 17:00",
}

# attendance_map[yyyy-mm-dd] = {period: "present"|"absent"}
attendance_map = {}


def require_login():
    if "user" not in session:
        return False
    return True


@app.route("/")
def index():
    if not require_login():
        return redirect(url_for("login"))
    return redirect(url_for("dashboard"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("email") or "User"
        session["user"] = username
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if not require_login():
        return redirect(url_for("login"))
    summary = _attendance_summary(date.today())
    return render_template("dashboard.html", user=session.get("user"), summary=summary)


@app.route("/students", methods=["GET", "POST"])
def students_page():
    if not require_login():
        return redirect(url_for("login"))
    if request.method == "POST":
        name = request.form.get("name")
        roll = request.form.get("roll_no")
        clazz = request.form.get("clazz")
        if name and roll and clazz:
            new_id = max([s["id"] for s in students] + [0]) + 1
            students.append({"id": new_id, "name": name, "roll_no": roll, "clazz": clazz})
        return redirect(url_for("students_page"))
    return render_template("students.html", user=session.get("user"), students=students)


@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    if not require_login():
        return redirect(url_for("login"))

    selected_date = request.args.get("date") or date.today().isoformat()
    weekday_key = _weekday_key(selected_date)
    slots = timetable.get(weekday_key, [])

    # Tabs: show Today / Tomorrow / Next (e.g., Friday in your screenshot)
    base_date = _safe_date(selected_date)
    tab_dates = [
        base_date,
        base_date + timedelta(days=1),
        base_date + timedelta(days=2),
    ]

    if request.method == "POST":
        selected_date = request.form.get("date") or selected_date
        weekday_key = _weekday_key(selected_date)
        slots = timetable.get(weekday_key, [])
        status_map = {}
        for slot in slots:
            raw = request.form.get(f"status_{slot['period']}")
            state = raw if raw in ("present", "absent") else None
            if state:
                status_map[slot["period"]] = state
        attendance_map[selected_date] = status_map
        return redirect(url_for("attendance", date=selected_date))

    existing = attendance_map.get(selected_date, {})
    return render_template(
        "attendance.html",
        user=session.get("user"),
        selected_date=selected_date,
        weekday=weekday_key,
        slots=slots,
        existing=existing,
        period_times=period_times,
        tab_dates=tab_dates,
    )


@app.route("/reports")
def reports():
    if not require_login():
        return redirect(url_for("login"))
    month = request.args.get("month") or date.today().strftime("%Y-%m")
    summary = _monthly_summary(month)
    return render_template("reports.html", user=session.get("user"), month=month, summary=summary)


@app.route("/api/reports/export")
def export_report():
    fmt = request.args.get("format", "pdf")
    return jsonify({"status": "not_implemented", "message": f"Export as {fmt} coming soon"})


def _attendance_summary(target_date: date):
    key = target_date.isoformat()
    weekday_key = _weekday_key(key)
    slots = timetable.get(weekday_key, [])
    records = attendance_map.get(key, {})
    total = len(slots)
    present = list(records.values()).count("present")
    absent = list(records.values()).count("absent")
    pct = round((present / total) * 100, 2) if total else 0
    return {
        "total_slots": total,
        "present": present,
        "absent": absent,
        "percentage": pct,
        "date": key,
        "weekday": weekday_key,
    }


def _monthly_summary(month_str: str):
    total_days = 0
    total_present = 0
    total_slots = 0
    for key, records in attendance_map.items():
        if key.startswith(month_str):
            weekday_key = _weekday_key(key)
            slots = timetable.get(weekday_key, [])
            total_days += 1
            total_slots += len(slots)
            total_present += list(records.values()).count("present")
    pct = round((total_present / total_slots) * 100, 2) if total_slots else 0
    return {
        "month": month_str,
        "total_days": total_days,
        "total_slots": total_slots,
        "average_percent": pct,
    }


def _weekday_key(date_str: str) -> str:
    """Return short weekday name (Mon, Tue, Wed, Thu, Fri, Sat, Sun) for a yyyy-mm-dd string."""
    try:
        d = datetime.fromisoformat(date_str)
    except ValueError:
        d = date.today()
    return d.strftime("%a")


def _safe_date(date_str: str) -> date:
    try:
        return datetime.fromisoformat(date_str).date()
    except ValueError:
        return date.today()


if __name__ == "__main__":
    app.run(debug=True)

