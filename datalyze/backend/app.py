# ─── Datalyze — Main Application Entry Point ────────────────────────────────
#
# This file creates the Flask app, registers all Blueprints,
# and starts the development server.
#
# Module structure:
#   config.py          → App configuration & constants
#   models.py          → In-memory data storage
#   utils.py           → Helper functions (OTP, hashing, chart tools)
#   auth_routes.py     → Authentication endpoints  (/api/register, /api/login, …)
#   upload_routes.py   → File upload endpoint       (/api/upload)
#   analysis.py        → Data analysis engine        (analyse function)
#   report_routes.py   → PDF report endpoint         (/api/report)
# ─────────────────────────────────────────────────────────────────────────────

import os
import matplotlib
matplotlib.use('Agg')
import warnings
warnings.filterwarnings('ignore')

from flask import Flask, render_template
from config import FRONTEND_DIR, SECRET_KEY, MAX_CONTENT_LENGTH, UPLOAD_FOLDER, REPORTS_FOLDER, SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from models import db


def create_app():
    """Application factory — creates and configures the Flask app."""

    app = Flask(__name__, template_folder=FRONTEND_DIR, static_folder=os.path.join(FRONTEND_DIR, 'static'))
    app.secret_key = SECRET_KEY
    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

    # Initialize extensions
    db.init_app(app)

    # Ensure runtime directories exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(REPORTS_FOLDER, exist_ok=True)

    # ── Register Blueprints ─────────────────────────────────────────────────
    from auth_routes import auth_bp
    from upload_routes import upload_bp
    from report_routes import report_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(report_bp)

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    # ── Root route — serves the frontend ────────────────────────────────────
    @app.route('/')
    def index():
        return render_template('index.html')

    return app


# ─── Development Server ────────────────────────────────────────────────────
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
