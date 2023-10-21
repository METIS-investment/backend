from datetime import datetime
from flask import Blueprint, jsonify, request
from extensions import db
from authorization import authorize
from models import User
from sqlalchemy.exc import IntegrityError
from firebase_admin import auth
import stripe

user_bp = Blueprint('user', __name__)


@user_bp.route('/signup', methods=['POST'])
@authorize
def signup():
    print("CALL - signup")
    try:
        data = request.get_json()
        user = User.query.get(request.uid)

        if user:
            return jsonify({"error": "User already registered  exist"}), 404

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

        # Fetch the user from Firebase
        #firebase_user = auth.get_user(request.uid)
        email = "info@simonsure.co"#firebase_user.email  # user's email

        # Create Stripe customer
        stripe_customer = stripe.Customer.create(
            name=f"{data.get('first_name')} {data.get('second_name')}",
            email=email,  # assuming uid is email
        )
        stripe_id = stripe_customer['id']

        user_id = request.uid

        new_user = User(
            id=user_id,
            first_name=first_name,
            second_name=second_name,
            birthdate=birthdate,
            registration_date=datetime.utcnow(),
            stripe_id=stripe_id,
            street=street,
            city=city,
            zip_code=zip_code,
            country=country,
            billable=False,
            finish_signup=False
        )

        db.session.add(new_user)
        db.session.commit()

        print("FINISHED - signup")
        return jsonify({"message": "User created successfully."}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred: " + str(e)}), 500


@user_bp.route('/finish_signup', methods=['POST'])
@authorize
def finish_signup():
    print("CALL - finish signup")
    try:
        user_id = request.uid
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User does not exist"}), 404

        user.finish_signup = True
        db.session.commit()

        print("FINISH - finish signup")
        return jsonify({"message": "Signup process completed."}), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database constraint violation. User may not be properly set up."}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred."}), 500


@user_bp.route('/payment_method', methods=['POST'])
#@authorize
def update_payment_details():
    try:
        # Get user by UID
        user_id = "1"#request.uid
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User does not exist"}), 404

        if not user.finish_signup:
            return jsonify({"error": "User has not finished setup"}), 403

        stripe_id = user.stripe_id

        # Fetch payload data
        data = request.get_json()

        # Validate PaymentMethod ID
        if not data or 'payment_method_id' not in data:
            return jsonify({"error": "PaymentMethod ID is missing"}), 400

        payment_method_id = data['payment_method_id']

        # Attach PaymentMethod to Customer
        r = stripe.PaymentMethod.attach(
            payment_method_id,
            customer=stripe_id,
        )

        # Set as default PaymentMethod
        stripe.Customer.modify(
            stripe_id,
            invoice_settings={
                "default_payment_method": r['id']
            }
        )

        user.billable = True
        db.session.commit()

        return jsonify({"message": "Payment method updated."}), 200

    except stripe.error.StripeError as e:
        return jsonify({"error": f"Stripe error."}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database constraint violation. User may not be properly set up."}), 400
    except Exception as e:
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
        print(e)
        return jsonify({"error": "An unexpected error occurred."}), 500
