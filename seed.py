import os
import sys
import random
from datetime import datetime, timedelta, timezone
from app import create_app, db
from app.models import User, Project, ProjectMember, Milestone, Task, Channel, ChannelMember, Message, ActivityLog, TaskComment

def seed_database(fresh=True):
    app = create_app(os.environ.get('FLASK_ENV', 'development'))
    with app.app_context():
        if fresh:
            print("Dropping all tables...")
            db.drop_all()
            print("Creating all tables...")
            db.create_all()

        print("Seeding Users...")
        users_data = [
            ("admin@iitm.ac.in", "admin", "Arun Kumar", "#01696f", "admin"),
            ("priya@iitm.ac.in", "priya", "Priya Sharma", "#964219", "member"),
            ("rahul@iitm.ac.in", "rahul", "Rahul Desai", "#006494", "member"),
            ("neha@iitm.ac.in", "neha", "Neha Gupta", "#7a39bb", "member"),
            ("karthik@iitm.ac.in", "karthik", "Karthik Iyer", "#437a22", "member"),
            ("sneha@iitm.ac.in", "sneha", "Sneha Patel", "#a12c7b", "member"),
            ("vikram@iitm.ac.in", "vikram", "Vikram Singh", "#da7101", "member"),
            ("divya@iitm.ac.in", "divya", "Divya Menon", "#01696f", "viewer"),
        ]
        
        users = []
        for email, username, display_name, color, role in users_data:
            u = User(
                email=email,
                username=username,
                display_name=display_name,
                avatar_initials="".join([n[0] for n in display_name.split()]),
                avatar_color=color,
                role=role
            )
            u.set_password("password123")
            db.session.add(u)
            users.append(u)
        db.session.commit()

        print("Seeding Projects...")
        projects_data = [
            ("FlowSync Web App", "Core team coordination platform MVP", "#01696f", "active"),
            ("Mobile App Migration", "Migrating React Native to Flutter", "#7a39bb", "planning"),
            ("Data Pipeline V2", "Refactoring ETL jobs to Apache Airflow", "#006494", "active"),
            ("Security Audit Q3", "Addressing pentest vulnerabilities", "#a12c7b", "on_hold"),
            ("Marketing Site Refresh", "New landing pages with Next.js", "#da7101", "completed")
        ]
        
        projects = []
        for name, desc, color, status in projects_data:
            p = Project(
                name=name,
                description=desc,
                color=color,
                status=status,
                created_by=users[0].id
            )
            db.session.add(p)
            projects.append(p)
        db.session.commit()

        print("Seeding Project Members...")
        for p in projects:
            # Add 3-5 random members to each project
            project_users = random.sample(users, random.randint(3, 5))
            for i, u in enumerate(project_users):
                role = 'lead' if i == 0 else 'member'
                pm = ProjectMember(project_id=p.id, user_id=u.id, role=role)
                db.session.add(pm)
        db.session.commit()

        print("Seeding Milestones...")
        for p in projects:
            for i in range(6):
                status = random.choice(['completed', 'active', 'pending'])
                due = datetime.now(timezone.utc) + timedelta(days=random.randint(-30, 60))
                m = Milestone(
                    project_id=p.id,
                    title=f"Milestone {i+1} for {p.name}",
                    description=f"Description for milestone {i+1}",
                    due_date=due.date(),
                    status=status,
                    order_index=i
                )
                db.session.add(m)
        db.session.commit()

        print("Seeding Tasks...")
        task_titles = [
            "Implement JWT refresh token rotation",
            "Fix N+1 query in student report endpoint",
            "Set up GitHub Actions CI pipeline",
            "Update UI library to latest version",
            "Design database schema for notifications",
            "Write unit tests for authentication module",
            "Optimize image loading on landing page",
            "Integrate Stripe payment gateway",
            "Create user onboarding flow",
            "Resolve memory leak in background worker"
        ]
        
        statuses = ['backlog', 'in_progress', 'in_review', 'done']
        priorities = ['low', 'medium', 'high', 'critical']
        
        for _ in range(45):
            p = random.choice(projects)
            u = random.choice(users)
            status = random.choice(statuses)
            due = datetime.now(timezone.utc) + timedelta(days=random.randint(-10, 30))
            completed_at = datetime.now(timezone.utc) - timedelta(days=random.randint(1, 10)) if status == 'done' else None
            
            t = Task(
                title=random.choice(task_titles) + f" #{random.randint(100, 999)}",
                description="This is a detailed description of the task that needs to be done.",
                project_id=p.id,
                assignee_id=u.id,
                reporter_id=users[0].id,
                status=status,
                priority=random.choice(priorities),
                due_date=due.date(),
                completed_at=completed_at,
                estimated_hours=random.randint(2, 20),
                actual_hours=random.randint(2, 20) if status == 'done' else None
            )
            db.session.add(t)
        db.session.commit()

        print("Seeding Channels & Messages...")
        channel_names = ['general', 'engineering', 'deployments']
        channels = []
        for name in channel_names:
            c = Channel(name=name, created_by=users[0].id)
            db.session.add(c)
            channels.append(c)
        db.session.commit()
        
        for c in channels:
            for u in users:
                cm = ChannelMember(channel_id=c.id, user_id=u.id)
                db.session.add(cm)
        db.session.commit()

        message_texts = [
            "Hey team, how is the sprint going?",
            "I've pushed the fix for the login bug.",
            "Can someone review my PR?",
            "Deploying to staging now.",
            "The CI pipeline is failing, looking into it.",
            "Great work on the new feature release!",
            "Standup at 10 AM today.",
            "I'll be OOO tomorrow."
        ]
        
        for _ in range(35):
            c = random.choice(channels)
            u = random.choice(users)
            m = Message(
                channel_id=c.id,
                sender_id=u.id,
                content=random.choice(message_texts),
                created_at=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 72))
            )
            db.session.add(m)
        db.session.commit()

        print("Seeding Activity Log...")
        action_types = ['task_created', 'task_moved', 'comment_added', 'project_created']
        tasks = Task.query.all()
        for _ in range(50):
            u = random.choice(users)
            t = random.choice(tasks)
            action = random.choice(action_types)
            log = ActivityLog(
                user_id=u.id,
                action_type=action,
                entity_type='task',
                entity_id=t.id,
                metadata_={'task_title': t.title, 'new_status': t.status} if action == 'task_moved' else {'task_title': t.title},
                created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 30))
            )
            db.session.add(log)
        db.session.commit()

        print("Seed completed successfully!")

if __name__ == '__main__':
    fresh = '--fresh' in sys.argv
    seed_database(fresh=fresh)
