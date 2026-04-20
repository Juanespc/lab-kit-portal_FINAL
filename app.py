from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import os

from database import (
    close_db,
    init_app,
    init_db,
    get_all_kits,
    create_damage_report,
    get_open_damage_reports,
    mark_report_solved
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey123")

init_app(app)

# Admin credentials
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "fau123")

# Initialize database
with app.app_context():
    init_db(seed=True)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/kits')
def kits():
    kits = get_all_kits()
    return render_template('student_kit.html', kits=kits)


@app.route('/request', methods=['GET', 'POST'])
def request_form():
    if request.method == 'POST':
        student_name = request.form.get('student_name')
        student_id = request.form.get('student_id')
        part_name = request.form.get('part_name')
        issue_type = request.form.get('issue_type')
        description = request.form.get('description')

        full_description = f"""
Student: {student_name} ({student_id})
Part: {part_name}
Issue: {issue_type}
Details: {description}
"""

        print("=== NEW REQUEST ===")
        print(full_description)

        # Temporary IDs for demo
        component_id = 1
        reported_by = 1

        create_damage_report(component_id, reported_by, full_description)

        return redirect(url_for('index'))

    return render_template('request_form.html')


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid username or password")

    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for('admin_login'))


@app.route('/admin')
@admin_required
def admin_dashboard():
    reports = get_open_damage_reports()
    return render_template('admin.html', reports=reports)


@app.route('/admin/solve/<int:report_id>', methods=['POST'])
@admin_required
def solve_report(report_id):
    mark_report_solved(report_id)
    return redirect(url_for('admin_dashboard'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)