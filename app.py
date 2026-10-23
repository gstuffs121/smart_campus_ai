
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)
from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)
from flask_mysqldb import MySQL

from config import (
    MYSQL_HOST,
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_DB,
    SECRET_KEY,
)

from ai.classifier import classify_complaint
from ai.priority import calculate_priority
from ai.sentiment import analyze_sentiment
from ai.duplicate_detector import find_duplicate
from ai.escalation import calculate_escalation
from ai.recommendation import generate_recommendation
from ai.emergency_detector import detect_emergency

# ===== EMAIL AND PASSWORD VALIDATION =====
import re

def is_valid_email(email):
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return re.fullmatch(pattern, email) is not None


def is_strong_password(password):
    return (
        len(password) >= 8
        and bool(re.search(r"[A-Z]", password))
        and bool(re.search(r"[a-z]", password))
        and bool(re.search(r"\d", password))
        and bool(re.search(r"[^A-Za-z0-9]", password))
    )


app = Flask(__name__)

# Flask and MySQL configuration
app.secret_key = SECRET_KEY

app.config["MYSQL_HOST"] = MYSQL_HOST
app.config["MYSQL_USER"] = MYSQL_USER
app.config["MYSQL_PASSWORD"] = MYSQL_PASSWORD
app.config["MYSQL_DB"] = MYSQL_DB
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)


# ---------------------------------------------------------
# HOME
# ---------------------------------------------------------

@app.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") == "admin":
        return redirect(url_for("admin_dashboard"))

    return redirect(url_for("student_dashboard"))


# ---------------------------------------------------------
# REGISTER
# ---------------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        role = request.form.get("role", "").strip()

        if not name or not email or not password or not confirm_password or not role:
            flash("Please fill all fields.")
            return redirect(url_for("register"))
            
        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for("register"))

        if not is_valid_email(email):
            flash("Please enter a valid email address.")
            return redirect(url_for("register"))
            
        if not is_strong_password(password):
            flash(
                "Password must contain at least 8 characters, "
                "one uppercase letter, one lowercase letter, "
                "one number, and one special character."
            )
            return redirect(url_for("register"))

        allowed_roles = ["student", "faculty", "non_faculty"]

        if role not in allowed_roles:
            flash("Please select a valid role.")
            return redirect(url_for("register"))

        cursor = mysql.connection.cursor()

        try:
            cursor.execute(
                "SELECT id FROM users WHERE email = %s",
                (email,),
            )
            existing_user = cursor.fetchone()

            if existing_user:
                flash("Email already registered.")
                return redirect(url_for("register"))

            hashed_password = generate_password_hash(password)

            cursor.execute(
                """
                INSERT INTO users (name, email, password, role)
                VALUES (%s, %s, %s, %s)
                """,
                (name, email, hashed_password, role),
            )

            mysql.connection.commit()
            flash("Registration successful. Please login.")

        except Exception:
            mysql.connection.rollback()
            app.logger.exception("Registration failed.")
            flash("Registration failed. Please try again.")

        finally:
            cursor.close()

        return redirect(url_for("login"))

    return render_template("register.html")


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        cursor = mysql.connection.cursor()

        try:
            cursor.execute(
                "SELECT * FROM users WHERE email = %s",
                (email,),
            )
            user = cursor.fetchone()

        finally:
            cursor.close()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["role"] = user["role"]

            if user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))

            return redirect(url_for("student_dashboard"))

        flash("Invalid email or password.")

    return render_template("login.html")


# ---------------------------------------------------------
# STUDENT / FACULTY / STAFF DASHBOARD
# ---------------------------------------------------------

@app.route("/student/dashboard")
def student_dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") == "admin":
        return redirect(url_for("admin_dashboard"))

    cursor = mysql.connection.cursor()

    try:
        cursor.execute(
            """
            SELECT *
            FROM complaints
            WHERE user_id = %s
            ORDER BY created_at DESC
            """,
            (session["user_id"],),
        )
        complaints = cursor.fetchall()

    finally:
        cursor.close()

    role = session.get("role")

    if role == "faculty":
        return render_template(
            "faculty_dashboard.html",
            complaints=complaints,
        )

    if role == "non_faculty":
        return render_template(
            "staff_dashboard.html",
            complaints=complaints,
        )

    return render_template(
        "student_dashboard.html",
        complaints=complaints,
    )


# ---------------------------------------------------------
# NEW COMPLAINT + EMERGENCY DETECTION
# ---------------------------------------------------------

@app.route("/student/complaint/new", methods=["GET", "POST"])
def new_complaint():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") == "admin":
        return redirect(url_for("admin_dashboard"))

    emergency_result = detect_emergency("", "")

    if request.method == "GET":
        return render_template(
            "submit_complaint.html",
            emergency_result=emergency_result,
        )

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    location = request.form.get("location", "").strip()

    # Check the submitted text for configured emergency phrases.
    emergency_result = detect_emergency(title, description)

    if emergency_result["is_emergency"]:
        app.logger.warning(
            "Potential emergency reported by user ID %s: %s",
            session["user_id"],
            ", ".join(emergency_result["detected_types"]),
        )

    if not title or not description or not location:
        flash("Please fill all complaint fields.")

        return render_template(
            "submit_complaint.html",
            emergency_result=emergency_result,
        )

    full_text = title + " " + description

    # AI 1 - Department classification
    department = classify_complaint(title, description)

    # AI 2 - Sentiment analysis
    sentiment = analyze_sentiment(full_text)

    # AI 3 - Priority calculation
    priority_score, priority_level = calculate_priority(
        title,
        description,
        sentiment,
    )

    # AI 4 - Escalation risk
    escalation_risk = calculate_escalation(
        priority_score,
        sentiment,
    )

    # AI 5 - Recommendation
    recommendation = generate_recommendation(
        department,
        priority_level,
        escalation_risk,
    )

    explanation = (
        f"The complaint was analyzed as {priority_level} "
        f"priority with a score of {priority_score}/100. "
        f"The detected department is {department}. "
        f"Sentiment was classified as {sentiment}, "
        f"with {escalation_risk} escalation risk."
    )

    cursor = mysql.connection.cursor()

    try:
        # AI 6 - Duplicate detection
        cursor.execute(
            """
            SELECT id, title, description
            FROM complaints
            ORDER BY created_at DESC
            """
        )
        existing_complaints = cursor.fetchall()

        old_texts = [
            (complaint.get("title") or "")
            + " "
            + (complaint.get("description") or "")
            for complaint in existing_complaints
        ]

        duplicate_index, similarity = find_duplicate(
            full_text,
            old_texts,
        )

        duplicate_status = duplicate_index is not None
        duplicate_of = None

        if duplicate_status:
            duplicate_of = existing_complaints[duplicate_index]["id"]

        cursor.execute(
            """
            INSERT INTO complaints
            (
                user_id,
                title,
                description,
                category,
                location,
                department,
                urgency,
                sentiment,
                priority_score,
                priority_level,
                duplicate_status,
                duplicate_of,
                escalation_risk,
                ai_explanation,
                ai_recommendation,
                status
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, 'Pending'
            )
            """,
            (
                session["user_id"],
                title,
                description,
                department,
                location,
                department,
                priority_level,
                sentiment,
                priority_score,
                priority_level,
                duplicate_status,
                duplicate_of,
                escalation_risk,
                explanation,
                recommendation,
            ),
        )

        mysql.connection.commit()

    except Exception:
        mysql.connection.rollback()
        app.logger.exception("Could not save complaint.")

        flash("The complaint could not be saved. Please try again.")

        return render_template(
            "submit_complaint.html",
            emergency_result=emergency_result,
        )

    finally:
        cursor.close()

    if emergency_result["is_emergency"]:
        flash(
            "SAFETY WARNING: A potential hazard was detected. "
            "Contact the appropriate campus safety team immediately "
            "if anyone may be in danger."
        )

    flash(
        f"Complaint submitted successfully! "
        f"AI Priority: {priority_level} ({priority_score}/100)"
    )

    return redirect(url_for("student_dashboard"))


# ---------------------------------------------------------
# USER COMPLAINT DETAILS
# ---------------------------------------------------------

@app.route("/student/complaint/<int:complaint_id>")
def complaint_details(complaint_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    cursor = mysql.connection.cursor()

    try:
        cursor.execute(
            """
            SELECT *
            FROM complaints
            WHERE id = %s AND user_id = %s
            """,
            (complaint_id, session["user_id"]),
        )
        complaint = cursor.fetchone()

    finally:
        cursor.close()

    if not complaint:
        flash("Complaint not found.")
        return redirect(url_for("student_dashboard"))

    return render_template(
        "complaint_details.html",
        complaint=complaint,
    )


# ---------------------------------------------------------
# ADMIN COMPLAINT DETAILS + STATUS UPDATE
# ---------------------------------------------------------

@app.route(
    "/admin/complaint/<int:complaint_id>",
    methods=["GET", "POST"],
)
def admin_complaint_details(complaint_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("student_dashboard"))

    cursor = mysql.connection.cursor()

    if request.method == "POST":
        new_status = request.form.get("status", "").strip()
        remarks = request.form.get("remarks", "").strip()

        allowed_statuses = [
            "Pending",
            "In Progress",
            "Resolved",
            "Rejected",
        ]

        if new_status not in allowed_statuses:
            cursor.close()
            flash("Invalid status selected.")
            return redirect(
                url_for(
                    "admin_complaint_details",
                    complaint_id=complaint_id,
                )
            )

        try:
            cursor.execute(
                "SELECT status FROM complaints WHERE id = %s",
                (complaint_id,),
            )
            current_complaint = cursor.fetchone()

            if not current_complaint:
                flash("Complaint not found.")
                return redirect(url_for("admin_dashboard"))

            old_status = current_complaint["status"]

            cursor.execute(
                """
                UPDATE complaints
                SET status = %s
                WHERE id = %s
                """,
                (new_status, complaint_id),
            )

            cursor.execute(
                """
                INSERT INTO complaint_history
                (
                    complaint_id,
                    old_status,
                    new_status,
                    changed_by,
                    remarks
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    complaint_id,
                    old_status,
                    new_status,
                    session["user_id"],
                    remarks,
                ),
            )

            mysql.connection.commit()
            flash("Complaint status updated successfully.")

        except Exception:
            mysql.connection.rollback()
            app.logger.exception("Could not update complaint status.")
            flash("The status could not be updated.")

        finally:
            cursor.close()

        return redirect(
            url_for(
                "admin_complaint_details",
                complaint_id=complaint_id,
            )
        )

    try:
        cursor.execute(
            """
            SELECT
                c.*,
                u.name AS user_name,
                u.email AS user_email,
                u.role AS user_role
            FROM complaints c
            JOIN users u ON c.user_id = u.id
            WHERE c.id = %s
            """,
            (complaint_id,),
        )
        complaint = cursor.fetchone()

        if not complaint:
            flash("Complaint not found.")
            return redirect(url_for("admin_dashboard"))

        cursor.execute(
            """
            SELECT
                ch.*,
                u.name AS changed_by_name
            FROM complaint_history ch
            LEFT JOIN users u ON ch.changed_by = u.id
            WHERE ch.complaint_id = %s
            ORDER BY ch.changed_at DESC
            """,
            (complaint_id,),
        )
        history = cursor.fetchall()

    finally:
        cursor.close()

    return render_template(
        "admin_complaint_details.html",
        complaint=complaint,
        history=history,
    )


# ---------------------------------------------------------
# ADMIN DASHBOARD
# ---------------------------------------------------------

@app.route("/admin/dashboard")
def admin_dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("student_dashboard"))

    cursor = mysql.connection.cursor()

    try:
        cursor.execute(
            """
            SELECT *
            FROM complaints
            ORDER BY priority_score DESC, created_at DESC
            """
        )
        complaints = cursor.fetchall()

        cursor.execute(
            "SELECT COUNT(*) AS total FROM complaints"
        )
        total = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT COUNT(*) AS total FROM complaints WHERE status = 'Pending'"
        )
        pending = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT COUNT(*) AS total FROM complaints WHERE status = 'In Progress'"
        )
        in_progress = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT COUNT(*) AS total FROM complaints WHERE status = 'Resolved'"
        )
        resolved = cursor.fetchone()["total"]

    finally:
        cursor.close()

    return render_template(
        "admin_dashboard.html",
        complaints=complaints,
        total=total,
        pending=pending,
        in_progress=in_progress,
        resolved=resolved,
    )


# ---------------------------------------------------------
# LOGOUT
# ---------------------------------------------------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------------------------------------------------
# ERROR HANDLERS
# ---------------------------------------------------------

@app.errorhandler(404)
def page_not_found(error):
    return "Page not found", 404


@app.errorhandler(500)
def internal_error(error):
    app.logger.exception("An internal server error occurred: %s", error)
    return "Internal server error", 500


# ---------------------------------------------------------
# RUN APPLICATION
# ---------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
