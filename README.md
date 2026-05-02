# FlowSync

FlowSync is a self-hosted team coordination platform for software and engineering teams. It manages tasks, projects, team members, real-time messaging, and productivity analytics — all in one place.

## Features
- **Dashboard**: KPI counts, activity feed, and your upcoming tasks.
- **Tasks**: Kanban board with drag-and-drop, grouped by status.
- **Projects**: Project lists with milestone progress and member tracking.
- **Team**: View team members, their workload, and completion rates.
- **Messages**: Real-time chat via Server-Sent Events (SSE).
- **Analytics**: Beautiful charts for weekly completions, project distribution, and team throughput.

## Tech Stack
- **Backend**: Python 3.11, Flask
- **Database**: PostgreSQL (via SQLAlchemy ORM) or SQLite (local)
- **Frontend**: Jinja2, Vanilla JavaScript, Pure CSS Design System
- **Deployment**: Docker, Google Cloud Run

## Local Development Setup

```bash
git clone <repo>
cd flowsync
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env as needed
python seed.py --fresh
python run.py
# Open http://localhost:5000
```

## Seeded Test Accounts
After running `seed.py`, the following accounts are available (password for all is `password123`):
- admin@iitm.ac.in (Admin)
- priya@iitm.ac.in (Member)
- rahul@iitm.ac.in (Member)

## Google Cloud Run Deployment

1. **Build locally first**
```bash
docker build -t flowsync .
docker run -p 8080:8080 -e SECRET_KEY=test -e FLASK_ENV=production flowsync
```

2. **Push to Google Container Registry**
```bash
gcloud auth configure-docker
docker tag flowsync gcr.io/YOUR_PROJECT_ID/flowsync
docker push gcr.io/YOUR_PROJECT_ID/flowsync
```

3. **Create Cloud SQL PostgreSQL instance (run once)**
```bash
gcloud sql instances create flowsync-db \
  --database-version=POSTGRES_15 \
  --region=asia-south1 \
  --tier=db-f1-micro

gcloud sql databases create flowsync --instance=flowsync-db
gcloud sql users create flowsync-user --instance=flowsync-db --password=YOUR_DB_PASSWORD
```

4. **Deploy to Cloud Run**
```bash
gcloud run deploy flowsync \
  --image gcr.io/YOUR_PROJECT_ID/flowsync \
  --platform managed \
  --region asia-south1 \
  --allow-unauthenticated \
  --add-cloudsql-instances YOUR_PROJECT_ID:asia-south1:flowsync-db \
  --set-env-vars="SECRET_KEY=your-secret-key,FLASK_ENV=production" \
  --set-env-vars="DATABASE_URL=postgresql://flowsync-user:YOUR_DB_PASSWORD@/flowsync?host=/cloudsql/YOUR_PROJECT_ID:asia-south1:flowsync-db" \
  --port 8080 \
  --memory 512Mi \
  --min-instances 1 \
  --max-instances 10
```

5. **Run seed data on Cloud Run (one-time)**
```bash
gcloud run jobs create flowsync-seed \
  --image gcr.io/YOUR_PROJECT_ID/flowsync \
  --region asia-south1 \
  --add-cloudsql-instances YOUR_PROJECT_ID:asia-south1:flowsync-db \
  --set-env-vars="DATABASE_URL=postgresql://..." \
  --command="python" \
  --args="seed.py"

gcloud run jobs execute flowsync-seed --region asia-south1
```

## Environment Variables
| Variable | Description |
|---|---|
| `SECRET_KEY` | Flask secret key for sessions |
| `FLASK_ENV` | `development` or `production` |
| `DATABASE_URL` | SQLAlchemy connection string |
| `PORT` | Port to run on (default 5000 or 8080 in Docker) |

## Project Structure
```
flowsync/
├── app/
├── static/
├── templates/
├── Dockerfile
├── requirements.txt
├── config.py
├── run.py
├── seed.py
└── README.md
```

## License
MIT
