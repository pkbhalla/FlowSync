from functools import wraps
from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.admin import admin_bp
from app.models import WhitelistInvitation, Project, User

def role_required(role):
    """Decorator: restrict route to users with a specific role."""
    def decorator(f):
        @wraps(f)
        @login_required
        def wrapper(*args, **kwargs):
            if current_user.role != role:
                abort(403)
            return f(*args, **kwargs)
        return wrapper
    return decorator

@admin_bp.route('/')
@role_required('admin')
def index():
    invites = WhitelistInvitation.query.order_by(WhitelistInvitation.created_at.desc()).all()
    projects = Project.query.all()
    return render_template('admin/index.html', invites=invites, projects=projects)

@admin_bp.route('/invite', methods=['POST'])
@role_required('admin')
def create_invite():
    email = request.form.get('email', '').strip().lower()
    project_id = request.form.get('project_id')
    if not email or not project_id:
        flash('Email and project are required', 'error')
        return redirect(url_for('admin.index'))
    existing = WhitelistInvitation.query.filter_by(email=email).first()
    if existing:
        flash(f'{email} is already invited', 'warning')
        return redirect(url_for('admin.index'))
    invite = WhitelistInvitation(
        email=email,
        project_id=int(project_id),
        invited_by=current_user.id
    )
    db.session.add(invite)
    db.session.commit()
    flash(f'Invite created for {email}', 'success')
    return redirect(url_for('admin.index'))
