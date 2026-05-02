from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timezone
from app import db
from app.tasks import tasks_bp
from app.models import Task, Project, User, ActivityLog

@tasks_bp.route('/', methods=['GET'])
@login_required
def index():
    tasks = Task.query.all()
    projects = Project.query.all()
    users = User.query.all()
    
    # Group tasks
    backlog = [t for t in tasks if t.status == 'backlog']
    in_progress = [t for t in tasks if t.status == 'in_progress']
    in_review = [t for t in tasks if t.status == 'in_review']
    done = [t for t in tasks if t.status == 'done']
    
    return render_template('tasks/board.html',
                           backlog=backlog, in_progress=in_progress,
                           in_review=in_review, done=done,
                           projects=projects, users=users)

@tasks_bp.route('/create', methods=['POST'])
@login_required
def create():
    data = request.json
    try:
        due_date = datetime.strptime(data.get('due_date'), '%Y-%m-%d').date() if data.get('due_date') else None
    except ValueError:
        due_date = None

    task = Task(
        title=data.get('title'),
        description=data.get('description'),
        project_id=data.get('project_id'),
        assignee_id=data.get('assignee_id') or None,
        reporter_id=current_user.id,
        status=data.get('status', 'backlog'),
        priority=data.get('priority', 'medium'),
        due_date=due_date
    )
    db.session.add(task)
    db.session.commit()
    
    log = ActivityLog(
        user_id=current_user.id,
        action_type='task_created',
        entity_type='task',
        entity_id=task.id,
        metadata_={'task_title': task.title}
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'success': True, 'task': task.to_dict()})

@tasks_bp.route('/<int:id>/update-status', methods=['POST'])
@login_required
def update_status(id):
    task = db.session.get(Task, id)
    if task is None:
        return jsonify({'error': 'Task not found'}), 404
    data = request.json
    new_status = data.get('status')
    if new_status in ['backlog', 'in_progress', 'in_review', 'done'] and task.status != new_status:
        old_status = task.status
        task.status = new_status
        if new_status == 'done':
            task.completed_at = datetime.now(timezone.utc)
        else:
            task.completed_at = None
        db.session.commit()
        
        log = ActivityLog(
            user_id=current_user.id,
            action_type='task_moved',
            entity_type='task',
            entity_id=task.id,
            metadata_={'task_title': task.title, 'old_status': old_status, 'new_status': new_status}
        )
        db.session.add(log)
        db.session.commit()
        
    return jsonify({'success': True})

@tasks_bp.route('/<int:id>', methods=['GET'])
@login_required
def get_task(id):
    task = db.session.get(Task, id)
    if task is None:
        return jsonify({'error': 'Task not found'}), 404
    return jsonify(task.to_dict())

@tasks_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_task(id):
    task = db.session.get(Task, id)
    if task is None:
        return jsonify({'error': 'Task not found'}), 404
    if task.reporter_id != current_user.id and current_user.role != 'admin':
        return jsonify({'error': 'Forbidden'}), 403
    db.session.delete(task)
    db.session.commit()
    return jsonify({'success': True})
