import hashlib, random
from flask import render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, current_user
from authlib.integrations.flask_client import OAuth
from app import db
from app.auth import auth_bp
from app.models import User, WhitelistInvitation, ProjectMember

oauth = OAuth()

def init_oauth(app):
    """Call from create_app to register Google provider."""
    oauth.init_app(app)
    if app.config.get('GOOGLE_CLIENT_ID'):
        oauth.register(
            name='google',
            client_id=app.config['GOOGLE_CLIENT_ID'],
            client_secret=app.config['GOOGLE_CLIENT_SECRET'],
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={'scope': 'openid email profile'},
        )

def _random_color():
    colors = ['#0e7c86','#2563eb','#7c3aed','#ea580c','#c2690e','#2d8a39','#c43e5c','#006494']
    return random.choice(colors)

# ---------- Standard email/password login (kept as fallback) ----------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user is None or not user.password_hash or not user.check_password(password):
            flash('Invalid email or password', 'error')
            return redirect(url_for('auth.login'))
        login_user(user, remember=True)
        next_page = request.args.get('next')
        return redirect(next_page or url_for('dashboard.index'))
    has_google = current_app.config.get('GOOGLE_CLIENT_ID') is not None
    return render_template('auth/login.html', has_google=has_google)

# ---------- Google OAuth ----------
@auth_bp.route('/google/login')
def google_login():
    if not current_app.config.get('GOOGLE_CLIENT_ID'):
        flash('Google OAuth not configured', 'error')
        return redirect(url_for('auth.login'))
    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route('/google/callback')
def google_callback():
    try:
        token = oauth.google.authorize_access_token()
    except Exception as e:
        flash(f'Google auth failed: {e}', 'error')
        return redirect(url_for('auth.login'))

    userinfo = token.get('userinfo')
    if not userinfo:
        flash('Could not fetch Google profile', 'error')
        return redirect(url_for('auth.login'))

    google_id = userinfo['sub']
    email = userinfo['email']
    name = userinfo.get('name', email.split('@')[0])

    # Check if user already exists (by google_id or email)
    user = User.query.filter((User.google_id == google_id) | (User.email == email)).first()

    if user:
        # Existing user — link google_id if missing
        if not user.google_id:
            user.google_id = google_id
            db.session.commit()
        login_user(user, remember=True)
        return redirect(url_for('dashboard.index'))

    # New user — check whitelist
    invite = WhitelistInvitation.query.filter_by(email=email, is_claimed=False).first()
    if not invite:
        flash('Unauthorized: Ask your admin for an invite.', 'error')
        return redirect(url_for('auth.login'))

    # Create new user from invite
    initials = ''.join([w[0] for w in name.split()[:2]]).upper() or 'U'
    user = User(
        email=email,
        username=email.split('@')[0],
        display_name=name,
        avatar_initials=initials,
        avatar_color=_random_color(),
        google_id=google_id,
        role='member',
    )
    db.session.add(user)
    db.session.flush()  # get user.id

    # Link to invited project
    pm = ProjectMember(project_id=invite.project_id, user_id=user.id, role='member')
    db.session.add(pm)

    invite.is_claimed = True
    db.session.commit()

    login_user(user, remember=True)
    flash(f'Welcome to FlowSync, {name}!', 'success')
    return redirect(url_for('dashboard.index'))

# ---------- Logout ----------
@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
