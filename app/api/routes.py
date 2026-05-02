from flask import jsonify, request
from flask_login import login_required, current_user
from app.api import api_bp
from app.models import Task, Project, User, ActivityLog
from app import db

@api_bp.route('/tasks')
@login_required
def get_tasks():
    project_id = request.args.get('project_id')
    status = request.args.get('status')
    assignee_id = request.args.get('assignee_id')
    
    query = Task.query
    if project_id: query = query.filter_by(project_id=project_id)
    if status: query = query.filter_by(status=status)
    if assignee_id: query = query.filter_by(assignee_id=assignee_id)
    
    tasks = query.all()
    return jsonify([t.to_dict() for t in tasks])

@api_bp.route('/users')
@login_required
def get_users():
    users = User.query.all()
    return jsonify([u.to_dict() for u in users])

@api_bp.route('/projects')
@login_required
def get_projects():
    projects = Project.query.all()
    return jsonify([{'id': p.id, 'name': p.name, 'color': p.color} for p in projects])

@api_bp.route('/activity', methods=['POST'])
@login_required
def log_activity():
    data = request.json
    log = ActivityLog(
        user_id=current_user.id,
        action_type=data.get('action_type'),
        entity_type=data.get('entity_type'),
        entity_id=data.get('entity_id'),
        metadata_=data.get('metadata', {})
    )
    db.session.add(log)
    db.session.commit()
    return jsonify({'success': True})
