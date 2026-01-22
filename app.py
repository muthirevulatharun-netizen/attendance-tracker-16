rom datetime import date, datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "change-me"  # replace for production

@app.context_processor
def inject_admin_context():
    """Make admin context available to all templates"""
    try:
        user_id = session.get("user_id")
        is_admin_user = False
        student_list = []
        if user_id and user_id in users:
            is_admin_user = users[user_id].get("role") == "admin"
            student_list = [{"id": uid, "name": u["name"]} for uid, u in users.items() if u.get("role") == "student"]
        return {
            "is_admin": is_admin_user,
            "student_users": student_list
        }
    except:
        return {"is_admin": False, "student_users": []}

# User database with user IDs and passwords
# Format: {user_id: {"password_hash": str, "name": str, "role": str}}
users = {
    "admin": {
        "password_hash": generate_password_hash("admin123"),
        "name": "Administrator",
        "role": "admin"
    },
    "24691A32R8": {
        "password_hash": generate_password_hash("passwordr8"),
        "name": "Surya Raju",
        "role": "student"
    },
    "24691A32S8": {
        "password_hash": generate_password_hash("passwords8"),
        "name": "Tharun Reddy",
        "role": "student"
    },
    "24691A32T7": {
        "password_hash": generate_password_hash("passwordt7"),
        "name": "Vamsi",
        "role": "student"
    }
}

# Students data per user_id
# Format: {user_id: [list of students]}
students_data = {
    "24691A32R8": [
        {"id": 1, "name": "Surya Raju", "roll_no": "24691A32R8", "clazz": "CSE"},
    ],
    "24691A32S8": [
        {"id": 1, "name": "Tharun Reddy", "roll_no": "24691A32S8", "clazz": "CSE"},
    ],
    "24691A32T7": [
        {"id": 1, "name": "Vamsi", "roll_no": "24691A32T7", "clazz": "CSE"},
    ],
}

# Subject-wise attendance data per user_id
# Format: {user_id: [{"subject": str, "present": int, "total": int}]}
subject_attendance = {
    "24691A32R8": [
        {"subject": "Aptitude", "present": 3, "total": 3},
        {"subject": "soft skills", "present": 1, "total": 1},
        {"subject": "Discrete Mathematical Structures", "present": 8, "total": 8},
        {"subject": "environmental science", "present": 4, "total": 6},
        {"subject": "Introduction To Data Science", "present": 8, "total": 8},
        {"subject": "Data Engineering", "present": 8, "total": 8},
        {"subject": "Data Science Laboratory", "present": 12, "total": 12},
        {"subject": "Data engineering laboratory", "present": 9, "total": 9},
        {"subject": "NPTEL-1", "present": 6, "total": 6},
        {"subject": "NPTEL-2", "present": 5, "total": 5},
        {"subject": "Code Tantra", "present": 6, "total": 6},
        {"subject": "devops", "present": 8, "total": 8},
    ],
    "24691A32S8": [
        {"subject": "Aptitude", "present": 3, "total": 3},
        {"subject": "soft skills", "present": 2, "total": 3},
        {"subject": "Technical training", "present": 8, "total": 10},
        {"subject": "Discrete Mathematical Structures", "present": 9, "total": 12},
        {"subject": "environmental science", "present": 7, "total": 9},
        {"subject": "DLCO", "present": 6, "total": 8},
        {"subject": "Introduction To Data Science", "present": 9, "total": 13},
        {"subject": "Data Engineering", "present": 9, "total": 13},
        {"subject": "Data Science Laboratory", "present": 12, "total": 18},
        {"subject": "Data engineering laboratory", "present": 9, "total": 15},
        {"subject": "NPTEL-1", "present": 8, "total": 9},
        {"subject": "NPTEL-2", "present": 7, "total": 10},
        {"subject": "Code Tantra", "present": 8, "total": 8},
        {"subject": "devops", "present": 8, "total": 13},
    ],
    "24691A32T7": [
        {"subject": "Aptitude", "present": 2, "total": 3},
        {"subject": "soft skills", "present": 1, "total": 1},
        {"subject": "Discrete Mathematical Structures", "present": 7, "total": 8},
        {"subject": "environmental science", "present": 4, "total": 6},
        {"subject": "Introduction To Data Science", "present": 7, "total": 8},
        {"subject": "Data Engineering", "present": 5, "total": 8},
        {"subject": "Data Science Laboratory", "present": 9, "total": 12},
        {"subject": "Data engineering laboratory", "present": 6, "total": 9},
        {"subject": "NPTEL-1", "present": 3, "total": 6},
        {"subject": "NPTEL-2", "present": 3, "total": 5},
        {"subject": "Code Tantra", "present": 4, "total": 6},
        {"subject": "devops", "present": 6, "total": 8},
    ]
}

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

# attendance_map[user_id][yyyy-mm-dd] = {period: "present"|"absent"}
attendance_map = {}


def require_login():
    if "user" not in session:
        return False
    return True

def is_admin():
    """Check if current user is admin"""
    user_id = session.get("user_id")
    if user_id and user_id in users:
        return users[user_id].get("role") == "admin"
    return False

def get_target_user_id():
    """Get the target user_id for data access (admin can select, others see their own)"""
    if is_admin():
        # Admin can view/edit any user's data via query parameter
        target_id = request.args.get("user_id") or request.form.get("user_id")
        if target_id and target_id in users:
            return target_id
        # If no specific user selected, return first student user
        student_users = [uid for uid, u in users.items() if u.get("role") == "student"]
        return student_users[0] if student_users else None
    else:
        # Regular users only see their own data
        return session.get("user_id")


@app.route("/")
def index():
    if not require_login():
        return redirect(url_for("login"))
    return redirect(url_for("dashboard"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        
        # Check if user exists (admin can be lowercase, students are uppercase)
        user = users.get(user_id) or users.get(user_id.upper())
        if not user:
            user_id = user_id.upper()
            user = users.get(user_id)
        
        if user and check_password_hash(user["password_hash"], password):
            session["user"] = user["name"]
            session["user_id"] = user_id if user_id in users else user_id.upper()
            session["role"] = user.get("role", "student")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid User ID or password. Please try again.", "error")
            return render_template("login.html", error="Invalid credentials")
    
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("user_id", None)
    session.pop("role", None)
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if not require_login():
        return redirect(url_for("login"))
    target_user_id = get_target_user_id()
    if not target_user_id:
        return redirect(url_for("login"))
    summary = _attendance_summary(date.today(), target_user_id)
    
    # Get overall statistics from subject attendance data
    subjects_data = subject_attendance.get(target_user_id, [])
    total_present_all = sum(s["present"] for s in subjects_data)
    total_classes_all = sum(s["total"] for s in subjects_data)
    overall_percentage = round((total_present_all / total_classes_all * 100), 2) if total_classes_all > 0 else 0
    total_absent_all = total_classes_all - total_present_all
    
    student_users = [{"id": uid, "name": u["name"]} for uid, u in users.items() if u.get("role") == "student"]
    return render_template("dashboard.html", 
                         user=session.get("user"), 
                         summary=summary,
                         total_present_all=total_present_all,
                         total_classes_all=total_classes_all,
                         total_absent_all=total_absent_all,
                         overall_percentage=overall_percentage,
                         is_admin=is_admin(),
                         student_users=student_users,
                         selected_user_id=target_user_id)


@app.route("/students", methods=["GET", "POST"])
def students_page():
    if not require_login():
        return redirect(url_for("login"))
    target_user_id = get_target_user_id()
    if not target_user_id:
        return redirect(url_for("login"))
    
    if target_user_id not in students_data:
        students_data[target_user_id] = []
    
    if request.method == "POST":
        # Admin can specify which user to add student for
        if is_admin():
            target_user_id = request.form.get("user_id") or target_user_id
        
        name = request.form.get("name")
        roll = request.form.get("roll_no")
        clazz = request.form.get("clazz")
        if name and roll and clazz:
            if target_user_id not in students_data:
                students_data[target_user_id] = []
            user_students = students_data.get(target_user_id, [])
            new_id = max([s["id"] for s in user_students] + [0]) + 1
            students_data[target_user_id].append({"id": new_id, "name": name, "roll_no": roll, "clazz": clazz})
        return redirect(url_for("students_page", user_id=target_user_id if is_admin() else None))
    
    user_students = students_data.get(target_user_id, [])
    student_users = [{"id": uid, "name": u["name"]} for uid, u in users.items() if u.get("role") == "student"]
    return render_template("students.html", 
                         user=session.get("user"), 
                         students=user_students,
                         is_admin=is_admin(),
                         student_users=student_users,
                         selected_user_id=target_user_id)


@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    if not require_login():
        return redirect(url_for("login"))

    target_user_id = get_target_user_id()
    if not target_user_id:
        return redirect(url_for("login"))
    
    if target_user_id not in attendance_map:
        attendance_map[target_user_id] = {}

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
        # Admin can specify which user to update attendance for
        if is_admin():
            target_user_id = request.form.get("user_id") or target_user_id
        
        selected_date = request.form.get("date") or selected_date
        weekday_key = _weekday_key(selected_date)
        slots = timetable.get(weekday_key, [])
        status_map = {}
        for slot in slots:
            raw = request.form.get(f"status_{slot['period']}")
            state = raw if raw in ("present", "absent") else None
            if state:
                status_map[slot["period"]] = state
        if target_user_id not in attendance_map:
            attendance_map[target_user_id] = {}
        attendance_map[target_user_id][selected_date] = status_map
        redirect_url = url_for("attendance", date=selected_date)
        if is_admin():
            redirect_url += f"&user_id={target_user_id}"
        return redirect(redirect_url)

    existing = attendance_map[target_user_id].get(selected_date, {})
    student_users = [{"id": uid, "name": u["name"]} for uid, u in users.items() if u.get("role") == "student"]
    return render_template(
        "attendance.html",
        user=session.get("user"),
        selected_date=selected_date,
        weekday=weekday_key,
        slots=slots,
        existing=existing,
        period_times=period_times,
        tab_dates=tab_dates,
        is_admin=is_admin(),
        student_users=student_users,
        selected_user_id=target_user_id,
    )


@app.route("/reports")
def reports():
    if not require_login():
        return redirect(url_for("login"))
    target_user_id = get_target_user_id()
    if not target_user_id:
        return redirect(url_for("login"))
    month = request.args.get("month") or date.today().strftime("%Y-%m")
    summary = _monthly_summary(month, target_user_id)
    # Get subject-wise attendance data
    subjects_data = subject_attendance.get(target_user_id, [])
    # Calculate overall statistics from subject data
    total_present = sum(s["present"] for s in subjects_data)
    total_classes = sum(s["total"] for s in subjects_data)
    overall_percentage = round((total_present / total_classes * 100), 2) if total_classes > 0 else 0
    
    student_users = [{"id": uid, "name": u["name"]} for uid, u in users.items() if u.get("role") == "student"]
    return render_template("reports.html", 
                         user=session.get("user"), 
                         month=month, 
                         summary=summary,
                         subjects_data=subjects_data,
                         total_present=total_present,
                         total_classes=total_classes,
                         overall_percentage=overall_percentage,
                         is_admin=is_admin(),
                         student_users=student_users,
                         selected_user_id=target_user_id)


@app.route("/api/reports/export")
def export_report():
    fmt = request.args.get("format", "pdf")
    return jsonify({"status": "not_implemented", "message": f"Export as {fmt} coming soon"})


def _attendance_summary(target_date: date, user_id: str):
    key = target_date.isoformat()
    weekday_key = _weekday_key(key)
    slots = timetable.get(weekday_key, [])
    user_attendance = attendance_map.get(user_id, {})
    records = user_attendance.get(key, {})
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


def _monthly_summary(month_str: str, user_id: str):
    total_days = 0
    total_present = 0
    total_slots = 0
    user_attendance = attendance_map.get(user_id, {})
    for key, records in user_attendance.items():
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


import os

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )


