from flask import Flask, render_template, redirect, request, url_for, session
from google.oauth2 import id_token
from google.auth.transport import requests
from google_auth_oauthlib.flow import Flow

app = Flask(__name__)
app.secret_key = "Arely's secret"

from datetime import timedelta
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)  # Adjust as needed

CLIENT_ID = '265023238074-14b0gggj86ft651p6ec521nkubt5srlc.apps.googleusercontent.com'
CLIENT_SECRET = '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'
REDIRECT_URI = 'http://localhost:5000/oauth2callback'


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/citas')
def booking():
    return render_template('booking.html')

@app.route('/login')
def login():
    # Set up the OAuth flow
    flow = Flow.from_client_secrets_file(
        'credentials.json',
        scopes=['openid', 'email'],
        redirect_uri=REDIRECT_URI
    )

    authorization_url, state = flow.authorization_url(prompt='consent')

    # Store the state so the callback can verify the auth response.
    session['oauth_state'] = state

    print("****** Redirecting to Google for login")
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    # Validate the OAuth response
    state = session.get('oauth_state')
    print("***** oauth_state from session:", state)

    flow = Flow.from_client_secrets_file(
        'credentials.json',
        scopes=['openid', 'email'],
        state=state,
        redirect_uri=REDIRECT_URI
    )

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Get user information
    id_info = id_token.verify_oauth2_token(flow.credentials.id_token, requests.Request(), CLIENT_ID)

    # Store user information in the session
    session['google_id'] = id_info['sub']
    session['email'] = id_info['email']

    # Redirect to the booking form or homepage.
    return redirect(url_for('citas'))

if __name__ == "__main__":
    app.run(debug=True, ssl_context=('cert.pem', 'key.pem'))
