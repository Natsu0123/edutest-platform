from datetime import datetime, timedelta

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db
from app.forms import LoginForm, RegisterForm
from app.models import User
from app.utils.i18n import LANGUAGES, translate as _t


auth_bp = Blueprint('auth', __name__)
MAX_LOGIN_ATTEMPTS = 5
LOCK_MINUTES = 10


@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_staff:
            return redirect(url_for('admin.admin_dashboard'))
        return redirect(url_for('student.dashboard'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/set-language/<lang_code>')
def set_language(lang_code):
    if lang_code in LANGUAGES:
        session['language'] = lang_code
        flash(_t('lang.changed'), 'success')
    return redirect(request.referrer or url_for('auth.index'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_staff:
            return redirect(url_for('admin.admin_dashboard'))
        return redirect(url_for('student.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        if is_login_locked():
            flash(_t('auth.login_locked', minutes=LOCK_MINUTES), 'danger')
            return render_template('auth/login.html', form=form)

        user = User.query.filter_by(username=form.username.data.strip()).first()
        if user and user.check_password(form.password.data):
            clear_login_attempts()
            login_user(user)
            flash(_t('auth.login_success'), 'success')
            if user.is_staff:
                return redirect(url_for('admin.admin_dashboard'))
            return redirect(url_for('student.dashboard'))

        register_failed_attempt()
        flash(_t('auth.login_error'), 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.admin_dashboard'))
        return redirect(url_for('student.dashboard'))

    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        if User.query.filter_by(username=username).first():
            flash(_t('auth.user_exists'), 'danger')
            return render_template('auth/register.html', form=form)

        user = User(username=username, full_name=form.full_name.data.strip(), role='student')
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash(_t('auth.register_success'), 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash(_t('auth.logout_success'), 'info')
    return redirect(url_for('auth.login'))



def is_login_locked() -> bool:
    expires_at = session.get('login_lock_until')
    if not expires_at:
        return False
    try:
        lock_until = datetime.fromisoformat(expires_at)
    except ValueError:
        clear_login_attempts()
        return False
    if datetime.utcnow() >= lock_until:
        clear_login_attempts()
        return False
    return True



def register_failed_attempt() -> None:
    attempts = session.get('login_attempts', 0) + 1
    session['login_attempts'] = attempts
    if attempts >= MAX_LOGIN_ATTEMPTS:
        session['login_lock_until'] = (datetime.utcnow() + timedelta(minutes=LOCK_MINUTES)).isoformat()



def clear_login_attempts() -> None:
    session.pop('login_attempts', None)
    session.pop('login_lock_until', None)
