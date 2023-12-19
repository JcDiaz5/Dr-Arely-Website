from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TimeField
from wtforms.validators import DataRequired
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials

import os
import uuid
import datetime

app = Flask(__name__)
app.secret_key = "Balu's secret"  # Change this to a secure secret key.

DENTIST_CALENDAR_ID = 'dra-arely-s-website@dental-website-1116.iam.gserviceaccount.com'

class BookingForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    time = TimeField('Time', validators=[DataRequired()])

@app.route('/')
def home():
    return render_template('home.html')

appointments = []

@app.route('/book', methods=['GET', 'POST'])
def book():
    form = BookingForm()

    if request.method == 'POST':
        guest_id = str(uuid.uuid4())
        appointment_details = {
            'name': request.form['name'],
            'email': request.form['email'],
            'date': request.form['date'],
            'time': request.form['time'],
            'guest_id': guest_id
        }

        # Store appointment details.
        appointments.append(appointment_details)

        # Call a function to send the details to the Google Calendar.
        send_to_google_calendar(appointment_details)

        return render_template('booking_confirmation.html', details=appointment_details)

    return render_template('booking_form.html', form=form)

# Function to send appointment details to Google Calendar
def send_to_google_calendar(details):
    # Combine date and time strings into a single datetime object
    datetime_str = f"{details['date']} {details['time']}"
    details['appointment_datetime'] = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')


    # Adjust the start and end times accordingly
    event = {
        'summary': 'Appointment',
        'description': f"Name: {details['name']}\nEmail: {details['email']}\nDate: {details['date']}\nTime: {details['time']}\nGuest ID: {details['guest_id']}",
    }

    service = get_google_calendar_service()
    service.events().insert(calendarId=DENTIST_CALENDAR_ID, body=event).execute()
    print('############## Send to calendar is working #############', event)

def get_google_calendar_service():
    # Use a service account for server-to-server authentication
    credentials = Credentials.from_service_account_file('credentials.json', scopes=['https://www.googleapis.com/auth/calendar'])

    # Create the Google Calendar service
    service = build('calendar', 'v3', credentials=credentials)

    print('*********** Get Calendar is working ***********')
    return service

if __name__ == '__main__':
    app.run(debug=True)
