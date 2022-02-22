import logging

from apscheduler.schedulers.base import BaseScheduler
from apscheduler.triggers.cron import CronTrigger

from automations.Automation import Automation, Publisher
from homie_helpers import add_property_boolean, add_property_string


class TvTimeToSleepAutomation(Automation):
    def __init__(self, mqtt_settings, config, scheduler: BaseScheduler, publisher: Publisher):
        super().__init__("tv-time-to-sleep-automation", "TV Time to sleep", mqtt_settings)
        self.publisher = publisher
        self.logger = logging.getLogger("TvTimeToSleepAutomation")

        self.url = config['image-url']

        self.is_enabled = True
        self.tv_is_on = False

        self.property_enabled = add_property_boolean(self, "enabled",
                                                     parent_node_id="service",
                                                     set_handler=self.set_enabled)

        add_property_boolean(self, "run",
                             property_name="Run now",
                             parent_node_id="service",
                             retained=False,
                             set_handler=self.run_now)
        add_property_string(self, "schedule", parent_node_id="config").value = config['schedule']
        add_property_string(self, "url", parent_node_id="config").value = config['image-url']

        self.start()
        scheduler.add_job(self.run, CronTrigger.from_crontab(config['schedule']))
        self.property_enabled.value = True

    def accept_message(self, topic, payload):
        if topic == 'homie/sony-bravia/power/power-status':
            self.logger.debug("Message received: %-70s | %s" % (topic, payload))
            self.tv_is_on = payload == 'active'

    def run(self):
        self.property_enabled.value = self.is_enabled
        if self.tv_is_on:
            self.run_now(True)

    def set_enabled(self, enabled):
        self.logger.info("Setting enabled to %s" % self.is_enabled)
        self.is_enabled = bool(enabled)

    def run_now(self, value):
        if value:
            self.logger.info("Showing Time-to-Sleep image: %s" % self.url)
            self.publisher.publish('homie/sony-bravia/player/cast/set', self.url)
