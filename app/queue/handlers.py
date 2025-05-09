import logging

logger = logging.getLogger(__name__)

def process_notification(message):
    """Maneja mensajes de notificaciones"""
    logger.info(f"Procesando notificación: {message}")
    # Implementa tu lógica aquí
    # Por ejemplo, enviar un email, una notificación push, etc.

def process_order(message):
    """Maneja mensajes de órdenes"""
    logger.info(f"Procesando orden: {message}")
    # Implementa tu lógica aquí
    # Por ejemplo, actualizar el estado de una orden en la BD

def process_payment(message):
    """Maneja mensajes de pagos"""
    logger.info(f"Procesando pago: {message}")
    # Implementa tu lógica aquí
