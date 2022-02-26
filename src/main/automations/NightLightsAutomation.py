import logging

from apscheduler.schedulers.base import BaseScheduler
from apscheduler.triggers.cron import CronTrigger

from automations.Automation import Automation, Publisher
from homie_helpers import add_property_boolean, add_property_string


class NightLightsAutomation(Automation):
    def __init__(self, mqtt_settings, config, scheduler: BaseScheduler, publisher: Publisher):
        super().__init__("night-lights-automation", "Turn on and off night lights", mqtt_settings)
        self.publisher = publisher
        self.logger = logging.getLogger("NightLightsAutomation")

        self.groups = config['groups']

        self.is_enabled = True

        self.property_enabled = add_property_boolean(self, "enabled",
                                                     parent_node_id="service",
                                                     set_handler=self.set_enabled)
        add_property_string(self, "on-schedule", parent_node_id="config").value = config['on-schedule']
        add_property_string(self, "off-schedule", parent_node_id="config").value = config['off-schedule']
        add_property_string(self, "lights", parent_node_id="config").value = str(self.groups)

        add_property_boolean(self, "run-on-now",
                             property_name="Turn on now",
                             parent_node_id="service",
                             retained=False,
                             set_handler=self.run_on_now)
        add_property_boolean(self, "run-off-now",
                             property_name="Turn off now",
                             parent_node_id="service",
                             retained=False,
                             set_handler=self.run_off_now)

        scheduler.add_job(self.run_on, CronTrigger.from_crontab(config['on-schedule']))
        scheduler.add_job(self.run_off, CronTrigger.from_crontab(config['off-schedule']))
        self.property_enabled.value = True

    def run_on(self):
        self.property_enabled.value = self.is_enabled
        self.run_on_now(True)

    def run_off(self):
        self.property_enabled.value = self.is_enabled
        self.run_off_now(True)

    def set_enabled(self, enabled):
        self.logger.info("Setting enabled to %s" % self.is_enabled)
        self.is_enabled = bool(enabled)

    def run_on_now(self, value):
        if value:
            for group_id in self.groups:
                self.logger.info("Turning on group %s" % group_id)
                self.publisher.publish("homie/philips-hue/%s/ison/set" % group_id, "true")

    def run_off_now(self, value):
        if value:
            for group_id in self.groups:
                self.logger.info("Turning off group %s" % group_id)
                self.publisher.publish("homie/philips-hue/%s/ison/set" % group_id, "false")
