from flask import (Blueprint, render_template, request, redirect,
                   url_for, session, flash)

from .database import Database
from .services import register_user, authenticate, search_doctors
from .booking import book_appointment
from .notifications import NotificationService, EmailNotifier, SMSNotifier

bp = Blueprint("main", __name__)


def conn():
    return Database.getInstance().get_connection()


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            register_user(conn(), request.form["name"], request.form["email"],
                          request.form["password"],
                          role=request.form.get("role", "patient"),
                          phone=request.form.get("phone", ""),
                          specialization=request.form.get("specialization", ""),
                          chamber=request.form.get("chamber", ""))
            flash("Registration successful. Please log in.")
            return redirect(url_for("main.login"))
        except ValueError as exc:
            flash(str(exc))
    return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = authenticate(conn(), request.form["email"], request.form["password"])
        if user:
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            return redirect(url_for("main.dashboard"))
        flash("Invalid email or password.")
    return render_template("login.html")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.index"))


@bp.route("/doctors")
def doctors():
    spec = request.args.get("specialization", "")
    return render_template("doctors.html", doctors=search_doctors(conn(), spec))


@bp.route("/book/<int:doctor_id>", methods=["GET", "POST"])
def book(doctor_id):
    if "user_id" not in session:
        return redirect(url_for("main.login"))
    doctor = conn().execute("SELECT * FROM users WHERE id = ?", (doctor_id,)).fetchone()
    result = None
    if request.method == "POST":
        notifier = NotificationService()
        notifier.subscribe(EmailNotifier(conn()))
        notifier.subscribe(SMSNotifier(conn()))
        result = book_appointment(conn(), session["user_id"], doctor_id,
                                  request.form["date"], request.form["time_slot"],
                                  request.form["type"], notifier)
        flash(f"Booking result: {result.status}")
    return render_template("book.html", doctor=doctor, result=result)


@bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("main.login"))
    rows = conn().execute(
        "SELECT * FROM appointments WHERE patient_id = ? ORDER BY date",
        (session["user_id"],),
    ).fetchall()
    return render_template("dashboard.html", appointments=rows)
