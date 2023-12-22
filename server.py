from flask import Flask, render_template, request, flash, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TimeField, ValidationError
from wtforms.validators import DataRequired
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials

import os
import re
import uuid
import datetime

app = Flask(__name__)
app.secret_key = "Balu's secret"  # Change this to a secure secret key.

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
        if not super().validate():
            flash("Corrige los errores por favor.")
            return False
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

appointments = []

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
    appointments.append(appointment_details)  # Store appointment details.
    send_to_google_calendar(appointment_details)  # Call a function to send the details to the Google Calendar.
    return render_template('booking_confirmation.html', details=appointment_details)

# Function to send appointment details to Google Calendar
def send_to_google_calendar(details):
    # Check if both date and time components are present
    if 'date' in details and 'time' in details and details['date'] and details['time']:
        # Combine date and time strings into a single datetime object
        datetime_str = f"{details['date']} {details['time']}"
        details['appointment_datetime'] = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')

        event = {
            'summary': 'Appointment',
            'description': f"Name: {details['name']}\nEmail: {details['email']}\nPhone: {details['phone']}\nGuest ID: {details['guest_id']}",
            'start': {
                'dateTime': details['appointment_datetime'].isoformat(),
                'timeZone': 'America/Los_Angeles', # Pacific Time Zone
            },
            'end': {
                'dateTime': (details['appointment_datetime'] + datetime.timedelta(hours=1.5)).isoformat(),
                'timeZone': 'America/Los_Angeles',
            },
        }
        service = get_google_calendar_service()
        service.events().insert(calendarId=DENTIST_CALENDAR_ID, body=event).execute()
    else:
        print("-------------- Error: Date or time component is missing. ---------------")


def get_google_calendar_service():
    # Use a service account for server-to-server authentication
    credentials = Credentials.from_service_account_file('credentials.json', scopes=['https://www.googleapis.com/auth/calendar'])
    # Create the Google Calendar service
    service = build('calendar', 'v3', credentials=credentials)
    return service



if __name__ == '__main__':
    app.run(debug=True)
