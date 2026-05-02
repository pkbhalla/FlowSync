from flask import jsonify, request
from flask_login import login_required, current_user
from app.api import api_bp
from app.models import Task, Project, User, ActivityLog, Message, Channel
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

# ─── Phase 4: Gemini AI Endpoints ───

@api_bp.route('/ai/breakdown-task', methods=['POST'])
@login_required
def ai_breakdown_task():
    """Use Gemini to break a task into subtasks."""
    from app.ai import generate_subtasks
    data = request.json or {}
    task_id = data.get('task_id')
    if not task_id:
        return jsonify({'error': 'task_id required'}), 400
    task = Task.query.get_or_404(task_id)
    subtask_defs = generate_subtasks(task.title, task.description or '')
    if not subtask_defs:
        return jsonify({'error': 'AI not configured or generation failed'}), 503
    created = []
    for sd in subtask_defs:
        st = Task(
            title=sd.get('title', 'Subtask'),
            description=sd.get('description', ''),
            project_id=task.project_id,
            reporter_id=current_user.id,
            assignee_id=task.assignee_id,
            parent_task_id=task.id,
            priority=task.priority,
            status='backlog',
        )
        db.session.add(st)
        created.append(st)
    db.session.commit()
    return jsonify({
        'success': True,
        'parent_task_id': task.id,
        'subtasks': [{'id': s.id, 'title': s.title, 'description': s.description} for s in created]
    })

@api_bp.route('/ai/summarize-chat/<int:channel_id>')
@login_required
def ai_summarize_chat(channel_id):
    """Summarize the last 50 messages in a channel using Gemini."""
    from app.ai import summarize_chat
    channel = Channel.query.get_or_404(channel_id)
    msgs = channel.messages.order_by(Message.created_at.desc()).limit(50).all()
    msgs.reverse()
    message_list = [{'sender': m.sender.display_name, 'content': m.content} for m in msgs]
    if not message_list:
        return jsonify({'summary': 'No messages in this channel.'})
    summary = summarize_chat(message_list)
    return jsonify({'summary': summary, 'message_count': len(message_list)})

# ─── Phase 6: Tour completion ───

@api_bp.route('/users/finish-tour', methods=['POST'])
@login_required
def finish_tour():
    current_user.has_seen_tour = True
    db.session.commit()
    return jsonify({'success': True})
