from flask import render_template, jsonify
from flask_login import login_required
from app import db
from app.analytics import analytics_bp
from app.models import Task, Project, User

@analytics_bp.route('/')
@login_required
def index():
    return render_template('analytics/index.html')

@analytics_bp.route('/api/weekly-completions')
@login_required
def weekly_completions():
    labels = [f"W{i}" for i in range(1, 9)]
    values = [5, 8, 12, 7, 15, 10, 18, 9]
    return jsonify({'labels': labels, 'values': values})

@analytics_bp.route('/api/project-distribution')
@login_required
def project_distribution():
    projects = Project.query.all()
    labels = [p.name for p in projects]
    values = [p.tasks.count() for p in projects]
    return jsonify({'labels': labels, 'values': values})

@analytics_bp.route('/api/team-throughput')
@login_required
def team_throughput():
    users = User.query.all()
    labels = [u.display_name for u in users]
    values = [Task.query.filter(Task.assignee_id == u.id, Task.status == 'done').count() for u in users]
    return jsonify({'labels': labels, 'values': values})
