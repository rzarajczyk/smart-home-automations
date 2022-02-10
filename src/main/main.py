import logging
import os
import shutil
from logging import config as logging_config

import paho.mqtt.client as mqtt
import yaml
from apscheduler.schedulers.background import BackgroundScheduler

from services.AirPurifierService import AirPurifierService
from services.Service import Publisher

ROOT = os.environ.get('APP_ROOT', ".")

########################################################################################################################
# logging configuration

LOGGER_CONFIGURATION = "%s/config/logging.yaml" % ROOT
if not os.path.isfile(LOGGER_CONFIGURATION):
    shutil.copy("%s/config-defaults/logging.yaml" % ROOT, LOGGER_CONFIGURATION)

with open(LOGGER_CONFIGURATION, 'r') as f:
    config = yaml.full_load(f)
    logging_config.dictConfig(config)

LOGGER = logging.getLogger("main")

########################################################################################################################
# application configuration

CONFIGURATION = "%s/config/application.yaml" % ROOT
if not os.path.isfile(CONFIGURATION):
    shutil.copy("%s/config-defaults/application.yaml" % ROOT, CONFIGURATION)

with open(CONFIGURATION, 'r') as f:
    config = yaml.full_load(f)

    MQTT_HOST = config['mqtt']['host']
    MQTT_PORT = config['mqtt']['port']
    MQTT_USER = config['mqtt']['user']
    MQTT_PASS = config['mqtt']['password']

    SERVICES_CONFIG = config['services']

########################################################################################################################
# core logic

client = mqtt.Client()
publisher = Publisher(client)
client.username_pw_set(MQTT_USER, MQTT_PASS)

client.connect(MQTT_HOST, MQTT_PORT)

scheduler = BackgroundScheduler(timezone="Europe/Warsaw")

SERVICES = [
    AirPurifierService(SERVICES_CONFIG['air-purifier'], scheduler, publisher)
]

LOGGER.info('All created services:')
for service in SERVICES:
    LOGGER.info(' - %s' % str(service))

scheduler.start()


def on_connect(client, userdata, flags, rc):
    LOGGER.info("Connected with result code %s" % str(rc))
    client.subscribe("homie/#")


def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode(encoding='UTF-8')
    for service in SERVICES:
        service.accept_message(topic, payload)


client.on_connect = on_connect
client.on_message = on_message

client.loop_forever()
