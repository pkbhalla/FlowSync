from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.projects import projects_bp
from app.models import Project, ProjectMember, User, Milestone, Task

@projects_bp.route('/', methods=['GET'])
@login_required
def index():
    projects = Project.query.all()
    users = User.query.all()
    return render_template('projects/index.html', projects=projects, users=users)

@projects_bp.route('/create', methods=['POST'])
@login_required
def create():
    name = request.form.get('name')
    description = request.form.get('description')
    color = request.form.get('color', '#01696f')
    
    project = Project(
        name=name,
        description=description,
        color=color,
        created_by=current_user.id
    )
    db.session.add(project)
    db.session.commit()
    
    # Add creator as lead
    pm = ProjectMember(project_id=project.id, user_id=current_user.id, role='lead')
    db.session.add(pm)
    db.session.commit()
    
    flash('Project created successfully', 'success')
    return redirect(url_for('projects.index'))

@projects_bp.route('/<int:id>', methods=['GET'])
@login_required
def detail(id):
    project = Project.query.get_or_404(id)
    users = User.query.all()
    # counts
    task_counts = {
        'backlog': project.tasks.filter_by(status='backlog').count(),
        'in_progress': project.tasks.filter_by(status='in_progress').count(),
        'in_review': project.tasks.filter_by(status='in_review').count(),
        'done': project.tasks.filter_by(status='done').count(),
    }
    return render_template('projects/detail.html', project=project, users=users, task_counts=task_counts)

@projects_bp.route('/<int:id>/add-member', methods=['POST'])
@login_required
def add_member(id):
    project = Project.query.get_or_404(id)
    user_id = request.form.get('user_id')
    role = request.form.get('role', 'member')
    
    if user_id:
        existing = ProjectMember.query.filter_by(project_id=id, user_id=user_id).first()
        if not existing:
            pm = ProjectMember(project_id=id, user_id=user_id, role=role)
            db.session.add(pm)
            db.session.commit()
            flash('Member added', 'success')
        else:
            flash('User is already a member', 'info')
            
    return redirect(url_for('projects.detail', id=id))
