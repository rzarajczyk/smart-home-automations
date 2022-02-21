import logging

from apscheduler.schedulers.base import BaseScheduler
from apscheduler.triggers.cron import CronTrigger

from homie_helpers import PropertyType
from homie_helpers import add_property
from automations.Automation import Automation, Publisher


class AirHumidifierAutomation(Automation):
    def __init__(self, mqtt_settings, config, scheduler: BaseScheduler, publisher: Publisher):
        super().__init__("air-humidifier-automation", "Air Humidifier Automation", mqtt_settings)
        self.publisher = publisher
        self.logger = logging.getLogger("AirHumidifierAutomation")

        self.is_enabled = True
        self.speed = None

        self.property_enabled = add_property(self, PropertyType.IS_ENABLED, set_handler=self.set_enabled)

        self.start()
        scheduler.add_job(self.run, CronTrigger.from_crontab(config['shutdown-schedule']))
        self.property_enabled.value = True

    def accept_message(self, topic, payload):
        if topic == 'homie/xiaomi-air-humidifier/speed/speed':
            self.speed = payload
            self.logger.debug("Message received: %-70s | %s" % (topic, payload))

    def run(self):
        self.property_enabled.value = self.is_enabled
        if self.is_enabled and self.speed != 'off':
            self.publisher.publish('homie/xiaomi-air-humidifier/speed/speed/set', 'off')

    def set_enabled(self, enabled):
        self.is_enabled = bool(enabled)
        self.logger.info("Setting enabled to %s" % self.is_enabled)
