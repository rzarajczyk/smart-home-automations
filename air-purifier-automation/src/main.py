from apscheduler.schedulers.blocking import BlockingScheduler
from homie_helpers import MqttSettings

from AirPurifierAutomation import AirPurifierAutomation
from bootstrap.bootstrap import start_service

config, logger, timezone = start_service()

scheduler = BlockingScheduler(timezone=timezone)

automation = AirPurifierAutomation(config=config['air-purifier-automation'], mqtt_settings=MqttSettings.from_dict(config['mqtt']))

scheduler.add_job(automation.run, 'interval', seconds=config['air-purifier-automation']['recalculate-interval-seconds'])
scheduler.start()