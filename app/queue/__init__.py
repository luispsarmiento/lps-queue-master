from .client import MessageBroker

# Pre-configurar handlers comunes
from . import handlers

# Crear una instancia por defecto
broker = MessageBroker()

__all__ = ['broker', 'MessageBroker', 'handlers']
