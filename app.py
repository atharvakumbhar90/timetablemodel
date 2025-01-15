from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import Timetable, Timetable2, db, User
import sqlite3

app = Flask(__name__, template_folder='project/templates', static_folder='project/static')
app.secret_key = 'd12f95cbce7978dad69f16fa8eb13d116578cec1607058eee99ba2b46dc32778'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///timetable.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


@app.route('/')
def default_route():
    return redirect(url_for('login'))


# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['role'] = user.role
            session['username'] = user.username

            if user.role == 'student':
                session['class_type'] = 'class1' if user.username == 'student1' else 'class2'
                return redirect(url_for('student_dashboard'))
            elif user.role == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('admin_panel'))
        else:
            return render_template('login.html', message="Invalid credentials. Please try again.")

    return render_template('login.html')


# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# Student Dashboard
@app.route('/student')
def student_dashboard():
    if 'role' in session and session['role'] == 'student':
        class_type = session.get('class_type')
        table_name = 'timetable' if class_type == 'class1' else 'timetable2'

        connection = sqlite3.connect('instance/timetable.db')
        cursor = connection.cursor()
        query = f"""
        SELECT 
            {table_name}.time_slot,
            {table_name}.day_of_week,
            {table_name}.subject,
            user.username AS teacher_name
        FROM 
            {table_name}
        INNER JOIN 
            user
        ON 
            {table_name}.teacher_id = user.id;
        """
        cursor.execute(query)
        data = cursor.fetchall()
        connection.close()

        timetable = [
            {"time_slot": row[0], "day_of_week": row[1], "subject": row[2], "teacher_name": row[3]}
            for row in data
        ]

        return render_template("student_dashboard.html", timetable=timetable, class_type=class_type)

    return redirect(url_for('login'))


# Teacher Dashboard
@app.route('/teacher', methods=['GET', 'POST'])
def teacher_dashboard():
    if 'role' in session and session['role'] == 'teacher':
        teacher_id = session['user_id']

        def get_available_substitute(current_teacher_id, day_of_week, time_slot):
            substitutes = User.query.filter(User.role == 'teacher', User.id != current_teacher_id).all()
            for teacher in substitutes:
                if not check_teacher_clash(teacher.id, day_of_week, time_slot):
                    return teacher
            return None

        message = ""
        if request.method == 'POST':
            day = request.form.get('day')
            time_slot = request.form.get('time_slot')

            if 'mark_absent_day' in request.form:
                for timetable in [Timetable, Timetable2]:
                    entries = timetable.query.filter_by(teacher_id=teacher_id, day_of_week=day).all()
                    for entry in entries:
                        substitute = get_available_substitute(teacher_id, day, entry.time_slot)
                        if substitute:
                            entry.teacher_id = substitute.id
                            message = f"Absence marked successfully."
                        else:
                            message += f"No substitute available for {entry.time_slot} on {day}. "

            elif 'mark_absent_slot' in request.form:
                for timetable in [Timetable, Timetable2]:
                    entry = timetable.query.filter_by(teacher_id=teacher_id, day_of_week=day, time_slot=time_slot).first()
                    if entry:
                        substitute = get_available_substitute(teacher_id, day, time_slot)
                        if substitute:
                            entry.teacher_id = substitute.id
                            message = f"Absence handled successfully {substitute.username} will cover your class."
                        else:
                            message += f"No substitute available for {time_slot} on {day}. "

            db.session.commit()

        timetable = Timetable.query.filter_by(teacher_id=teacher_id).all()
        timetable_2 = Timetable2.query.filter_by(teacher_id=teacher_id).all()
        return render_template('teacher_dashboard.html', timetable=timetable, timetable_2=timetable_2, message=message)

    return redirect(url_for('login'))


# Admin Panel
@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if 'role' in session and session['role'] == 'admin':
        message = ""
        if request.method == 'POST':
            if 'add_teacher' in request.form:
                teacher_name = request.form['teacher_name']
                teacher_password = request.form['teacher_password']

                if User.query.filter_by(username=teacher_name, role='teacher').first():
                    message = f"Teacher {teacher_name} already exists."
                else:
                    new_teacher = User(username=teacher_name, password=teacher_password, role='teacher')
                    db.session.add(new_teacher)
                    db.session.commit()
                    message = "Teacher added successfully."

            elif 'remove_teacher' in request.form:
                teacher_id = request.form['teacher_id']

                teacher = User.query.filter_by(id=teacher_id, role='teacher').first()
                if teacher:
                    db.session.delete(teacher)
                    db.session.commit()
                    message = "Teacher removed successfully."

        teachers = User.query.filter_by(role='teacher').all()
        timetable = Timetable.query.all()
        timetable_2 = Timetable2.query.all()
        return render_template('admin_panel.html', teachers=teachers, timetable=timetable, timetable_2=timetable_2, message=message)

    return redirect(url_for('login'))

@app.route('/admin/class2', methods=['GET', 'POST'])
def admin_class2_timetable():
    if 'role' in session and session['role'] == 'admin':
        if request.method == 'POST':
            day = request.form['day']
            time_slot = request.form['time_slot']
            subject = request.form['subject']
            teacher_id = request.form['teacher']

            # Check for conflict in Class 2 (Timetable2)
            if check_teacher_clash(teacher_id, day, time_slot):
                flash(f"Teacher {teacher_id} is already assigned to a class at {time_slot} on {day}. Please choose a different slot.", 'error')
                return redirect(url_for('admin_class2_timetable'))

            timetable_entry = Timetable2.query.filter_by(day_of_week=day, time_slot=time_slot).first()
            if timetable_entry:
                timetable_entry.subject = subject
                timetable_entry.teacher_id = teacher_id
            else:
                new_entry = Timetable2(day_of_week=day, time_slot=time_slot, subject=subject, teacher_id=teacher_id)
                db.session.add(new_entry)

            db.session.commit()
            flash("Class 2 timetable updated successfully.", 'success')
            return redirect(url_for('admin_panel'))

        timetable2_entries = Timetable2.query.all()
        teachers = User.query.filter_by(role='teacher').all()
        return render_template('admin_class2_timetable.html', timetable2=timetable2_entries, teachers=teachers)

    return redirect(url_for('login'))

#CLASH
def check_teacher_clash(teacher_id, day_of_week, time_slot):
    # Check for existing clash in both timetables (Timetable and Timetable2)
    conflict_class1 = Timetable.query.filter_by(teacher_id=teacher_id, day_of_week=day_of_week, time_slot=time_slot).first()
    if conflict_class1:
        return True  # Clash found in Class 1 (Timetable)
    
    conflict_class2 = Timetable2.query.filter_by(teacher_id=teacher_id, day_of_week=day_of_week, time_slot=time_slot).first()
    if conflict_class2:
        return True  # Clash found in Class 2 (Timetable2)
    
    return False  # No clash

if __name__ == '__main__':
    app.run(debug=True)