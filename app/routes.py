from app import app, db
from flask import render_template, request, flash, redirect, url_for
from .forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from .models import User
from werkzeug.urls import url_parse
import requests


@app.route('/', methods=['Get'])
def index():
    return render_template('index.html.j2')

@app.route('/properties', methods=['GET', 'POST'])
def properties():
    if request.method == 'POST':
        name = request.form.get('name')
        url = "https://pokeapi.co/api/v2/pokemon/" + f"{name.lower()}"
        response = requests.get(url)
        if response.ok:
            data = response.json()
            pokidata = {}
            pokidata = {
                'id': data['id'], 
                'name': data['name'].title(), 
                'weight': data['weight'], 
                'height': data['height'], 
                'types': data['types'], 
                'abilities': data['abilities'], 
                'stats': data['stats'],
                'default_sprite': data['sprites']['front_default'], 
                'shiny_sprite': data['sprites']['front_shiny']
            }
            return render_template('properties.html.j2', pokidata = pokidata)
        else:
            error_string = "Sorry Love, something went wrong."
            return render_template('properties.html.j2', error = error_string)
    error_string = "Please enter a Poki name or ID number."
    return render_template('properties.html.j2', error = error_string)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash ('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('index')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html.j2', title ='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for ('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You have been successfully registered!')
        return(redirect (url_for('login')))
    return render_template('register.html.j2', title = 'Register', form=form)