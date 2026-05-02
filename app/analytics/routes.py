from flask import render_template, jsonify
from flask_login import login_required
from sqlalchemy import func
from datetime import datetime, timezone, timedelta
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
    today = datetime.now(timezone.utc).date()
    labels = []
    values = []
    for i in range(7, -1, -1):
        week_start = today - timedelta(days=today.weekday()) - timedelta(weeks=i)
        week_end = week_start + timedelta(days=7)
        count = Task.query.filter(
            Task.status == 'done',
            Task.completed_at >= datetime.combine(week_start, datetime.min.time()),
            Task.completed_at < datetime.combine(week_end, datetime.min.time())
        ).count()
        labels.append(f"W{8 - i}")
        values.append(count)
    return jsonify({'labels': labels, 'values': values})

@analytics_bp.route('/api/project-distribution')
@login_required
def project_distribution():
    rows = (
        db.session.query(Project.name, func.count(Task.id))
        .outerjoin(Task, Task.project_id == Project.id)
        .group_by(Project.id, Project.name)
        .all()
    )
    labels = [r[0] for r in rows]
    values = [r[1] for r in rows]
    return jsonify({'labels': labels, 'values': values})

@analytics_bp.route('/api/team-throughput')
@login_required
def team_throughput():
    rows = (
        db.session.query(User.display_name, func.count(Task.id))
        .outerjoin(Task, (Task.assignee_id == User.id) & (Task.status == 'done'))
        .group_by(User.id, User.display_name)
        .all()
    )
    labels = [r[0] for r in rows]
    values = [r[1] for r in rows]
    return jsonify({'labels': labels, 'values': values})
