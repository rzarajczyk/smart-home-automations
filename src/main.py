import paho.mqtt.client as mqtt
from apscheduler.schedulers.background import BackgroundScheduler
from bootstrap.bootstrap import start_service

from automations.AirHumidifierAutomation import AirHumidifierAutomation
from automations.AirPurifierAutomation import AirPurifierAutomation
from automations.Automation import Publisher
from automations.TvTimeToSleepAutomation import TvTimeToSleepAutomation
from automations.TvVolumeAutomation import TvVolumeAutomation

config, logger, timezone = start_service()

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
}
AUTOMATIONS = []

for key in CLASSES:
    if key in SERVICES_CONFIG:
        automation_class = CLASSES[key]
        AUTOMATIONS.append(automation_class(MQTT_SETTINGS, SERVICES_CONFIG[key], scheduler, publisher))

for automation in AUTOMATIONS:
    automation.start()

logger.info('All created services:')
for automation in AUTOMATIONS:
    logger.info(' - %s' % str(automation))

scheduler.start()


def on_connect(client, userdata, flags, rc):
    logger.info("Connected with result code %s" % str(rc))
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
