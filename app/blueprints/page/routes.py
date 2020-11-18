from flask import Blueprint, render_template, request

page = Blueprint('page', __name__, template_folder='templates')


@page.route('/')
def index():
    return render_template('index.html')


@page.route('/applications', methods=['GET', 'POST'])
def applications():
    if request.method == 'POST':
        return "POST REQUEST RECEIVED"

    return "GET REQUEST RECEIVED"
