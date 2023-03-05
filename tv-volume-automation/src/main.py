from apscheduler.schedulers.blocking import BlockingScheduler
from homie_helpers import MqttSettings

from bootstrap.bootstrap import start_service
from TvVolumeAutomation import TvVolumeAutomation

config, logger, timezone = start_service()

scheduler = BlockingScheduler(timezone=timezone)

automation = TvVolumeAutomation(config=config['tv-volume'], mqtt_settings=MqttSettings.from_dict(config['mqtt']))

scheduler.add_job(automation.run, 'interval', seconds=config['tv-volume']['recalculate-interval-seconds'])
scheduler.start()