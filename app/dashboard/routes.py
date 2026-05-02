from flask import render_template
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
from app.dashboard import dashboard_bp
from app.models import Task, Project, ActivityLog, User, db

@dashboard_bp.route('/')
@login_required
def index():
    now = datetime.now().date()
    start_of_week = now - timedelta(days=now.weekday())

    total_tasks = Task.query.count()
    in_progress = Task.query.filter_by(status='in_progress').count()
    overdue = Task.query.filter(Task.due_date < now, Task.status != 'done').count()
    completed_this_week = Task.query.filter(Task.status == 'done', Task.completed_at >= start_of_week).count()

    activity_feed = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(20).all()
    
    my_tasks = Task.query.filter_by(assignee_id=current_user.id).filter(Task.status != 'done').order_by(Task.due_date).limit(10).all()
    
    projects = Project.query.limit(3).all()

    return render_template('dashboard/index.html',
                           total_tasks=total_tasks,
                           in_progress=in_progress,
                           overdue=overdue,
                           completed_this_week=completed_this_week,
                           activity_feed=activity_feed,
                           my_tasks=my_tasks,
                           projects=projects)
