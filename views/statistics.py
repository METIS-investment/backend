from datetime import datetime, timedelta
import calendar
from sqlalchemy import func, and_
from models import Investment, Evaluation, Profit, User
from extensions import db
from authorization import authorize
import stripe
from flask import request, jsonify, Blueprint

statistics_bp = Blueprint('statistics', __name__)


@statistics_bp.route('/investment/statistics', methods=['GET'])
@authorize
def get_investment_statistics():
    try:
        user_id = request.uid

        # Retrieve stripe_id and billable status from the database
        user = User.query.filter_by(id=user_id).first()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        if not user.billable:
            return jsonify({'error': 'User is not billable'}), 403

        stripe_id = user.stripe_id

        # Get time interval parameters from request
        start_year = int(request.args.get('start_year'))
        start_month = int(request.args.get('start_month'))
        end_year = int(request.args.get('end_year'))
        end_month = int(request.args.get('end_month'))

        # Calculate user's profit
        user_profit = calculate_user_profit(start_year, start_month, end_year, end_month, stripe_id)

        if user_profit is not None:
            return jsonify({'user_profit': user_profit}), 200
        else:
            return jsonify({'error': 'An error occurred while calculating user profit'}), 500

    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500


#######    utilities     #######
def calculate_user_profit(start_year, start_month, end_year, end_month, stripe_customer_id):
    try:
        # Initialize variables
        total_user_profit = 0
        current_year = start_year
        current_month = start_month

        while (current_year, current_month) <= (end_year, end_month):
            # Calculate the user's gain for the current month
            user_gain = calculate_user_gain(current_year, current_month, stripe_customer_id)

            if user_gain is not None:
                total_user_profit += user_gain

            # Increment the current month and check for year rollover
            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1

        return total_user_profit

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


def calculate_user_gain(year, month, stripe_customer_id):
    try:
        # Get the total gains for the month
        total_gains = calculate_total_gains(year, month)  # Assuming you have a function that does this

        # Calculate the share of gains allocated to users (60% of total gains)
        allocated_gains = 0.6 * total_gains

        # Calculate the user's share of payments for the month
        user_payment_fraction = calculate_user_share(year, month, stripe_customer_id)  # Assuming you have implemented this

        # Calculate the user's gain for the month, as part of the 60% of total gains
        user_gain = user_payment_fraction * allocated_gains

        return user_gain

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


def calculate_user_share(year, month, stripe_customer_id):
    try:
        # Define the date range for the given month
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month, calendar.monthrange(year, month)[1])
        start_timestamp = int(start_date.timestamp())
        end_timestamp = int(end_date.timestamp())

        # Fetch all transactions to us for that month
        all_transactions = stripe.Charge.list(created={"gte": start_timestamp, "lt": end_timestamp})

        # Fetch all transactions from that user for that month
        user_transactions = stripe.Charge.list(
            customer=stripe_customer_id,
            created={"gte": start_timestamp, "lt": end_timestamp}
        )

        # Calculate the sum of all transactions to us
        total_amount = sum(charge['amount'] for charge in all_transactions)

        # Calculate the sum of all transactions from that user to us
        user_amount = sum(charge['amount'] for charge in user_transactions)

        # Compute the fraction of the user's payments to us
        fraction = user_amount / total_amount if total_amount != 0 else 0

        return fraction

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


def calculate_value_gain(year, month):
    try:
        # Initialize total gain variable
        total_gain = 0

        # Define the date range for the given month
        start_date = datetime(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = datetime(year, month, last_day)

        # 1. Find companies with investments
        investments = Investment.query.all()

        for investment in investments:
            company_id = investment.company
            share = investment.share

            # 2a. Find the latest evaluation before this month
            prev_eval = Evaluation.query.filter(
                and_(
                    Evaluation.company == company_id,
                    Evaluation.time < start_date
                )
            ).order_by(Evaluation.time.desc()).first()

            # 2b. Find the latest evaluation of this month
            current_eval = Evaluation.query.filter(
                and_(
                    Evaluation.company == company_id,
                    Evaluation.time >= start_date,
                    Evaluation.time <= end_date
                )
            ).order_by(Evaluation.time.desc()).first()

            if prev_eval is not None and current_eval is not None:
                # 3. Calculate value increase
                value_diff = current_eval.assets - prev_eval.assets
                value_diff += current_eval.revenue - prev_eval.revenue
                value_diff -= current_eval.liability - prev_eval.liability

                # 5. Calculate our share in the increase
                value_diff *= share
                total_gain += value_diff

            # 4. Sum Profit for the current month
            profits = Profit.query.filter(
                and_(
                    Profit.company == company_id,
                    Profit.time >= start_date,
                    Profit.time <= end_date
                )
            ).all()
            total_profit = sum(p.amount for p in profits)
            total_gain += total_profit * share

        return total_gain

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None