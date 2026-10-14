# 🚀 Datalyze — How to Run

## Prerequisites

Make sure you have **Python 3.10+** installed. You can verify with:

```bash
python --version
```

---

## 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

---

## 2. Initialize the Database

Before running the server for the first time, the SQLite database needs to be initialized. The app automatically creates the necessary tables on the first run, but ensure you run the app once locally.

## 3. Run the Backend (Flask Server - Development)

```bash
cd backend
python app.py
```

The server will start at: **http://localhost:5000**

> The backend serves both the API and the frontend HTML, so you only need to run this one command. Open the URL above in your browser to use the full application.

---

## 4. Production Deployment

For production, it is highly recommended to use the provided Docker setup or run the app via Gunicorn.

### Using Docker (Recommended)

1. Build the Docker image from the root `datalyze` directory:
   ```bash
   docker build -t datalyze-app .
   ```
2. Run the Docker container:
   ```bash
   docker run -p 8000:8000 datalyze-app
   ```
   The app will be available at **http://localhost:8000**.

### Using Gunicorn (Without Docker)

```bash
cd backend
gunicorn --bind 0.0.0.0:8000 --workers 3 wsgi:app
```

---

## 5. Project Structure

```
datalyze/
├── COMMANDS.md              ← You are here
├── README.md                ← Project overview
├── Dockerfile               ← Production Docker configuration
├── .gitignore
│
├── backend/                 ← Flask API server
│   ├── app.py               ← Main entry point (starts the server)
│   ├── wsgi.py              ← Gunicorn entry point for production
│   ├── config.py            ← Configuration & constants
│   ├── models.py            ← Database models (SQLAlchemy)
│   ├── datalyze.db          ← SQLite Database (auto-generated)
│   ├── utils.py             ← Helper functions (OTP, hashing, charts)
│   ├── auth_routes.py       ← Auth endpoints (/api/register, /api/login, …)
│   ├── upload_routes.py     ← File upload endpoint (/api/upload)
│   ├── analysis.py          ← Data analysis engine
│   ├── report_routes.py     ← PDF report endpoint (/api/report)
│   ├── requirements.txt     ← Python dependencies
│   ├── uploads/             ← Uploaded files (auto-created)
│   └── reports/             ← Generated reports (auto-created)
│
└── frontend/                ← Client-side UI
    ├── index.html           ← Single-page application HTML
    └── static/              ← Static assets
        ├── css/style.css    ← Extracted styling
        └── js/script.js     ← Extracted logic
```

---

## 6. Available API Endpoints

| Method | Endpoint             | Description                  |
|--------|----------------------|------------------------------|
| GET    | `/`                  | Serve the frontend UI        |
| POST   | `/api/register`      | Register a new user          |
| POST   | `/api/verify-otp`    | Verify registration OTP      |
| POST   | `/api/login`         | Login (sends OTP)            |
| POST   | `/api/login-verify`  | Verify login OTP             |
| POST   | `/api/logout`        | Logout current session       |
| GET    | `/api/me`            | Get current user info        |
| POST   | `/api/upload`        | Upload & analyse a dataset   |
| POST   | `/api/report`        | Generate PDF report          |

---

## 5. Supported File Formats

- **CSV** (`.csv`)
- **Excel** (`.xls`, `.xlsx`)
- **JSON** (`.json`)

Max upload size: **50 MB**

---

## 6. Troubleshooting

### Port already in use?
```bash
# Change the port in backend/app.py or run with:
python -c "from app import create_app; create_app().run(port=8080)"
```

### Missing dependencies?
```bash
pip install flask pandas numpy matplotlib seaborn scipy reportlab openpyxl
```

### Module not found errors?
Make sure you are running from inside the `backend/` directory:
```bash
cd backend
python app.py
```
