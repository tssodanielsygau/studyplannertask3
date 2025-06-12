#standard routes for the website, where the user can go to
from flask import Blueprint

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return "<p>Login Page</p>"

@auth.route('/logout')
def logout():
    return "<p>Logout Page</p>"

@auth.route('/sign-up')
def signup():
    return "<p>Signup Page</p>"
