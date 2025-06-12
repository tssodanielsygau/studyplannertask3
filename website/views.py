#standard routes for the website, where the user can go to
from flask import Blueprint

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return "<h1>Home Page</h1>"
