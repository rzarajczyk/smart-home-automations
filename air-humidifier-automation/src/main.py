from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from homie_helpers import MqttSettings

from bootstrap.bootstrap import start_service
from AirHumidifierAutomation import AirHumidifierAutomation

config, logger, timezone = start_service()

scheduler = BlockingScheduler(timezone=timezone)

automation = AirHumidifierAutomation(config=config['air-humidifier-automation'], mqtt_settings=MqttSettings.from_dict(config['mqtt']))

scheduler.add_job(automation.run, CronTrigger.from_crontab(config['air-humidifier-automation']['shutdown-schedule'], timezone))
scheduler.start()