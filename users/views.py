from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from markupsafe import Markup
from users.forms import RegisterForm, LoginForm
from models import User
from app import db
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
import bcrypt
import pyotp
import logging

users_blueprint = Blueprint('users', __name__, template_folder='templates')


@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        logging.warning('SECURITY - User registration [%s, %s]', form.username.data, request.remote_addr)
        new_user = User(username=form.username.data, password=form.password.data, role='user')
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('users.login'))
    return render_template('users/register.html', form=form)


@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if not session.get('authentication_attempts'):
        session['authentication_attempts'] = 0
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user \
                or not bcrypt.checkpw(form.password.data.encode('utf-8'), user.password) \
                or not pyotp.TOTP(user.pinkey).verify(form.pin.data):
            logging.warning('SECURITY - Invalid Login Attempt [%s, %s]', form.username.data, request.remote_addr)
            session['authentication_attempts'] += 1
            if session.get('authentication_attempts') >= 3:
                flash(Markup('Number of incorrect login attempts exceeded. Please click '
                             '<a href="/reset">here</a> to reset.'))
                return render_template('users/login.html')
            flash('Please check your login details and try again, {} login attempts remaining'
                  .format(3 - session.get('authentication_attempts')))
            return render_template('users/login.html', form=form)
        else:
            login_user(user)
            user.last_login = user.current_login
            user.current_login = datetime.now()
            db.session.add(user)
            db.session.commit()
            logging.warning('SECURITY - Log in [%s, %s, %s, %s]', current_user.id, current_user.username
                            , current_user.role, request.remote_addr)
            if current_user.role == 'user':
                return redirect(url_for('blog.blog'))
            if current_user.role == 'admin':
                return redirect(url_for('admin.admin'))
    return render_template('users/login.html', form=form)


@users_blueprint.route('/reset')
def reset():
    session['authentication_attempts'] = 0
    return redirect(url_for('users.login'))


@users_blueprint.route('/logout')
@login_required
def logout():
    logging.warning('SECURITY - Log Out [%s, %s, %s, %s]', current_user.id, current_user.username, current_user.role
                    , request.remote_addr)
    logout_user()
    return redirect(url_for('main.index'))
