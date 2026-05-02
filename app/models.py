from datetime import datetime, timezone
import json
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.types import TypeDecorator, VARCHAR

from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# To support JSON on sqlite as fallback
class JSONEncodedDict(TypeDecorator):
    impl = VARCHAR
    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value
    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value
        
# Use dialect specific JSON if needed, or fallback
DbJSON = JSON().with_variant(JSONEncodedDict(), 'sqlite')

class ProjectMember(db.Model):
    __tablename__ = 'project_member'
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    role = db.Column(db.String(50), default='member') # lead, member
    joined_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class ChannelMember(db.Model):
    __tablename__ = 'channel_member'
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    joined_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_read_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    display_name = db.Column(db.String(128), nullable=False)
    avatar_initials = db.Column(db.String(3), nullable=False)
    avatar_color = db.Column(db.String(7), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='member') # admin/member/viewer
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_seen_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    timezone = db.Column(db.String(50), default='UTC')

    projects = relationship('Project', secondary='project_member', back_populates='members')
    channels = relationship('Channel', secondary='channel_member', back_populates='members')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'display_name': self.display_name,
            'avatar_initials': self.avatar_initials,
            'avatar_color': self.avatar_color,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_seen_at': self.last_seen_at.isoformat() if self.last_seen_at else None,
            'timezone': self.timezone
        }

class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), nullable=False)
    status = db.Column(db.String(50), default='planning') # planning/active/on_hold/completed
    start_date = db.Column(db.Date)
    due_date = db.Column(db.Date)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    members = relationship('User', secondary='project_member', back_populates='projects')
    tasks = relationship('Task', backref='project', lazy='dynamic')
    milestones = relationship('Milestone', backref='project', lazy='dynamic', order_by='Milestone.order_index')

class Milestone(db.Model):
    __tablename__ = 'milestone'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date)
    status = db.Column(db.String(50), default='pending') # pending/active/completed
    order_index = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), default='backlog') # backlog/in_progress/in_review/done
    priority = db.Column(db.String(50), default='medium') # low/medium/high/critical
    due_date = db.Column(db.Date)
    completed_at = db.Column(db.DateTime)
    estimated_hours = db.Column(db.Float)
    actual_hours = db.Column(db.Float)
    tags = db.Column(DbJSON, default=list) # JSON array
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    assignee = relationship('User', foreign_keys=[assignee_id], backref='assigned_tasks')
    reporter = relationship('User', foreign_keys=[reporter_id], backref='reported_tasks')
    comments = relationship('TaskComment', backref='task', lazy='dynamic')

    def is_overdue(self):
        if self.due_date and self.status != 'done':
            return self.due_date < datetime.now().date()
        return False

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'project_id': self.project_id,
            'assignee_id': self.assignee_id,
            'reporter_id': self.reporter_id,
            'status': self.status,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'estimated_hours': self.estimated_hours,
            'actual_hours': self.actual_hours,
            'tags': self.tags,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_overdue': self.is_overdue()
        }

class TaskComment(db.Model):
    __tablename__ = 'task_comment'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship('User', backref='comments')

class Channel(db.Model):
    __tablename__ = 'channel'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    is_private = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    members = relationship('User', secondary='channel_member', back_populates='channels')
    messages = relationship('Message', backref='channel', lazy='dynamic')

class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(50), default='text') # text/system/attachment
    attachment_name = db.Column(db.String(256))
    attachment_url = db.Column(db.String(1024))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    edited_at = db.Column(db.DateTime)

    sender = relationship('User', backref='messages_sent')

class ActivityLog(db.Model):
    __tablename__ = 'activity_log'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action_type = db.Column(db.String(100), nullable=False) 
    # task_created/task_moved/comment_added/project_created/member_joined/milestone_completed
    entity_type = db.Column(db.String(50), nullable=False) # task/project/milestone/message
    entity_id = db.Column(db.Integer, nullable=False)
    metadata_ = db.Column('metadata', DbJSON, default=dict)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship('User')
