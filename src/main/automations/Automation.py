import logging

from homie.device_base import Device_Base
from paho.mqtt.client import Client


class Publisher:
    def __init__(self, client: Client):
        self.client = client

    def publish(self, topic, payload):
        self.client.publish(topic, payload)


class MqttCollector:
    def __init__(self, topic, logger, type):
        self.topic = topic
        self.logger = logger
        self.type = type
        self.val = None

    def collect(self, topic, payload):
        if topic == self.topic:
            self.logger.debug("Message accepted: %s = %s" % (topic, payload))
            self.val = self.type(payload)

    @property
    def value(self):
        return self.val


class Automation(Device_Base):
    def __init__(self, device_id, name, mqtt_settings):
        super().__init__(device_id=device_id, name=name, mqtt_settings=mqtt_settings)
        self.logger = logging.getLogger(device_id)
        self.mqtt_collectors: list[MqttCollector] = []

    def mqtt_collect(self, topic, type=str):
        collector = MqttCollector(topic, self.logger, type)
        self.mqtt_collectors.append(collector)
        return collector

    def accept_message(self, topic, payload):
        for collector in self.mqtt_collectors:
            collector.collect(topic, payload)
