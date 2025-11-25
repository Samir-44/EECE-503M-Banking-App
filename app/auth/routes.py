from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import auth_bp
from .forms import RegisterForm, LoginForm, ProfileForm
from ..models import User
from ..extensions import db
from ..security import log_event, record_failed_login, is_locked_out


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('banking.dashboard'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(full_name=form.full_name.data.strip(), email=form.email.data.lower().strip(), phone=form.phone.data)
        user.set_password(form.password.data)
        user.role = 'customer'
        db.session.add(user)
        db.session.commit()
        log_event('REGISTER_SUCCESS', f'user_id={user.id}')
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('banking.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        key = form.email.data.lower().strip() or request.remote_addr
        if is_locked_out(key):
            log_event('LOGIN_LOCKOUT', f'key={key}')
            flash('Too many failed attempts. Try again later.', 'danger')
            return render_template('auth/login.html', form=form)

        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            log_event('LOGIN_SUCCESS', f'user_id={user.id}')
            return redirect(url_for('banking.dashboard'))
        else:
            record_failed_login(key)
            log_event('LOGIN_FAILURE', f'email={form.email.data}')
            flash('Invalid email or password', 'danger')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    log_event('LOGOUT', f'user_id={current_user.id}')
    logout_user()
    flash('Logged out', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data.strip()
        current_user.phone = form.phone.data
        db.session.commit()
        log_event('USER_UPDATED', f'user_id={current_user.id}')
        flash('Profile updated', 'success')
        return redirect(url_for('auth.profile'))
    return render_template('auth/profile.html', form=form)
