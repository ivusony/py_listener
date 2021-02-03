import pika
import logging
import json

# LOGGER configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s :	%(asctime)s : %(name)s: %(message)s')
file_handler = logging.FileHandler('../logs/connected.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# import amqp urls
config = open("./amqp.config.json")

class Sender:
    def __init__(self, production):
        self.is_production = production
        self.protocol = "amqp"
        self.mq_url = None
        self.is_connected_to_queue = False

        if self.is_production:
            self.mq_url = json.load(config)["production"]
        else:
            self.mq_url = json.load(config)["development"]
    
    def production(self):
        return self.is_production

    def check_connection(self):
        try:
            pika.BlockingConnection(pika.URLParameters(self.mq_url))
            if self.is_production:
                print('Connected to rabbitmq')
            else:
                print('Connected to test rabbit mq')
            self.is_connected_to_queue = True
        except Exception:
            self.is_connected_to_queue = False

    def forward_to_queue(self, msg, imei):
        try:
            # print(f"[sender] Sending data to queue")
            connection = pika.BlockingConnection(pika.URLParameters(self.mq_url))
            channel = connection.channel()
            # channel.queue_declare(queue='f1')
            
            channel.exchange_declare(
                exchange="exchange_name",
                # exchange_type="x-random",
                exchange_type="direct",
                durable=True
            )
            # channel.queue_bind(
            #     exchange="f1-listener",
            #     queue="f1"
            # )
            channel.basic_publish(
                exchange="exchange_name",
                routing_key="",
                body=msg,
                # arguments={
                #     'x-message-ttl' : '60000'
                # }
                properties=pika.BasicProperties(
                    expiration="60000"
                )
            )
            # logger.info(f"AVL from device IMEI {imei} sent to exchange")
            connection.close()
        except Exception:
            logger.critical('CONNECTION TO EXCHANGE FAILED')