from datetime import datetime, timedelta
import calendar
from sqlalchemy import func, and_
from models import Investment, Evaluation, Profit, User
from extensions import db
from authorization import authorize
import stripe
from flask import request, jsonify, Blueprint

statistics_bp = Blueprint('statistics', __name__)


@statistics_bp.route('/investment/balance', methods=['GET'])
@authorize
def total_balance_user():
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
        user_investment, monthly_investment = user_investment_range(start_year, start_month, end_year, end_month, stripe_id)
        user_profit, monthly_profits = user_profit_range(start_year, start_month, end_year, end_month, stripe_id)
        balance = user_investment+user_profit
        monthly_balance = [a_i + b_i for a_i, b_i in zip(monthly_investment, monthly_profits)]

        if user_profit is not None:
            return jsonify({'total_balance': balance, 'monthly_balance': monthly_balance}), 200
        else:
            return jsonify({'error': 'An error occurred while calculating user profit'}), 500

    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500


@statistics_bp.route('/investment/investment', methods=['GET'])
@authorize
def total_investment_user():
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
        user_profit, monthly_profits = user_investment_range(start_year, start_month, end_year, end_month, stripe_id)

        if user_profit is not None:
            return jsonify({'total_investment': user_profit, 'monthly_investments': monthly_profits}), 200
        else:
            return jsonify({'error': 'An error occurred while calculating user profit'}), 500

    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500


@statistics_bp.route('/investment/profits', methods=['GET'])
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
        user_profit, monthly_profits = user_profit_range(start_year, start_month, end_year, end_month, stripe_id)

        if user_profit is not None:
            return jsonify({'user_profit': user_profit, 'monthly_profits': monthly_profits}), 200
        else:
            return jsonify({'error': 'An error occurred while calculating user profit'}), 500

    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500


#######    utilities     #######
def user_profit_range(start_year, start_month, end_year, end_month, stripe_customer_id):
    try:
        # Initialize variables
        total_user_profit = 0
        monthly_profits = {}
        current_year = start_year
        current_month = start_month

        while (current_year, current_month) <= (end_year, end_month):
            # Calculate the user's gain for the current month
            user_gain = user_profit_in_month(current_year, current_month, stripe_customer_id)

            if user_gain is not None:
                total_user_profit += user_gain
                monthly_key = f"{current_year}-{str(current_month).zfill(2)}"
                monthly_profits[monthly_key] = user_gain

            # Increment the current month and check for year rollover
            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1

        return total_user_profit, monthly_profits

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None, None


def user_investment_range(start_year, start_month, end_year, end_month, stripe_customer_id):
    try:
        # Initialize variables
        total_user_profit = 0
        monthly_profits = {}
        current_year = start_year
        current_month = start_month

        while (current_year, current_month) <= (end_year, end_month):
            # Calculate the user's gain for the current month
            user_gain = user_investment_in_month(current_year, current_month, stripe_customer_id)

            if user_gain is not None:
                total_user_profit += user_gain
                monthly_key = f"{current_year}-{str(current_month).zfill(2)}"
                monthly_profits[monthly_key] = user_gain

            # Increment the current month and check for year rollover
            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1

        return total_user_profit, monthly_profits

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None, None


def user_profit_in_month(year, month, stripe_customer_id):
    try:
        # Get the total gains for the month
        total_gains = total_profit_in_month(year, month)

        # Calculate the share of gains allocated to users (60% of total gains)
        allocated_gains = 0.6 * total_gains

        # Calculate the user's share of payments for the month
        user_payment_fraction = user_profit_share_in_month(year, month, stripe_customer_id)  # Assuming you have implemented this

        # Calculate the user's gain for the month, as part of the 60% of total gains
        user_gain = user_payment_fraction * allocated_gains

        return user_gain

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


def user_investment_in_month(year, month, stripe_customer_id):
    try:
        # Define the start and end dates for the given month and year
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month, calendar.monthrange(year, month)[1])

        # Convert these dates to Unix timestamps
        start_timestamp = int(start_date.timestamp())
        end_timestamp = int(end_date.timestamp())

        # Initialize total payment variable
        total_payment = 0

        # Fetch Stripe charges for the given customer ID and date range
        charges = stripe.Charge.list(
            customer=stripe_customer_id,
            created={
                'gte': start_timestamp,
                'lte': end_timestamp
            }
        )

        # Sum up all the payments made by the customer
        for charge in charges:
            if charge['status'] == 'succeeded':  # Only consider successful charges
                total_payment += charge['amount']

        return total_payment

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


def total_investment_in_month(year, month):
    try:
        # Define the start and end dates for the given month and year
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month, calendar.monthrange(year, month)[1])

        # Convert these dates to Unix timestamps
        start_timestamp = int(start_date.timestamp())
        end_timestamp = int(end_date.timestamp())

        # Initialize total payment variable
        total_payment = 0

        # Fetch Stripe charges for the given customer ID and date range
        charges = stripe.Charge.list(
            created={
                'gte': start_timestamp,
                'lte': end_timestamp
            }
        )

        # Sum up all the payments made by the customer
        for charge in charges:
            if charge['status'] == 'succeeded':  # Only consider successful charges
                total_payment += charge['amount']

        return total_payment

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


def user_profit_share_in_month(year, month, stripe_customer_id):
    try:
        # Define the date range for the given month
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month, calendar.monthrange(year, month)[1])
        start_timestamp = int(start_date.timestamp())
        end_timestamp = int(end_date.timestamp())

        # Calculate the sum of all transactions to us
        total_amount = total_investment_in_month(year, month)

        # Calculate the sum of all transactions from that user to us
        user_amount = user_investment_in_month(year, month, stripe_customer_id)

        # Compute the fraction of the user's payments to us
        fraction = user_amount / total_amount if total_amount != 0 else 0

        return fraction

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


def total_profit_in_month(year, month):
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