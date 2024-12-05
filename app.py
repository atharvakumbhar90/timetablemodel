from flask import Flask, render_template, request, redirect, url_for
from models import db, Teacher, Timetable
from utils import get_free_teacher, send_notification
from google_calendar import mark_absent

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///college_schedule.db'
db.init_app(app)

@app.route('/')
def index():
    timetable = Timetable.query.all()
    return render_template('view_timetable.html', timetable=timetable)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        # Handle timetable input
        pass
    return render_template('admin.html')

@app.route('/mark_absent/<int:teacher_id>/<int:time_slot>', methods=['POST'])
def mark_absent_route(teacher_id, time_slot):
    mark_absent(teacher_id, time_slot)
    free_teacher = get_free_teacher(time_slot)
    if free_teacher:
        send_notification(free_teacher)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
