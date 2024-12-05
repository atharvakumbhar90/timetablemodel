from googleapiclient.discovery import build
from google.oauth2 import service_account
import datetime

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'service_account.json'  # Replace with your service account file path

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('calendar', 'v3', credentials=credentials)

def check_teacher_availability(calendar_id, time_slot, day_of_week):
    """
    Check if a teacher is available in their Google Calendar.
    """
    # Convert day_of_week and time_slot to a specific datetime range
    day_of_week_to_date = {
        'Monday': 0,
        'Tuesday': 1,
        'Wednesday': 2,
        'Thursday': 3,
        'Friday': 4,
        'Saturday': 5
    }
    now = datetime.datetime.utcnow()
    start_of_week = now - datetime.timedelta(days=now.weekday())
    day_date = start_of_week + datetime.timedelta(days=day_of_week_to_date[day_of_week])

    time_slot_start = datetime.datetime.strptime(time_slot.split('-')[0], '%H:%M').time()
    time_slot_end = datetime.datetime.strptime(time_slot.split('-')[1], '%H:%M').time()
    
    start_time = datetime.datetime.combine(day_date, time_slot_start)
    end_time = datetime.datetime.combine(day_date, time_slot_end)

    events_result = service.events().list(calendarId=calendar_id, timeMin=start_time.isoformat() + 'Z',
                                          timeMax=end_time.isoformat() + 'Z', singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        return True
    return False

def mark_absent(calendar_id, time_slot, day_of_week):
    """
    Mark a teacher as absent in their Google Calendar.
    """
    # Convert day_of_week and time_slot to a specific datetime range
    day_of_week_to_date = {
        'Monday': 0,
        'Tuesday': 1,
        'Wednesday': 2,
        'Thursday': 3,
        'Friday': 4,
        'Saturday': 5
    }
    now = datetime.datetime.utcnow()
    start_of_week = now - datetime.timedelta(days=now.weekday())
    day_date = start_of_week + datetime.timedelta(days=day_of_week_to_date[day_of_week])

    time_slot_start = datetime.datetime.strptime(time_slot.split('-')[0], '%H:%M').time()
    time_slot_end = datetime.datetime.strptime(time_slot.split('-')[1], '%H:%M').time()
    
    start_time = datetime.datetime.combine(day_date, time_slot_start)
    end_time = datetime.datetime.combine(day_date, time_slot_end)

    event = {
        'summary': 'Absent',
        'description': 'Marked absent automatically',
        'start': {
            'dateTime': start_time.isoformat() + 'Z',
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_time.isoformat() + 'Z',
            'timeZone': 'UTC',
        },
    }

    service.events().insert(calendarId=calendar_id, body=event).execute()
