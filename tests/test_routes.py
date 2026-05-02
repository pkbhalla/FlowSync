"""Tests for FlowSync auth and task routes."""
import pytest
from app import create_app, db
from app.models import User, Project, Task, ProjectMember


@pytest.fixture
def app():
    application = create_app('testing')
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def _register_admin(client):
    return client.post('/auth/register', data={
        'display_name': 'Admin User',
        'email': 'admin@example.com',
        'password': 'adminpass123',
    }, follow_redirects=True)


def _login(client, email='admin@example.com', password='adminpass123'):
    return client.post('/auth/login', data={
        'email': email,
        'password': password,
    }, follow_redirects=True)


class TestAuthRoutes:
    def test_login_page_loads(self, client):
        resp = client.get('/auth/login')
        assert resp.status_code == 200

    def test_register_page_loads(self, client):
        resp = client.get('/auth/register')
        assert resp.status_code == 200

    def test_register_creates_admin(self, client):
        _register_admin(client)
        with client.application.app_context():
            user = User.query.filter_by(email='admin@example.com').first()
            assert user is not None
            assert user.role == 'admin'

    def test_login_valid_credentials(self, client):
        _register_admin(client)
        # logout first
        client.get('/auth/logout')
        resp = _login(client)
        assert resp.status_code == 200

    def test_login_invalid_credentials(self, client):
        _register_admin(client)
        client.get('/auth/logout')
        resp = client.post('/auth/login', data={
            'email': 'admin@example.com',
            'password': 'wrongpass',
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_logout_redirects_to_login(self, client):
        _register_admin(client)
        resp = client.get('/auth/logout', follow_redirects=False)
        assert resp.status_code == 302

    def test_open_redirect_blocked(self, client):
        _register_admin(client)
        client.get('/auth/logout')
        resp = client.post('/auth/login?next=http://evil.com', data={
            'email': 'admin@example.com',
            'password': 'adminpass123',
        }, follow_redirects=False)
        # Should redirect to dashboard, not the external URL
        assert resp.status_code == 302
        assert 'evil.com' not in resp.headers.get('Location', '')


class TestTaskRoutes:
    def _setup(self, client, app):
        _register_admin(client)
        with app.app_context():
            user = User.query.filter_by(email='admin@example.com').first()
            project = Project(name='Test Project', color='#0e7c86', created_by=user.id)
            db.session.add(project)
            db.session.commit()
            pm = ProjectMember(project_id=project.id, user_id=user.id, role='lead')
            db.session.add(pm)
            db.session.commit()
            return project.id

    def test_tasks_page_requires_login(self, client):
        resp = client.get('/tasks/', follow_redirects=False)
        assert resp.status_code == 302

    def test_tasks_page_loads_when_authenticated(self, client, app):
        self._setup(client, app)
        resp = client.get('/tasks/')
        assert resp.status_code == 200

    def test_create_task(self, client, app):
        project_id = self._setup(client, app)
        import json
        resp = client.post('/tasks/create', json={
            'title': 'New Task',
            'project_id': project_id,
            'priority': 'medium',
        })
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['success'] is True

    def test_delete_task_by_reporter(self, client, app):
        project_id = self._setup(client, app)
        import json
        create_resp = client.post('/tasks/create', json={
            'title': 'Task to delete',
            'project_id': project_id,
        })
        task_id = json.loads(create_resp.data)['task']['id']
        del_resp = client.delete(f'/tasks/{task_id}')
        assert del_resp.status_code == 200

    def test_delete_task_by_non_reporter_forbidden(self, client, app):
        project_id = self._setup(client, app)
        # Create a second user and try to delete the first user's task
        import json
        create_resp = client.post('/tasks/create', json={
            'title': 'Protected task',
            'project_id': project_id,
        })
        task_id = json.loads(create_resp.data)['task']['id']

        with app.app_context():
            other = User(
                email='other@example.com',
                username='other',
                display_name='Other User',
                avatar_initials='OU',
                avatar_color='#ea580c',
                role='member',
            )
            other.set_password('otherpass')
            db.session.add(other)
            db.session.commit()

        client.get('/auth/logout')
        client.post('/auth/login', data={
            'email': 'other@example.com',
            'password': 'otherpass',
        })
        del_resp = client.delete(f'/tasks/{task_id}')
        assert del_resp.status_code == 403
