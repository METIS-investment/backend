from datetime import datetime
from flask import Blueprint, jsonify, request
from extensions import db
from authorization import authorize
from users_models import User
from sqlalchemy.exc import IntegrityError

user_bp = Blueprint('user', __name__)


@user_bp.route('/user')
@authorize
def hello_world():  # put application's code here
    return jsonify({"message": "user endpoint."}), 200


@user_bp.route('/signup', methods=['POST'])
@authorize
def signup():
    try:
        data = request.get_json()

        # Validation for each field
        if not data:
            return jsonify({"error": "No data provided"}), 400

        required_fields = ['first_name', 'second_name', 'birthdate', 'country', 'street', 'city', 'zip_code']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"{field} is missing"}), 400

        first_name = data.get('first_name')
        second_name = data.get('second_name')
        try:
            birthdate = datetime.strptime(data.get('birthdate'), '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            return jsonify({"error": "Invalid birthdate format"}), 400

        country = data.get('country')
        street = data.get('street')
        city = data.get('city')
        zip_code = data.get('zip_code')

        user_id = request.uid

        new_user = User(
            id=user_id,
            first_name=first_name,
            second_name=second_name,
            birthdate=birthdate,
            registration_date=datetime.utcnow(),
            stripe_id='some_stripe_id',
            street=street,
            city=city,
            zip_code=zip_code,
            country=country,
            billable=False,
            finish_signup=False
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User created successfully."}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred: " + str(e)}), 500


@user_bp.route('/finish_signup', methods=['POST'])
@authorize
def finish_signup():
    try:
        user_id = request.uid
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User does not exist"}), 404

        user.finish_signup = True
        db.session.commit()

        return jsonify({"message": "Signup process completed."}), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database constraint violation. User may not be properly set up."}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred."}), 500


@user_bp.route('/details', methods=['GET'])
@authorize
def get_details():
    try:
        user_id = request.uid
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User does not exist"}), 404

        response = {
            "first_name": user.first_name,
            "second_name": user.second_name,
            "birthdate": user.birthdate.strftime('%Y-%m-%d'),
            "country": user.country,
            "street": user.street,
            "city": user.city,
            "zip_code": user.zip_code,
            "setup_up": user.finish_signup,
            "registration_date": user.registration_date.strftime('%Y-%m-%d %H:%M:%S')
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": "An unexpected error occurred."}), 500
