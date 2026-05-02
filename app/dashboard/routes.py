from flask import render_template
from flask_login import login_required, current_user
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta, timezone
from app.dashboard import dashboard_bp
from app.models import Task, Project, ActivityLog, User, db

@dashboard_bp.route('/')
@login_required
def index():
    now = datetime.now().date()
    start_of_week = now - timedelta(days=now.weekday())

    # Single query for all KPI counts
    counts = db.session.query(
        func.count(Task.id),
        func.count(Task.id).filter(Task.status == 'in_progress'),
        func.count(Task.id).filter(Task.due_date < now, Task.status != 'done'),
        func.count(Task.id).filter(Task.status == 'done', Task.completed_at >= datetime.combine(start_of_week, datetime.min.time()))
    ).first()

    total_tasks, in_progress, overdue, completed_this_week = counts

    # Eager-load user for activity feed to avoid N+1
    activity_feed = (ActivityLog.query
        .options(joinedload(ActivityLog.user))
        .order_by(ActivityLog.created_at.desc())
        .limit(20).all())

    # Eager-load project for tasks
    my_tasks = (Task.query
        .options(joinedload(Task.project))
        .filter_by(assignee_id=current_user.id)
        .filter(Task.status != 'done')
        .order_by(Task.due_date)
        .limit(10).all())

    projects = Project.query.limit(5).all()

    return render_template('dashboard/index.html',
                           total_tasks=total_tasks,
                           in_progress=in_progress,
                           overdue=overdue,
                           completed_this_week=completed_this_week,
                           activity_feed=activity_feed,
                           my_tasks=my_tasks,
                           projects=projects)
