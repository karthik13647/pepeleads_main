from flask import Flask, request, jsonify
from index import index_bp, db, CustomerAction
from page2 import page2_bp
from page3 import page3_bp
from referral import referral_bp
import os
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///survey_response.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)

# Initialize the database with our app
db.init_app(app)

def fromjson_filter(s):
    try:
        return json.loads(s)
    except Exception:
        return {}

app.jinja_env.filters['fromjson'] = fromjson_filter

# Register Blueprints
app.register_blueprint(index_bp)         # Handles index.html at '/'
app.register_blueprint(page2_bp)         # Handles page2.html at '/page2'
app.register_blueprint(page3_bp)         # Handles page3.html at '/page3'
app.register_blueprint(referral_bp)      # Handles referral routes at '/referral'

# Create/update tables on app startup
with app.app_context():
    db.create_all()

# --- S2S Tracking Endpoint ---
@app.route('/track-action', methods=['POST'])
def track_action():
    data = request.get_json()
    # Now using unique_user_id instead of customer_id as a string.
    unique_user_id = data.get("unique_user_id")
    action_type = data.get("action_type")
    referral_id = data.get("referral_id")
    
    # Validate incoming data
    if not all([unique_user_id, action_type, referral_id]):
        return jsonify({"error": "Missing data"}), 400
    
    # Create a new tracking event
    new_event = CustomerAction(
        unique_user_id=unique_user_id,
        action_type=action_type,
        referral_id=referral_id
    )
    try:
        db.session.add(new_event)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(debug=True)
