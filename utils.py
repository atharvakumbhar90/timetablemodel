from models import Teacher, Timetable

def get_free_teacher(time_slot):
    # Logic to get a free teacher
    free_teachers = Teacher.query.filter_by(availability=True).all()
    for teacher in free_teachers:
        # Check if teacher is free at the time_slot
        pass
    return free_teacher

def send_notification(teacher):
    # Logic to send notification
    pass
