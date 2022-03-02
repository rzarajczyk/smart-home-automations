from apscheduler.schedulers.base import BaseScheduler
from apscheduler.triggers.cron import CronTrigger

from automations.Automation import Automation, Publisher
from homie_helpers import add_property_boolean, add_property_string


class TvRebootAutomation(Automation):
    def __init__(self, mqtt_settings, config, scheduler: BaseScheduler, publisher: Publisher):
        super().__init__("tv-reboot-automation", "TV Reboot", mqtt_settings)
        self.publisher = publisher

        self.property_enabled = add_property_boolean(self, "enabled",
                                                     parent_node_id="service",
                                                     set_handler=self.set_enabled)
        add_property_string(self, "schedule", parent_node_id="config").value = config['schedule']
        add_property_boolean(self, "run",
                             property_name="Run now",
                             parent_node_id="service",
                             retained=False,
                             set_handler=self.run_now)
        self.property_enabled.value = True

        scheduler.add_job(self.run, CronTrigger.from_crontab(config['schedule'], "Europe/Warsaw"))

    def run(self):
        if self.property_enabled.value:
            self.run_now(True)

    def set_enabled(self, enabled):
        self.logger.info("Setting enabled to %s" % enabled)

    def run_now(self, value):
        if value:
            self.logger.info("Rebooting TV")
            self.publisher.publish('homie/sony-bravia/power/reboot/set', "true")
