from flask import Blueprint
from app.controllers.example_controller import example_function

example_bp = Blueprint('example', __name__)

@example_bp.route('/example', methods=['GET'])
def example_route():
    return example_function()