from datetime import datetime
from flask import Blueprint, jsonify, request
from extensions import db
from authorization import authorize
import stripe
from models import User  # Add this import

investment_bp = Blueprint('investment', __name__)


@investment_bp.route('/one-time-investment', methods=['POST'])
@authorize
def one_time_investment():
    try:
        # Get user ID and details
        user_id = request.uid
        user = User.query.get(user_id)

        # Check if user exists and is billable
        if not user:
            return jsonify({"error": "User does not exist"}), 404
        if not user.billable:
            return jsonify({"error": "User is not billable"}), 403

        # Get value from request payload
        data = request.get_json()
        if 'value' not in data:
            return jsonify({"error": "Value is missing"}), 400
        value = int(data['value'])

        # Create Stripe PaymentIntent
        payment_intent = stripe.PaymentIntent.create(
            amount=value,
            currency="eur",
            customer=user.stripe_id
        )

        return jsonify({"payment_intent": payment_intent['client_secret']}), 201

    except stripe.error.StripeError as e:
        return jsonify({"error": f"Stripe error: {str(e)}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred: " + str(e)}), 500


@investment_bp.route('/recurring-investment', methods=['POST'])
@authorize
def setup_subscription():
    try:
        user_id = request.uid
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User does not exist"}), 404
        if not user.billable:
            return jsonify({"error": "User is not billable"}), 403

        data = request.get_json()
        if 'monthly_value' not in data:
            return jsonify({"error": "Monthly value is missing"}), 400
        monthly_value = int(data['monthly_value'])

        customer_id = user.stripe_id
        subscriptions = stripe.Subscription.list(customer=customer_id, status='all')

        for subscription in subscriptions:
            if subscription.status in ['active', 'trialing', 'past_due', 'unpaid']:
                return jsonify({"error": "Already an active subscription"}), 400

        # Create Stripe Subscription
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{'price_data': {
                "unit_amount": monthly_value,
                "currency": "eur",
                "product": "prod_Or6dLhhP1w1avS",
                "recurring": {"interval": "month"}
            }}],
            expand=['latest_invoice.payment_intent'],
        )

        return jsonify(
            subscriptionId=subscription.id,
            clientSecret=subscription.latest_invoice.payment_intent.client_secret
        ), 201

    except stripe.error.StripeError as e:
        return jsonify({"error": f"Stripe error: {str(e)}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred: " + str(e)}), 500


@investment_bp.route('/recurring-investment', methods=['DELETE'])
@authorize
def cancel_subscription():
    try:
        user_id = request.uid
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User does not exist"}), 404
        if not user.billable:
            return jsonify({"error": "User is not billable"}), 403

        customer_id = user.stripe_id
        subscriptions = stripe.Subscription.list(customer=customer_id, status='all')

        for subscription in subscriptions:
            if subscription.status in ['active', 'trialing', 'past_due', 'unpaid']:
                stripe.Subscription.modify(
                    subscription.id,
                    cancel_at_period_end=True
                )

        return jsonify({"message": "Subscription cancelled"}), 200

    except stripe.error.StripeError as e:
        return jsonify({"error": f"Stripe error: {str(e)}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@investment_bp.route('/recurring-investment', methods=['PATCH'])
@authorize
def update_subscription():
    try:
        # Get the user ID from the request
        user_id = request.uid
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User does not exist"}), 404
        if not user.billable:
            return jsonify({"error": "User is not billable"}), 403

        # Get new EUR value from JSON payload
        new_value_eur = request.json.get('value', None)
        if new_value_eur is None:
            return jsonify({"error": "Missing value"}), 400

        customer_id = user.stripe_id

        # Check for active subscription
        active_subscriptions = stripe.Subscription.list(customer=customer_id, status='active', limit=1)
        if len(active_subscriptions) == 0:
            return jsonify({"error": "No active subscription found"}), 404

        active_subscription = active_subscriptions.data[0]
        sub_item_id = active_subscription['items']['data'][0]['id']

        # Check if subscription is already canceled but still active
        if active_subscription['cancel_at_period_end']:
            return jsonify({"error": "Subscription is already canceled but still active"}), 400

        # Modify the subscription
        stripe.Subscription.modify(
            active_subscription['id'],
            proration_behavior='none',
            items=[{
                "id": sub_item_id,
                "price_data": {
                    "currency": "eur",
                    "unit_amount": int(new_value_eur),
                    "recurring": {"interval": "month"},
                    "product": "prod_Or6dLhhP1w1avS"}
            }]
        )

        return jsonify({"message": "Subscription updated successfully"}), 200

    except stripe.error.StripeError as e:
        return jsonify({"error": f"Stripe error: {str(e)}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@investment_bp.route('/investment', methods=['GET'])
@authorize
def get_investment_details():
    try:
        user_id = request.uid
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User does not exist"}), 404
        if not user.billable:
            return jsonify({"error": "User is not billable"}), 403

        customer_id = user.stripe_id

        # Fetch active subscription details from Stripe
        active_subscriptions = stripe.Subscription.list(customer=customer_id, status='active', limit=1)

        if len(active_subscriptions) == 0:
            subscription_info = {
                "active": False,
                "monthly_rate": None
            }
        else:
            active_subscription = active_subscriptions.data[0]
            monthly_rate = active_subscription['items']['data'][0]['price']['unit_amount']
            subscription_info = {
                "active": True,
                "monthly_rate": monthly_rate
            }

        # Fetch total debited amount from Stripe charges
        charges = stripe.Charge.list(customer=customer_id)
        total_debited = sum(charge['amount'] for charge in charges)

        response_data = {
            "subscription_info": subscription_info,
            "total_debited": total_debited
        }

        return jsonify(response_data), 200

    except stripe.error.StripeError as e:
        return jsonify({"error": f"Stripe error: {str(e)}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500