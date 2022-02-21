import logging

from apscheduler.schedulers.base import BaseScheduler

from automations.Automation import Automation, Publisher
from homie_helpers import PropertyType
from homie_helpers import add_property


class TvVolumeAutomation(Automation):
    def __init__(self, mqtt_settings, config, scheduler: BaseScheduler, publisher: Publisher):
        super().__init__("tv-volume-automation", "TV Volume Automation", mqtt_settings)
        self.publisher = publisher
        self.logger = logging.getLogger("TvVolumeAutomation")
        self.max_volume = config['max-volume-level']

        self.is_enabled = True
        self.volume = 0

        self.property_enabled = add_property(self, PropertyType.IS_ENABLED, set_handler=self.set_enabled)

        self.start()
        scheduler.add_job(self.run, 'interval', seconds=config['recalculate-interval-seconds'])
        self.property_enabled.value = True

    def accept_message(self, topic, payload):
        if topic == 'homie/sony-bravia/volume/volume-level':
            self.logger.debug("Message received: %-70s | %s" % (topic, payload))
            self.volume = int(payload)

    def run(self):
        self.property_enabled.value = self.is_enabled
        if self.is_enabled and self.volume > self.max_volume:
            self.logger.info("Setting TV volume to %s" % self.max_volume)
            self.publisher.publish('homie/sony-bravia/volume/volume-level/set', self.max_volume)

    def set_enabled(self, enabled):
        self.logger.info("Setting enabled to %s" % self.is_enabled)
        self.is_enabled = bool(enabled)
