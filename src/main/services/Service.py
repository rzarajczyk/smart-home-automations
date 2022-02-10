from paho.mqtt.client import Client


class Publisher:
    def __init__(self, client: Client):
        self.client = client

    def publish(self, topic, payload):
        self.client.publish(topic, payload)


class Service:
    def accept_message(self, topic, payload):
        pass
