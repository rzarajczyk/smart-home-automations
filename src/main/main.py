import logging
from logging import config as logging_config

import paho.mqtt.client as mqtt
import yaml
from apscheduler.schedulers.background import BackgroundScheduler

from automations.AirHumidifierAutomation import AirHumidifierAutomation
from automations.AirPurifierAutomation import AirPurifierAutomation
from automations.Automation import Publisher
from automations.EveningColorTemperatureAutomation import EveningColorTemperatureAutomation
from automations.NightLightsAutomation import NightLightsAutomation
from automations.PrinterRebootAutomation import PrinterRebootAutomation
from automations.TvRebootAutomation import TvRebootAutomation
from automations.TvTimeToSleepAutomation import TvTimeToSleepAutomation
from automations.TvVolumeAutomation import TvVolumeAutomation

########################################################################################################################
# logging configuration

with open('logging.yaml', 'r') as f:
    config = yaml.full_load(f)
    logging_config.dictConfig(config)

LOGGER = logging.getLogger("main")

########################################################################################################################
# application configuration

with open('config/smart-home-automations.yaml', 'r') as f:
    config = yaml.full_load(f)

    MQTT_HOST = config['mqtt']['host']
    MQTT_PORT = config['mqtt']['port']
    MQTT_USER = config['mqtt']['user']
    MQTT_PASS = config['mqtt']['password']

    MQTT_SETTINGS = {
        'MQTT_BROKER': config['mqtt']['host'],
        'MQTT_PORT': config['mqtt']['port'],
        'MQTT_USERNAME': config['mqtt']['user'],
        'MQTT_PASSWORD': config['mqtt']['password'],
        'MQTT_SHARE_CLIENT': True
    }

    SERVICES_CONFIG = config['services']

########################################################################################################################
# core logic

client = mqtt.Client()
publisher = Publisher(client)
client.username_pw_set(MQTT_USER, MQTT_PASS)

client.connect(MQTT_HOST, MQTT_PORT)

scheduler = BackgroundScheduler(timezone="Europe/Warsaw")

CLASSES = {
    'air-purifier': AirPurifierAutomation,
    'air-humidifier': AirHumidifierAutomation,
    'tv-volume': TvVolumeAutomation,
    'tv-time-to-sleep': TvTimeToSleepAutomation,
    'tv-reboot': TvRebootAutomation,
    'evening-lights': EveningColorTemperatureAutomation,
    'night-lights': NightLightsAutomation,
    'printer-reboot': PrinterRebootAutomation
}
AUTOMATIONS = []

for key in CLASSES:
    if key in SERVICES_CONFIG:
        automation_class = CLASSES[key]
        AUTOMATIONS.append(automation_class(MQTT_SETTINGS, SERVICES_CONFIG[key], scheduler, publisher))

for automation in AUTOMATIONS:
    automation.start()

LOGGER.info('All created services:')
for automation in AUTOMATIONS:
    LOGGER.info(' - %s' % str(automation))

scheduler.start()


def on_connect(client, userdata, flags, rc):
    LOGGER.info("Connected with result code %s" % str(rc))
    client.subscribe("homie/#")


def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode(encoding='UTF-8')
    for service in AUTOMATIONS:
        service.accept_message(topic, payload)


client.on_connect = on_connect
client.on_message = on_message

client.loop_forever()
# time.sleep(10000)
