# app/mom/client.py
import json
import threading
import logging
import time
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
from app.configs.config import Config

logger = logging.getLogger(__name__)

class MessageBroker:
    def __init__(self, app=None):
        self.app = app
        self.mongo_uri = Config.MONGO_URI
        self.database_name = Config.MONGO_DB_NAME
        self.client = None
        self.db = None
        self.consumers = {}
        self.should_stop = False
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializar con la aplicación Flask"""
        self.app = app
        self.mongo_uri = Config.MONGO_URI
        self.database_name = Config.MONGO_DB_NAME
        
        # Conectar a MongoDB
        self._connect()
        
        # Crear índices para mejorar rendimiento
        self._create_indexes()
        
        # Limpiar conexiones al cerrar la app
        @app.teardown_appcontext
        def close_connection(exception):
            self.close()
    
    def _connect(self):
        """Establecer conexión con MongoDB"""
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client[self.database_name]
            logger.info(f"Conectado a MongoDB en {self.mongo_uri}")
        except Exception as e:
            logger.error(f"Error al conectar con MongoDB: {e}")
            raise
    
    def _create_indexes(self):
        """Crear índices para mejorar rendimiento"""
        try:
            # Índice para buscar mensajes no procesados por cola
            self.db.messages.create_index([
                ('queue', 1),
                ('processed', 1),
                ('created_at', 1)
            ])
            logger.info("Índices creados en la colección de mensajes")
        except Exception as e:
            logger.error(f"Error al crear índices: {e}")
    
    def publish(self, queue, message):
        """Publicar un mensaje en una cola"""
        if self.db != None:
            self._connect()
        
        try:
            # Crear documento de mensaje
            message_doc = {
                'queue': queue,
                'message': message,
                'created_at': datetime.utcnow(),
                'processed': False,
                'processed_at': None
            }
            
            # Insertar en la colección
            result = self.db.messages.insert_one(message_doc)
            logger.debug(f"Mensaje publicado en cola {queue} con ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error al publicar mensaje: {e}")
            raise
    
    def register_consumer(self, queue, callback):
        """Registrar un consumidor para una cola"""
        if self.db != None:
            self._connect()
        
        # Consumir mensajes en un hilo separado
        def consumer_thread():
            logger.info(f"Iniciando consumo de cola {queue}")
            while not self.should_stop:
                try:
                    # Buscar y marcar un mensaje como en proceso
                    # Usamos find_one_and_update para garantizar operación atómica
                    message_doc = self.db.messages.find_one_and_update(
                        {
                            'queue': queue,
                            'processed': False
                        },
                        {
                            '$set': {
                                'processing': True,
                                'processing_started_at': datetime.utcnow()
                            }
                        },
                        sort=[('created_at', 1)]
                    )
                    
                    if message_doc:
                        try:
                            # Extraer mensaje y procesar
                            message = message_doc['message']
                            callback(message)
                            
                            # Marcar como procesado exitosamente
                            self.db.messages.update_one(
                                {'_id': message_doc['_id']},
                                {
                                    '$set': {
                                        'processed': True,
                                        'processed_at': datetime.utcnow(),
                                        'processing': False
                                    }
                                }
                            )
                            logger.debug(f"Mensaje {message_doc['_id']} procesado exitosamente")
                        except Exception as e:
                            # Error al procesar el mensaje
                            logger.error(f"Error al procesar mensaje {message_doc['_id']}: {e}")
                            
                            # Marcar como fallido
                            self.db.messages.update_one(
                                {'_id': message_doc['_id']},
                                {
                                    '$set': {
                                        'processing': False,
                                        'error': str(e),
                                        'error_at': datetime.utcnow()
                                    }
                                }
                            )
                    else:
                        # No hay mensajes, esperar
                        time.sleep(1)
                except Exception as e:
                    logger.error(f"Error en el consumidor de {queue}: {e}")
                    # Pausa para evitar ciclos de error intensivos
                    time.sleep(1)
        
        thread = threading.Thread(target=consumer_thread)
        thread.daemon = True
        thread.start()
        
        # Guardar referencia al hilo
        self.consumers[queue] = thread
        logger.info(f"Consumidor registrado para cola {queue}")
    
    def get_queue_status(self, queue):
        """Obtener estadísticas de una cola"""
        if self.db != None:
            self._connect()
            
        try:
            pending = self.db.messages.count_documents({
                'queue': queue,
                'processed': False
            })
            
            processing = self.db.messages.count_documents({
                'queue': queue,
                'processing': True
            })
            
            processed = self.db.messages.count_documents({
                'queue': queue,
                'processed': True
            })
            
            failed = self.db.messages.count_documents({
                'queue': queue,
                'error': {'$exists': True}
            })
            
            return {
                'queue': queue,
                'pending': pending,
                'processing': processing,
                'processed': processed,
                'failed': failed,
                'total': pending + processing + processed
            }
        except Exception as e:
            logger.error(f"Error al obtener estado de la cola {queue}: {e}")
            raise
    
    def retry_failed(self, queue, limit=100):
        """Reintentar mensajes fallidos"""
        if self.db!= None:
            self._connect()
            
        try:
            # Buscar mensajes con error
            result = self.db.messages.update_many(
                {
                    'queue': queue,
                    'error': {'$exists': True}
                },
                {
                    '$set': {
                        'processed': False,
                        'processing': False
                    },
                    '$unset': {
                        'error': "",
                        'error_at': ""
                    }
                },
                limit=limit
            )
            
            return result.modified_count
        except Exception as e:
            logger.error(f"Error al reintentar mensajes fallidos: {e}")
            raise
    
    def close(self):
        """Cerrar conexiones"""
        self.should_stop = True
        # Esperar a que los hilos terminen
        for queue, thread in self.consumers.items():
            if thread.is_alive():
                thread.join(timeout=1)
        
        # Cerrar conexión con MongoDB
        if self.client:
            self.client.close()
            logger.info("Conexión con MongoDB cerrada")