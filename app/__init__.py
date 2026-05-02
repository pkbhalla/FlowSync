from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

import os

def create_app(config_name='default'):
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    app = Flask(__name__,
                static_folder=os.path.join(root_path, 'static'),
                template_folder=os.path.join(root_path, 'app', 'templates'))
    app.config.from_object(config[config_name])

    db.init_app(app)
    login_manager.init_app(app)

    # Init Google OAuth
    from app.auth.routes import init_oauth
    init_oauth(app)

    # Register blueprints
    from app.auth.routes import auth_bp
    from app.dashboard.routes import dashboard_bp
    from app.tasks.routes import tasks_bp
    from app.projects.routes import projects_bp
    from app.team.routes import team_bp
    from app.messages.routes import messages_bp
    from app.analytics.routes import analytics_bp
    from app.api.routes import api_bp

    from app.admin.routes import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(tasks_bp, url_prefix='/tasks')
    app.register_blueprint(projects_bp, url_prefix='/projects')
    app.register_blueprint(team_bp, url_prefix='/team')
    app.register_blueprint(messages_bp, url_prefix='/messages')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    with app.app_context():
        db.create_all()

    # Register error handlers
    from app.errors import register_error_handlers
    register_error_handlers(app)

    return app
