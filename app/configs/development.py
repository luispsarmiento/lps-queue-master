import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    
    # Configuración del broker de colas
    QUEUE_BROKER_URL = os.environ.get('QUEUE_BROKER_URL') or 'localhost'

DEBUG = True
SECRET_KEY = 'your-development-secret-key'