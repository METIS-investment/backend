from flask import Flask
from extensions import db
from flask_cors import CORS
import firebase_admin


def create_app():
    app = Flask(__name__)
    CORS(app)

    # Configurations
    firebase_admin.initialize_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://datagrip:ow94t8cmuo49tu8cs@34.90.69.65:5432/postgres'

    # Initialize extensions
    db.init_app(app)

    # Blueprints and routes can be registered here, e.g.
    from views.root import root_bp
    app.register_blueprint(root_bp)
    from views.user import user_bp
    app.register_blueprint(user_bp)

    return app
