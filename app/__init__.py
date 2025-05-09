from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.configs.development')  # Default to development config

    # Import and register blueprints here
    from app.routes.example_routes import example_bp
    app.register_blueprint(example_bp)

    return app