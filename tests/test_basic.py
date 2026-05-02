import unittest
from app import create_app, db
from app.models import User

class BasicTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app('development')
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_main_page_redirects(self):
        # Unauthenticated users should see the landing page directly
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Simplify workflows.', response.data)

    def test_user_creation(self):
        with self.app.app_context():
            u = User(
                email='test@example.com',
                username='testuser',
                display_name='Test User',
                avatar_initials='TU',
                avatar_color='#000000',
                role='admin'
            )
            u.set_password('password')
            db.session.add(u)
            db.session.commit()
            
            user = User.query.filter_by(email='test@example.com').first()
            self.assertIsNotNone(user)
            self.assertTrue(user.check_password('password'))

if __name__ == "__main__":
    unittest.main()