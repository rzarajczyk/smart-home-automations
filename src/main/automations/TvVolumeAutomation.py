from apscheduler.schedulers.base import BaseScheduler

from automations.Automation import Automation, Publisher
from homie_helpers import add_property_boolean, add_property_int


class TvVolumeAutomation(Automation):
    def __init__(self, mqtt_settings, config, scheduler: BaseScheduler, publisher: Publisher):
        super().__init__("tv-volume-automation", "TV Volume Protection", mqtt_settings)
        self.publisher = publisher

        self.max_volume = config['max-volume-level']

        self.is_enabled = True
        self.volume = self.mqtt_collect('homie/sony-bravia/volume/volume-level', int)

        self.property_enabled = add_property_boolean(self, "enabled",
                                                     property_name="Service is enabled",
                                                     parent_node_id="service",
                                                     set_handler=self.set_enabled)
        add_property_int(self, "interval",
                         parent_node_id="config",
                         unit="s").value = config['recalculate-interval-seconds']
        add_property_int(self, "max-volume-level", parent_node_id="config").value = self.max_volume
        self.property_enabled.value = True

        scheduler.add_job(self.run, 'interval', seconds=config['recalculate-interval-seconds'])

    def run(self):
        self.property_enabled.value = self.is_enabled
        if self.is_enabled and self.volume.value > self.max_volume:
            self.logger.info("Setting TV volume to %s" % self.max_volume)
            self.publisher.publish('homie/sony-bravia/volume/volume-level/set', self.max_volume)

    def set_enabled(self, enabled):
        self.logger.info("Setting enabled to %s" % self.is_enabled)
        self.is_enabled = bool(enabled)
