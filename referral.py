from flask import Blueprint, render_template, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json

referral_bp = Blueprint('referral_bp', __name__, url_prefix='/referral')

# Set up database connections for the different pages
engine_page1 = create_engine('sqlite:///survey_response.db', connect_args={'check_same_thread': False})
engine_page2 = create_engine('sqlite:///survey_responses_page1.db', connect_args={'check_same_thread': False})
engine_page3 = create_engine('sqlite:///survey_responses_page2.db', connect_args={'check_same_thread': False})

SessionPage1 = sessionmaker(bind=engine_page1)
SessionPage2 = sessionmaker(bind=engine_page2)
SessionPage3 = sessionmaker(bind=engine_page3)

@referral_bp.route('/', methods=['GET'])
def index():
    return render_template('referral.html')

@referral_bp.route('/search', methods=['POST'])
def search():
    # Local imports to prevent circular dependency issues.
    from index import SurveyResponseIndex
    from page2 import SurveyResponsePage2
    from page3 import SurveyResponsePage3

    search_id = request.form.get('search_id')
    if not search_id:
        return render_template('referral.html', error="Please enter an ID to search")

    try:
        search_id = int(search_id)
    except ValueError:
        return render_template('referral.html', error="Please enter a valid numeric ID")

    # Search in all three databases.
    session1 = SessionPage1()
    session2 = SessionPage2()
    session3 = SessionPage3()

    try:
        # Search in Page 1 (survey_response) database.
        response1 = session1.query(SurveyResponseIndex).filter_by(id=search_id).first()
        if response1:
            other_data = {}
            if response1.other_data:
                try:
                    other_data = json.loads(response1.other_data)
                except Exception:
                    pass
            result = {
                'ID': response1.id,
                'Name': other_data.get('name', ''),
                'Email': other_data.get('email', ''),
                'Age': response1.age,
                'Gender': response1.gender,
                'Day Experience': other_data.get('day_experience', ''),
                'Alarm Usage': other_data.get('alarm_usage', ''),
                'Alarm Choice': other_data.get('alarm_choice', ''),
                'Unique User ID': response1.unique_user_id,
                'Referral ID': response1.referral_id,
                'Database': 'Page 1'
            }
            return render_template('referral.html', response=result)

        # Search in Page 2 database.
        response2 = session2.query(SurveyResponsePage2).filter_by(id=search_id).first()
        if response2:
            result = {
                'ID': response2.id,
                'Name': response2.name,
                'Email': response2.email,
                'Password': response2.password,
                'Age': response2.age,
                'Gender': response2.gender,
                'Alarm Usage': response2.alarm_usage,
                'Unique User ID': 'N/A',
                'Referral ID': 'N/A',
                'Database': 'Page 2'
            }
            return render_template('referral.html', response=result)

        # Search in Page 3 database.
        response3 = session3.query(SurveyResponsePage3).filter_by(id=search_id).first()
        if response3:
            result = {
                'ID': response3.id,
                'Alarm Choice': response3.alarm_choice,
                'Features': response3.features,
                'Number of Alarms': response3.num_alarms,
                'Purchase Date': response3.purchase_date.strftime('%Y-%m-%d') if response3.purchase_date else None,
                'Alarm URL': response3.alarm_url,
                'Comments': response3.comments,
                'Unique User ID': 'N/A',
                'Referral ID': 'N/A',
                'Database': 'Page 3'
            }
            return render_template('referral.html', response=result)

        return render_template('referral.html', error=f"No entry found with ID {search_id} in any database")
    finally:
        session1.close()
        session2.close()
        session3.close()

@referral_bp.route('/unique-user/<referral_id>', methods=['GET'])
def view_unique_user(referral_id):
    from index import SurveyResponseIndex
    responses = SurveyResponseIndex.query.filter_by(referral_id=referral_id).all()
    if responses:
        return render_template('unique_user.html', referral_id=referral_id, responses=responses)
    return render_template('referral.html', error="No responses found for this unique user.")
