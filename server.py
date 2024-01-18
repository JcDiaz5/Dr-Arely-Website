from flask import Flask, render_template, request, flash, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TimeField, ValidationError
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

import os
import re
import uuid
import json
import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default_secret_key")

credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_PATH', 'credentials.json')

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
DENTIST_CALENDAR_ID = '1d157f9d7c9ad6fa4202bd92820539282e8f0799df30507ebcede6589ff20881@group.calendar.google.com'


class BookingForm(FlaskForm):
    name = StringField('name')
    email = StringField('email')
    phone = StringField('phone')
    date = DateField('date')
    time = TimeField('time')

    # Validations for booking form
    def validate(self):
        if len(self.name.data) < 2:
            flash("Nombre debe contener al menos 2 letras.")
            return False
        if not EMAIL_REGEX.match(self.email.data):
            flash("Email invalido!")
            return False
        if not self.phone.data.isdigit() or len(self.phone.data) != 10:
            flash("Teléfono debe contener exactamente 10 números.")
            return False
        if not self.date.data:
            flash("La fecha es obligatoria.")
            return False
        if not self.time.data:
            flash("La hora es obligatoria.")
            return False
        return True

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/booking_form')
def booking_form():
    form = BookingForm()
    return render_template('booking_form.html', form=form)
appointment = []

@app.route('/book', methods=['GET', 'POST'])
def book():
    form = BookingForm()
    if not form.validate():
        return redirect('/booking_form')
    guest_id = str(uuid.uuid4())
    appointment_details = {
        'name': form.name.data,
        'email': form.email.data,
        'phone': form.phone.data,
        'date': form.date.data,
        'time': form.time.data,
        'guest_id': guest_id
    }
    appointment.clear() # Clear list from previous appointment.
    appointment.append(appointment_details)
    print('####', appointment)
    send_to_google_calendar(appointment_details) 
    return redirect('/appointment')

@app.route('/appointment')
def appointment_confirmation():
    details = appointment
    return render_template('booking_confirmation.html', details=details)

def send_to_google_calendar(details):
    if 'date' in details and 'time' in details and details['date'] and details['time']:

        datetime_str = f"{details['date']} {details['time']}"
        print(f"*** {details['date']} {details['time']} ***")
        details['appointment_datetime'] = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        print(f".... Date and Time (string): {details['appointment_datetime']} ....")

# __________________________________DO NOT ERASE CODE, PENDING OVERLAP BOOKING VALIDATIONS!________________________________
        # Checking for conflicts with existing events
    # if has_conflict(details):
    #     flash("¡Conflicto de citas! Por favor, elija otra hora o fecha.")
    #     return redirect('/booking_form')
    # else:
# ____________________________________TAB OVER THE BOTTOM CODE___________________________________________
    event = {
        'summary': f"Px(web) {details['name']}",
        'description': f"Name: {details['name']}\nEmail: {details['email']}\nPhone: {details['phone']}\nGuest ID: {details['guest_id']}",
        'start': {
            'dateTime': details['appointment_datetime'].isoformat(),
            'timeZone': 'America/Los_Angeles', # Pacific Time Zone
        },
        'end': {
            'dateTime': (details['appointment_datetime'] + datetime.timedelta(hours=2)).isoformat(),
            'timeZone': 'America/Los_Angeles',
        },
    }
    service = get_google_calendar_service()
    service.events().insert(calendarId=DENTIST_CALENDAR_ID, body=event).execute()
    print("-------------- Event created successfully ---------------")


# __________________________________DO NOT ERASE CODE, PENDING OVERLAP BOOKING VALIDATIONS!________________________________

# def is_conflict(new_start, new_end, existing_start, existing_end):
#     conflict = new_start < existing_end and new_end > existing_start
#     return conflict

# def has_conflict(new_details):

#     service = get_google_calendar_service()

#     if not ('appointment_datetime' in new_details and new_details['appointment_datetime']):
#         print("Error: Invalid date or time component.")
#         return False
    
#     print(f"Checking for conflicts in the time range: {new_details['appointment_datetime']} - {new_details['appointment_datetime'] + datetime.timedelta(hours=2)}")
#     print(f"timeMin: {new_details['appointment_datetime'].isoformat()}")
#     print(f"timeMax: {(new_details['appointment_datetime'] + datetime.timedelta(hours=2)).isoformat()}")

#     events_result = (
#         service.events()
#         .list(
#             calendarId=DENTIST_CALENDAR_ID,
#             timeMin=new_details['appointment_datetime'].isoformat(),
#             timeMax=(new_details['appointment_datetime'] + datetime.timedelta(hours=2)).isoformat(),
#             singleEvents=True,
#             orderBy='startTime',
#         ).execute()
#     )
#     print('++++++ Events Result:', events_result)

#     existing_events = events_result.get('items', [])

#     # Check for conflicts with existing events
#     for existing_event in existing_events:
#         print(f"......... {existing_event} .........")
#         try:
#             existing_start = datetime.datetime.fromisoformat(existing_event['start']['dateTime'])
#             existing_end = datetime.datetime.fromisoformat(existing_event['end']['dateTime'])
#         except ValueError as e:
#             print(f"Error processing existing event: {e}")
#             continue  # Skip this event and move to the next one
        
#         if is_conflict(
#                 new_details['appointment_datetime'],
#                 new_details['appointment_datetime'] + datetime.timedelta(hours=2),
#                 existing_start,
#                 existing_end
#         ):
#             print(f"Time range in API request: {new_details['appointment_datetime']} - {new_details['appointment_datetime'] + datetime.timedelta(hours=2)}")
#             return True

#     return False


def get_google_calendar_service():
    # Use a service account for server-to-server authentication
    credentials = Credentials.from_service_account_file('credentials.json', scopes=['https://www.googleapis.com/auth/calendar'])
    # Create the Google Calendar service
    service = build('calendar', 'v3', credentials=credentials)
    print('........Get calendar is working...............')
    return service


from server import app

if __name__ == '__main__':
    app.run()
