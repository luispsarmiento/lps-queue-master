from flask import Flask
from .queue import broker
import logging

logging.basicConfig(
    level=logging.INFO,  # Set the logging level to INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Log to the console
        logging.FileHandler('app.log')  # Log to a file
    ]
)

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.configs.development')  # Default to development config
    
    # Inicializar el broker de colas
    broker.init_app(app)
    
    # Registrar blueprints
    from app.routes.example_routes import example_bp
    app.register_blueprint(example_bp)
    
    # Registrar consumidores de mensajes
    from .queue import handlers
    broker.register_consumer('notifications', handlers.process_notification)
    broker.register_consumer('orders', handlers.process_order)
    broker.register_consumer('payments', handlers.process_payment)
    
    return app