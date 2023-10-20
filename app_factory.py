from flask import Flask
from extensions import db
from flask_cors import CORS
from firebase_admin import credentials
import firebase_admin


def create_app():
    app = Flask(__name__)
    CORS(app)

    # Configurations
    firebaseApp = firebase_admin.initialize_app()
    #app.config['SQLALCHEMY_DATABASE_URI'] = '...'

    # Initialize extensions
    #db.init_app(app)

    # Blueprints and routes can be registered here, e.g.
    from views.root import root_bp
    app.register_blueprint(root_bp)

    return app
