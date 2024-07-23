from flask import Flask, request, render_template
import re
import requests

app = Flask(__name__)

COMMON_PASSWORDS_URL = 'https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-1000.txt'
common_passwords = set(requests.get(COMMON_PASSWORDS_URL).text.splitlines())

def is_password_strong(password):
    if len(password) < 10:
        return False
    if password in common_passwords:
        return False
    return True

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        password = request.form['password']
        if is_password_strong(password):
            return render_template('welcome.html', password=password)
        else:
            return render_template('home.html', error='Password does not meet the requirements.')
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')