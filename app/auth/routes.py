from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app import db
from app.auth import auth_bp
from app.models import User

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_password(password):
            flash('Invalid email or password', 'error')
            return redirect(url_for('auth.login'))
        login_user(user, remember=True)
        return redirect(url_for('dashboard.index'))
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        display_name = request.form.get('display_name')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
            flash('Email or username already registered', 'error')
            return redirect(url_for('auth.register'))
            
        user = User(
            email=email,
            username=username,
            display_name=display_name,
            avatar_initials=display_name[:2].upper() if display_name else 'US',
            avatar_color='#01696f'
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=True)
        return redirect(url_for('dashboard.index'))
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
