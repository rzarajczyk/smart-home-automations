from apscheduler.schedulers.base import BaseScheduler
from apscheduler.triggers.cron import CronTrigger

from automations.Automation import Automation, Publisher
from homie_helpers import add_property_boolean, add_property_string


class AirHumidifierAutomation(Automation):
    def __init__(self, mqtt_settings, config, scheduler: BaseScheduler, publisher: Publisher):
        super().__init__("air-humidifier-automation", "Air Humidifier", mqtt_settings)
        self.publisher = publisher

        self.speed = self.mqtt_collect('homie/xiaomi-air-humidifier/speed/speed')

        self.property_enabled = add_property_boolean(self, "enabled",
                                                     parent_node_id="service",
                                                     set_handler=self.set_enabled)
        add_property_string(self, "shutdown-schedule", parent_node_id="config").value = config['shutdown-schedule']
        self.property_enabled.value = True

        scheduler.add_job(self.run, CronTrigger.from_crontab(config['shutdown-schedule'], "Europe/Warsaw"))

    def run(self):
        if self.property_enabled.value and self.speed.value != 'off':
            self.logger.info("Setting humidifier speed to off")
            self.publisher.publish('homie/xiaomi-air-humidifier/speed/speed/set', 'off')

    def set_enabled(self, enabled):
        self.logger.info("Setting enabled to %s" % enabled)
