from apscheduler.schedulers.base import BaseScheduler
from apscheduler.triggers.cron import CronTrigger

from automations.Automation import Automation, Publisher
from homie_helpers import add_property_boolean, add_property_string


class TvTimeToSleepAutomation(Automation):
    def __init__(self, mqtt_settings, config, scheduler: BaseScheduler, publisher: Publisher):
        super().__init__("tv-time-to-sleep-automation", "TV Time to sleep", mqtt_settings)
        self.publisher = publisher

        self.url = config['image-url']

        self.tv_is_on = self.mqtt_collect('homie/sony-bravia/power/ison', lambda ison: ison == 'true')

        self.property_enabled = add_property_boolean(self, "enabled",
                                                     parent_node_id="service",
                                                     set_handler=self.set_enabled,
                                                     initial_value=True)
        add_property_boolean(self, "run",
                             property_name="Run now",
                             parent_node_id="service",
                             retained=False,
                             set_handler=self.run_now)
        add_property_string(self, "schedule", parent_node_id="config").value = config['schedule']
        add_property_string(self, "url", parent_node_id="config").value = config['image-url']

        scheduler.add_job(self.run, CronTrigger.from_crontab(config['schedule'], "Europe/Warsaw"))

    def run(self):
        enabled = self.property_enabled.value
        is_on = self.tv_is_on.value
        print(is_on)
        if enabled and is_on:
            self.run_now(True)
        else:
            self.logger.warning('Time-To-Sleep skipped; enabled=%s, is_on=%s' % (enabled, is_on))

    def set_enabled(self, enabled):
        self.logger.info("Setting enabled to %s" % enabled)

    def run_now(self, value):
        if value:
            self.logger.info("Showing Time-to-Sleep image: %s" % self.url)
            self.publisher.publish('homie/sony-bravia/player/cast/set', self.url)
