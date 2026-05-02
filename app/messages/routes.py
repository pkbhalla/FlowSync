import json
from flask import render_template, request, jsonify, Response, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.messages import messages_bp
from app.models import Channel, Message, User
import queue
import threading

# Simple pubsub for SSE
clients = []
clients_lock = threading.Lock()

def notify_clients(data):
    with clients_lock:
        for q in clients:
            q.put(data)

@messages_bp.route('/')
@login_required
def index():
    channels = Channel.query.all()
    if not channels:
        gen = Channel(name='general', description='General discussion', created_by=current_user.id)
        db.session.add(gen)
        db.session.commit()
        channels = [gen]
    return redirect(url_for('messages.channel', channel_id=channels[0].id))

@messages_bp.route('/<int:channel_id>')
@login_required
def channel(channel_id):
    channels = Channel.query.all()
    active_channel = Channel.query.get_or_404(channel_id)
    msgs = active_channel.messages.order_by(Message.created_at.asc()).limit(50).all()
    users = User.query.all()
    return render_template('messages/index.html', channels=channels, active_channel=active_channel, messages=msgs, users=users)

@messages_bp.route('/<int:channel_id>/send', methods=['POST'])
@login_required
def send(channel_id):
    data = request.json
    content = data.get('content')
    if not content:
        return jsonify({'error': 'No content'}), 400
    msg = Message(
        channel_id=channel_id,
        sender_id=current_user.id,
        content=content
    )
    db.session.add(msg)
    db.session.commit()
    payload = {
        'id': msg.id,
        'channel_id': msg.channel_id,
        'content': msg.content,
        'created_at': msg.created_at.isoformat(),
        'sender': {
            'id': current_user.id,
            'display_name': current_user.display_name,
            'avatar_initials': current_user.avatar_initials,
            'avatar_color': current_user.avatar_color
        }
    }
    notify_clients(json.dumps(payload))
    return jsonify({'success': True})

@messages_bp.route('/stream')
@login_required
def stream():
    def event_stream():
        q = queue.Queue()
        with clients_lock:
            clients.append(q)
        try:
            while True:
                data = q.get()
                yield f"data: {data}\n\n"
        finally:
            with clients_lock:
                clients.remove(q)
    return Response(event_stream(), mimetype="text/event-stream")

@messages_bp.route('/channels/create', methods=['POST'])
@login_required
def create_channel():
    name = request.form.get('name')
    is_private = request.form.get('is_private') == 'true'
    ch = Channel(name=name, is_private=is_private, created_by=current_user.id)
    db.session.add(ch)
    db.session.commit()
    flash('Channel created', 'success')
    return redirect(url_for('messages.channel', channel_id=ch.id))
