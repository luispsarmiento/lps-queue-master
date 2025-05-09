from app.queue import broker

def example_function():
    broker.publish('orders', {
        'order_id': 123,  # ID generado
        'customer_id': 1,
        'items': ["item1", "item2"],
        'status': "pending",
        'total': 99.99
    })
    return {"message": "Hello from the controller!"}