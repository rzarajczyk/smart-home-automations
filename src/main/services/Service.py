from homie.device_base import Device_Base
from paho.mqtt.client import Client


class Publisher:
    def __init__(self, client: Client):
        self.client = client

    def publish(self, topic, payload):
        self.client.publish(topic, payload)


class Service(Device_Base):
    def __init__(self, device_id, name, mqtt_settings):
        super().__init__(device_id=device_id, name=name, mqtt_settings=mqtt_settings)

    def accept_message(self, topic, payload):
        pass
