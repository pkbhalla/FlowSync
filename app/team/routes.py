from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.team import team_bp
from app.models import User, Task

@team_bp.route('/', methods=['GET'])
@login_required
def index():
    users = User.query.all()
    for u in users:
        u.open_tasks = Task.query.filter(Task.assignee_id == u.id, Task.status == 'in_progress').count()
        total = Task.query.filter(Task.assignee_id == u.id).count()
        done = Task.query.filter(Task.assignee_id == u.id, Task.status == 'done').count()
        u.completion_rate = (done / total * 100) if total > 0 else 0
    return render_template('team/index.html', users=users)

@team_bp.route('/invite', methods=['POST'])
@login_required
def invite():
    if current_user.role != 'admin':
        flash('Only admins can invite new members', 'error')
        return redirect(url_for('team.index'))
    email = request.form.get('email')
    username = request.form.get('username')
    display_name = request.form.get('display_name')
    password = request.form.get('password')
    if User.query.filter_by(email=email).first():
        flash('Email already exists', 'error')
        return redirect(url_for('team.index'))
    user = User(
        email=email, username=username, display_name=display_name,
        avatar_initials=display_name[:2].upper() if display_name else 'US',
        avatar_color='#006494'
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    flash('User created', 'success')
    return redirect(url_for('team.index'))
