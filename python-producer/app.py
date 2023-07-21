from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer,AvroConsumer
from faker import Faker
import json
import time
import logging
import random
import os
from flask import Flask

fake=Faker()

# Define the Avro schema
avro_schema_str = '''
{
  "type": "record",
  "name": "user",
  "fields": [
    {"name": "user_name", "type": "string"},
    {"name": "user_address", "type": "string"},
    {"name": "platform", "type": "string"},
    {"name": "signup_at", "type": "string"},
    {"name": "user_id", "type": "int"}
  ]
}
'''

# key_avro_schema_str = '''
# {
#   "type": "record",
#   "name": "Key",
#   "fields": [
#     {"name": "id", "type": "string"}
#   ]
# }
# '''

key_avro_schema_str = '''
{
  "type": "record",
  "name": "Key",
  "fields": [
    {"name": "key", "type": "string"}
  ]
}
'''

# Create an Avro schema object
avro_schema = avro.loads(avro_schema_str)
key_avro_schema = avro.loads(key_avro_schema_str)

logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)

# Configuración del productor y consumidor de Kafka
bootstrap_servers = 'kafka:9092'

bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS","localhost:9092")
schema_registry_url=os.getenv("SCHEMA_REGISTRY_URL","http://localhost:8081")
kafka_topic=os.getenv("KAFKA_TOPIC","user-tracker")
fake_users_count=10

producer=None
consumer=None




# Función para verificar la conexión con Kafka
def kafka_connection():
    global producer,consumer

    connected = False
    while not connected:
        try:
            producer_config = {
                'bootstrap.servers': bootstrap_servers,
                'schema.registry.url': schema_registry_url,
                "allow.auto.create.topics":True
                }
            # producer = AvroProducer(producer_config, default_value_schema=avro_schema)
            producer = AvroProducer(producer_config, default_value_schema=avro_schema,default_key_schema=key_avro_schema)

            consumer_config = {
                'bootstrap.servers': bootstrap_servers,
                'group.id': 'my_group',
                'schema.registry.url': schema_registry_url,
                "allow.auto.create.topics":True,
                'auto.offset.reset': 'earliest'
                }

            consumer = AvroConsumer(consumer_config)

            connected = True
            logger.info(f'Conexion con Kafka exitosa :)')

        except Exception as e:
            logger.info(f'Error al conectar con Kafka: {e}')
            time.sleep(1)  # Esperar 1 segundo antes de volver a intentar

def insert_callback(err,msg):
    logger.info(f"Se inserto en kafka: {msg}")

def generate_random_user():
    return {
           'user_id': fake.random_int(min=20000, max=100000),
           'user_name':fake.name(),
           'user_address':fake.street_address() + ' | ' + fake.city() + ' | ' + fake.country_code(),
           'platform': random.choice(['Mobile', 'Laptop', 'Tablet']),
           'signup_at': str(fake.date_time_this_month())    
           }

def insert_fake_users():
    global kafka_topic,fake_users_count

    logger.info("Insertando usuarios fake ...")

    for i in range(fake_users_count):
        logger.info("Generando usuario fake ...")

        data = generate_random_user()

        logger.info("Insertando usuario generado ...")

        key_message = {"key": f"user-{data['user_id']}"}  # Replace "your_string_key" with your desired key data

        # Produce the message to Kafka
        producer.produce(topic=kafka_topic, key=key_message,value=data,callback=insert_callback)

        # Flush the producer to ensure all messages are sent
        producer.flush()

    logger.info('Datos insertados en Kafka')

    # Close the producer
    # producer.close()

def message_to_user(message):
    return message.value()

def read_fake_users():
    global kafka_topic

    logger.info("Obteniendo usuarios ...")
    
    consumer.subscribe([kafka_topic])
    f_users=[]

    while True:
        message = consumer.poll(1.0)

        if message is None:
            break
        if message.error():
            logger.info('Error al recibir mensaje: {}'.format(message.error()))
            break

        user = message_to_user(message)

        logger.info(f'Mensaje recibido: {user}')

        f_users.append(user)

    # Close the consumer when done
    # consumer.close()

    return f_users

@app.route('/insert', methods=['GET'])
def post_users():
    insert_fake_users()
    return "OK"

@app.route('/list', methods=['GET'])
def get_users():
    f_users=read_fake_users()
    return json.dumps(f_users)

@app.route('/reconnect', methods=['GET'])
def reconnect():
    kafka_connection()
    return "OK"

kafka_connection()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
