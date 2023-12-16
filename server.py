from flask import Flask, render_template
app = Flask(__name__)
app.secret_key = "My secret"

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/citas')
def booking():
    return render_template('booking.html')

if __name__ == "__main__":
    app.run(debug=True)