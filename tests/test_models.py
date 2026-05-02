"""Tests for FlowSync database models."""
import pytest
from datetime import date, datetime, timezone, timedelta
from app import create_app, db
from app.models import User, Project, Task, ProjectMember, Channel, Message


@pytest.fixture
def app():
    application = create_app('testing')
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def session(app):
    return db.session


def _make_user(email='test@example.com', username='testuser', role='member'):
    u = User(
        email=email,
        username=username,
        display_name='Test User',
        avatar_initials='TU',
        avatar_color='#0e7c86',
        role=role,
    )
    u.set_password('password123')
    return u


class TestUserModel:
    def test_password_hashing(self, session):
        u = _make_user()
        session.add(u)
        session.commit()
        assert u.password_hash is not None
        assert u.check_password('password123')
        assert not u.check_password('wrongpassword')

    def test_to_dict(self, session):
        u = _make_user()
        session.add(u)
        session.commit()
        d = u.to_dict()
        assert d['email'] == 'test@example.com'
        assert d['username'] == 'testuser'
        assert 'password_hash' not in d

    def test_unique_email_constraint(self, session):
        u1 = _make_user()
        u2 = _make_user()
        session.add(u1)
        session.commit()
        session.add(u2)
        with pytest.raises(Exception):
            session.commit()

    def test_google_oauth_user_no_password(self, session):
        u = User(
            email='google@example.com',
            username='googleuser',
            display_name='Google User',
            avatar_initials='GU',
            avatar_color='#2563eb',
            google_id='google-sub-123',
        )
        session.add(u)
        session.commit()
        assert u.password_hash is None


class TestTaskModel:
    def _make_project_and_user(self, session):
        u = _make_user()
        session.add(u)
        session.flush()
        p = Project(name='Test Project', color='#0e7c86', created_by=u.id)
        session.add(p)
        session.flush()
        return u, p

    def test_is_overdue_past_due_date(self, session):
        u, p = self._make_project_and_user(session)
        t = Task(
            title='Old task',
            project_id=p.id,
            reporter_id=u.id,
            status='in_progress',
            due_date=date.today() - timedelta(days=1),
        )
        session.add(t)
        session.commit()
        assert t.is_overdue() is True

    def test_is_overdue_future_due_date(self, session):
        u, p = self._make_project_and_user(session)
        t = Task(
            title='Future task',
            project_id=p.id,
            reporter_id=u.id,
            status='in_progress',
            due_date=date.today() + timedelta(days=7),
        )
        session.add(t)
        session.commit()
        assert t.is_overdue() is False

    def test_is_not_overdue_when_done(self, session):
        u, p = self._make_project_and_user(session)
        t = Task(
            title='Done task',
            project_id=p.id,
            reporter_id=u.id,
            status='done',
            due_date=date.today() - timedelta(days=5),
        )
        session.add(t)
        session.commit()
        assert t.is_overdue() is False

    def test_to_dict_contains_expected_keys(self, session):
        u, p = self._make_project_and_user(session)
        t = Task(title='Test', project_id=p.id, reporter_id=u.id)
        session.add(t)
        session.commit()
        d = t.to_dict()
        for key in ('id', 'title', 'project_id', 'status', 'priority', 'is_overdue'):
            assert key in d
