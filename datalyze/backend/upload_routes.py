# ─── File Upload Routes ─────────────────────────────────────────────────────
from flask import Blueprint, request, jsonify, session
import pandas as pd
from datetime import datetime

from models import db, User
from analysis import analyse

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/api/upload', methods=['POST'])
def upload():
    email = session.get('user')
    if not email:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401

    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'}), 400

    f = request.files['file']
    fname = f.filename.lower()

    try:
        if fname.endswith('.csv'):
            df = pd.read_csv(f)
        elif fname.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(f)
        elif fname.endswith('.json'):
            df = pd.read_json(f)
        else:
            return jsonify({'success': False, 'message': 'Unsupported format. Use CSV, Excel, or JSON'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Read error: {str(e)}'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    # Update streak
    today = datetime.now().date()
    if user.last_upload:
        last = datetime.fromisoformat(user.last_upload).date()
        if last != today:
            user.streak += 1
    else:
        user.streak = 1
        
    user.last_upload = datetime.now().isoformat()
    db.session.commit()

    # Run full analysis
    result = analyse(df, f.filename)
    result['streak'] = user.streak
    return jsonify(result)
