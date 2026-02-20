
from datetime import date, datetime, timedelta
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
        {"id": 1, "name": "Surya Raju", "roll_no": "24691A32R8", "clazz": "CSD"},
    ],
    "24691A32S8": [
        {"id": 1, "name": "Tharun Reddy", "roll_no": "24691A32S8", "clazz": "CSD"},
    ],
    "24691A32T7": [
        {"id": 1, "name": "Vamsi", "roll_no": "24691A32T7", "clazz": "CSD"},
    ],
}

# Subject-wise attendance data per user_id
# Format: {user_id: [{"subject": str, "present": int, "total": int}]}
subject_attendance = {
    "24691A32R8": [
        {"subject": "Aptitude","course code":"aps","present": 4, "total": 3},
        {"subject": "soft skills","course code":"ss","present": 3, "total": 3},
        {"subject": "Technical training","course code":"TT", "present": 8, "total": 10},
        {"subject": "Discrete Mathematical Structures","course code":"23MAT108","present": 12, "total": 12},
        {"subject": "environmental science","course code":"23CHE901", "present": 7, "total": 9},
        {"subject": "Introduction To Data Science","course code":"23CSD105","present": 12, "total": 13},
        {"subject": "Data Engineering","course code":"23CSD106", "present": 12, "total": 13},
        {"subject": "Data Science Laboratory","course code":"23CSD203", "present": 15, "total": 18},
        {"subject": "Data engineering laboratory","course code":"23CSD204", "present": 15, "total": 15},
        {"subject": "Product engineering and design thinking","course code":"23IIC5M03", "present": 8, "total": 10},
        {"subject": "Understanding incubation entreprenurship","course code":"23IIC5M06", "present": 8, "total": 9},
        {"subject": "Code Tantra","course code":"CT", "present": 8, "total": 8},
        {"subject": "devops","course code":"23CSD603", "present": 11, "total": 13},
    ],
    "24691A32S8": [
        {"subject": "Aptitude","course code":"aps", "present": 7, "total": 7},
        {"subject": "soft skills","course code":"ss", "present": 3, "total": 4},
        {"subject": "Technical training","course code":"TT", "present": 14, "total": 16},
        {"subject": "Discrete Mathematical Structures","course code":"23MAT108", "present": 14, "total": 19},
        {"subject": "environmental science","course code":"23CHE901", "present": 13, "total": 15},
        {"subject": "Digital Logic and computer organization","course code":"23CSD103", "present": 13, "total": 17},
        {"subject": "Introduction To Data Science","course code":"23CSD105", "present": 18, "total": 22},
        {"subject": "Data Engineering","course code":"23CSD106", "present": 14, "total": 18},
        {"subject": "Data Science Laboratory","course code":"23CSD203", "present": 21, "total": 27},
        {"subject": "Data engineering laboratory","course code":"23CSD204", "present": 17, "total": 23},
        {"subject": "Product engineering and design thinking","course code":"23IIC5M03", "present": 14, "total": 17},
        {"subject": "Understanding incubation entreprenurship","course code":"23IIC5M06", "present": 12, "total": 15},
        {"subject": "Code Tantra","course code":"CT", "present": 14, "total": 14},
        {"subject": "Devops","course code":"23CSD603", "present": 19, "total": 24},
    ],
    "24691A32T7": [
        {"subject": "Aptitude","course code":"", "present": 5, "total": 7},
        {"subject": "soft skills","course code":"", "present": 4, "total": 4},
        {"subject": "Technical training","course code":"TT", "present": 14, "total": 16},
        {"subject": "Discrete Mathematical Structures","course code":"23MAT108", "present": 15, "total": 19},
        {"subject": "environmental science","course code":"23CHE901", "present": 12, "total": 15},
        {"subject": "Digital Logic and computer organization","course code":"23CSD103", "present": 13, "total": 17},
        {"subject": "Introduction To Data Science","course code":"23CSD105", "present": 20, "total": 22},
        {"subject": "Data Engineering","course code":"23CSD106","present": 12, "total": 18},
        {"subject": "Data Science Laboratory","course code":"23CSD203", "present": 21, "total": 27},
        {"subject": "Data engineering laboratory","course code":"23CSD204", "present": 20, "total": 23},
        {"subject": "Product engineering and design thinking", "course code":"23IIC5M03","present": 12, "total": 17},
        {"subject": "Understanding incubation entreprenurship","course code":"23IIC5M06", "present": 10, "total": 15},
        {"subject": "Code Tantra","course code":"", "present": 12, "total": 14},
        {"subject": "devops","course code":"23CSD603", "present": 21, "total": 24},
    ]
}

# Timetable derived from the provided weekly schedule.
timetable = {
    "Mon": [
        {"period": 1, "subject": "23IIC5M06", "room": "SRB221", "teacher": "Mr. K Durga Charan"},
        {"period": 2, "subject": "23MAT108", "room": "SRB221", "teacher": "Dr. Sangeetha Dawan"},
        {"period": 3, "subject": "23CSD106", "room": "SRB221", "teacher": "Dr. K. Nirmala Devi"},
        {"period": 4, "subject": "23CSD103", "room": "SRB221", "teacher": "Dr. P. Ramanathan"},
        {"period": 5, "subject": "23CSD203", "room": "SRB219", "teacher": "RD / TB / AP"},
        {"period": 6, "subject": "23CSD203", "room": "SRB219", "teacher": "RD / TB / AP"},
        {"period": 7, "subject": "23CSD203", "room": "SRB219", "teacher": "RD / TB / AP"},
    ],
    "Tue": [
        {"period": 1, "subject": "23IIC5M03", "room": "SRB221", "teacher": "Mr. A Kalyan Kumar"},
        {"period": 2, "subject": "TT", "room": "SRB221", "teacher": "Mrs. Anuradha Prudhivi"},
        {"period": 3, "subject": "TT", "room": "SRB221", "teacher": "Mrs. Anuradha Prudhivi"},
        {"period": 4, "subject": "23CSD603", "room": "SRB221", "teacher": ""},
        {"period": 5, "subject": "SRB219", "room": "SRB219", "teacher": "NBV / AA / RD"},
    ],
    "Wed": [
        {"period": 1, "subject": "23CSD204", "room": "SRB221", "teacher": "Dr. K. Nirmala Devi"},
        {"period": 2, "subject": "23CSD204", "room": "SRB221", "teacher": "Dr. K. Nirmala Devi"},
        {"period": 3, "subject": "23CSD204", "room": "SRB221", "teacher": "Dr. K. Nirmala Devi"},
        {"period": 4, "subject": "23CSD105", "room": "SRB221", "teacher": "Mr. Rantu Das"},
        {"period": 5, "subject": "23CHE901", "room": "SRB221", "teacher": "Dr. K. V. Vivekananda"},
        {"period": 6, "subject": "23CSD103", "room": "SRB221", "teacher": "Dr. P. Ramanathan"},
        {"period": 7, "subject": "MM", "room": "SRB221", "teacher": "NO teacher"},
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
        {"period": 3, "subject": "CT", "room": "SRB221", "teacher": "Dr. S. Gopala Krishnan"},
        {"period": 4, "subject": "23IIC5M06", "room": "SRB221", "teacher": "Mr. K Durga Charan"},
        {"period": 5, "subject": "APS", "room": "SRB221", "teacher": "Mr. Chollangi Venkata Ramu"},
        {"period": 6, "subject": "23CSD105", "room": "SRB221", "teacher": "Mr. Rantu Das"},
        {"period": 7, "subject": "23CHE901", "room": "SRB221", "teacher": "Dr. K. V. Vivekananda"},
    ],
    "Sat": [
        {"period": 1, "subject": "23CSD603", "room": "SRB221", "teacher": "Mr. N Bhargav Krishna"},
        {"period": 2, "subject": "23IIC5M03", "room": "SRB221", "teacher": "Mr. A Kalyan Kumar"},
        {"period": 3, "subject": "23CSD106", "room": "SRB221", "teacher": "Dr. K. Nirmala Devi"},
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
def rebuild_subject_attendance(user_id):
    """Rebuild subject attendance from attendance_map while preserving initial data and order"""
    # Create a mapping of course code to subject info from existing subject_attendance
    course_code_to_subject = {}
    initial_data = {}
    initial_order = []  # Preserve original order
    
    if user_id in subject_attendance:
        for entry in subject_attendance[user_id]:
            code = entry.get("course code", "").strip()
            subject_name = entry.get("subject", "")
            
            # Store even if code is empty (for subjects like Aptitude, soft skills, Code Tantra)
            if code:
                course_code_to_subject[code] = subject_name
                initial_data[code] = {
                    "present": entry["present"],
                    "total": entry["total"]
                }
                initial_order.append(code)
            else:
                # Use subject name as key if no course code
                course_code_to_subject[subject_name] = subject_name
                initial_data[subject_name] = {
                    "present": entry["present"],
                    "total": entry["total"]
                }
                initial_order.append(subject_name)
    
    # Also build from timetable to get any missing codes
    for day_slots in timetable.values():
        for slot in day_slots:
            code = slot["subject"].upper()
            if code not in course_code_to_subject and code not in ["MM", "SRB219"]:
                course_code_to_subject[code] = code
    
    # Calculate NEW attendance counts from attendance_map (to add to existing)
    new_attendance = {}
    user_attendance = attendance_map.get(user_id, {})

    for date_key, periods in user_attendance.items():
        weekday = _weekday_key(date_key)
        slots = timetable.get(weekday, [])

        period_subject_map = {}
        for slot in slots:
            period_subject_map[int(slot["period"])] = slot["subject"].upper()

        for period, status in periods.items():
            # Ensure period is int for lookup
            period_int = int(period) if isinstance(period, str) else period
            subject_code = period_subject_map.get(period_int)
            if not subject_code or subject_code in ["MM", "SRB219"]:
                continue

            if subject_code not in new_attendance:
                new_attendance[subject_code] = {"present": 0, "total": 0}

            new_attendance[subject_code]["total"] += 1
            if status == "present":
                new_attendance[subject_code]["present"] += 1

    # Merge initial data with new attendance data
    merged_subjects = {}
    
    # Start with initial data
    for code, data in initial_data.items():
        merged_subjects[code] = {
            "subject": course_code_to_subject.get(code, code),
            "present": data["present"],
            "total": data["total"]
        }
    
    # Add new attendance on top
    for code, data in new_attendance.items():
        if code in merged_subjects:
            merged_subjects[code]["present"] += data["present"]
            merged_subjects[code]["total"] += data["total"]
        else:
            merged_subjects[code] = {
                "subject": course_code_to_subject.get(code, code),
                "present": data["present"],
                "total": data["total"]
            }
    
    # Convert to list format preserving original order
    result = []
    # First add subjects in their original order
    for code in initial_order:
        if code in merged_subjects:
            data = merged_subjects[code]
            result.append({
                "subject": data["subject"],
                "course code": code if code and code != data["subject"] else "",
                "present": data["present"],
                "total": data["total"]
            })
    
    # Then add any new subjects that weren't in initial data
    for code, data in merged_subjects.items():
        if code not in initial_order:
            result.append({
                "subject": data["subject"],
                "course code": code if code and code != data["subject"] else "",
                "present": data["present"],
                "total": data["total"]
            })
    
    subject_attendance[user_id] = result



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
        password = request.form.get("password", "").strip()
        
        if name and roll and clazz:
            # If password provided, create new user account
            if password:
                # Create user account with roll_no as user_id
                if roll not in users:
                    users[roll] = {
                        "password_hash": generate_password_hash(password),
                        "name": name,
                        "role": "student"
                    }
                    # Create initial subject_attendance with all subjects at 0/0
                    # Copy subject structure from existing student
                    template_subjects = subject_attendance.get("24691A32R8", [])
                    subject_attendance[roll] = [
                        {
                            "subject": subj["subject"],
                            "course code": subj.get("course code", ""),
                            "present": 0,
                            "total": 0
                        }
                        for subj in template_subjects
                    ]
                    # Create empty students data for new user
                    students_data[roll] = []
            
            # Add student record
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
    # Convert DD/MM/YYYY to YYYY-MM-DD if needed
    selected_date = _normalize_date_format(selected_date)
    
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
        
        # Get the date from form and normalize it
        form_date = request.form.get("date", "").strip()
        if form_date:
            selected_date = _normalize_date_format(form_date)
        
        weekday_key = _weekday_key(selected_date)
        slots = timetable.get(weekday_key, [])
        
        # Get valid periods for this day
        valid_periods = {slot['period'] for slot in slots}
        
        status_map = {}
        for slot in slots:
            raw = request.form.get(f"status_{slot['period']}")
            state = raw if raw in ("present", "absent") else None
            if state:
                status_map[int(slot["period"])] = state  # Store period as integer
        
        if target_user_id not in attendance_map:
            attendance_map[target_user_id] = {}
        attendance_map[target_user_id][selected_date] = status_map
        # Rebuild subject attendance from attendance_map to update reports
        rebuild_subject_attendance(target_user_id)
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
    # Don't rebuild here - only rebuild when attendance is saved
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


def _normalize_date_format(date_str: str) -> str:
    """Convert DD/MM/YYYY or other formats to YYYY-MM-DD format"""
    if not date_str:
        return date.today().isoformat()
    
    date_str = str(date_str).strip()
    
    if not date_str:
        return date.today().isoformat()
    
    # Try ISO format first (YYYY-MM-DD)
    try:
        datetime.fromisoformat(date_str)
        return date_str
    except:
        pass
    
    # Try DD/MM/YYYY format
    try:
        d = datetime.strptime(date_str, "%d/%m/%Y")
        result = d.strftime("%Y-%m-%d")
        return result
    except:
        pass
    
    # Try DD-MM-YYYY format  
    try:
        d = datetime.strptime(date_str, "%d-%m-%Y")
        return d.strftime("%Y-%m-%d")
    except:
        pass
    
    # Try M/D/YYYY format
    try:
        d = datetime.strptime(date_str, "%m/%d/%Y")
        return d.strftime("%Y-%m-%d")
    except:
        pass
    
    # If all else fails, return today's date
    return date.today().isoformat()


import os

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    ) 
