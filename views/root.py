from flask import Blueprint, jsonify, request

root_bp = Blueprint('root', __name__)


@root_bp.route('/')
def hello_world():  # put application's code here
    return jsonify({"message": "This is the METIS Investment API."}), 200