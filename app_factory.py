import os

from flask import Flask
from extensions import db
from flask_cors import CORS
import firebase_admin
import stripe


def create_app():
    app = Flask(__name__)
    CORS(app)

    # Configurations
    firebase_admin.initialize_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URI')# 'postgresql://datagrip:ow94t8cmuo49tu8cs@34.90.69.65:5432/postgres'
    stripe.api_key = "sk_test_51O3HaIC7Nc96FuKDPP4x5n6mwanPUKYqVK9dZw0gxxBv2CB7jjN73USNWNXGcwoClL9tzDjyNGhkNS2YPUthJL4v00GNJAuVcJ"

    # Initialize extensions
    db.init_app(app)

    # Blueprints and routes can be registered here, e.g.
    from views.root import root_bp
    app.register_blueprint(root_bp)
    from views.user import user_bp
    app.register_blueprint(user_bp)
    from views.investment import investment_bp
    app.register_blueprint(investment_bp)
    from views.companies import companies_bp
    app.register_blueprint(companies_bp)
    from views.statistics import statistics_bp
    app.register_blueprint(statistics_bp)

    return app
