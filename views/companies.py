from datetime import datetime
from flask import Blueprint, jsonify, request
from extensions import db
from authorization import authorize
from sqlalchemy.exc import IntegrityError
from models import Company, Evaluation  # Add this import

companies_bp = Blueprint('companies', __name__)


@companies_bp.route('/company/register', methods=['POST'])
@authorize
def company_register():
    try:
        data = request.json

        # Validate input data
        mandatory_fields = ['name', 'country', 'city', 'street', 'incorporation_date', 'evaluation_0']
        for field in mandatory_fields:
            if field not in data:
                return jsonify({'error': f'Missing {field}'}), 400

        # Get company_id from request
        company_id = request.uid

        # Create company record
        new_company = Company(id=company_id,
                              name=data['name'],
                              country=data['country'],
                              city=data['city'],
                              street=data['street'],
                              incorporation_date=datetime.fromisoformat(data['incorporation_date']))
        db.session.add(new_company)

        # Create evaluation records
        for i in range(5):  # Loop from evaluation_0 to evaluation_4
            key = f'evaluation_{i}'
            if key in data:
                eval_data = data[key]
                new_evaluation = Evaluation(company=company_id,
                                            profit=eval_data['profit'],
                                            revenue=eval_data['revenue'],
                                            assets=eval_data['assets'],
                                            liability=eval_data['liability'],
                                            time=datetime.fromisoformat(eval_data['time']))
                db.session.add(new_evaluation)

        # Commit changes
        db.session.commit()
        return jsonify({'success': 'Company and evaluations added successfully', 'company_id': company_id}), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Integrity error, possibly duplicate data'}), 409

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500