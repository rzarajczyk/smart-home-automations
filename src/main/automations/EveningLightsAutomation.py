import logging

from apscheduler.schedulers.base import BaseScheduler
from apscheduler.triggers.cron import CronTrigger

from automations.Automation import Automation, Publisher
from homie_helpers import add_property_boolean, add_property_string, add_property_int


class EveningLightsAutomation(Automation):
    def __init__(self, mqtt_settings, config, scheduler: BaseScheduler, publisher: Publisher):
        super().__init__("evening-lights-automation", "Change color temperature at the specific time", mqtt_settings)
        self.publisher = publisher
        self.logger = logging.getLogger("EveningLightsAutomation")

        self.groups = config['groups']
        self.duration = 10 * config['duration-seconds']
        self.target = config['target-temperature-kelvin']

        self.is_enabled = True
        self.groups_on = {}
        self.groups_bri = {}

        self.property_enabled = add_property_boolean(self, "enabled",
                                                     parent_node_id="service",
                                                     set_handler=self.set_enabled)
        add_property_string(self, "schedule", parent_node_id="config").value = config['schedule']
        add_property_string(self, "groups", parent_node_id="config").value = str(self.groups)
        add_property_int(self, "duration", unit="s", parent_node_id="config").value = self.duration
        add_property_int(self, "target",
                         unit="K",
                         property_name="Target color temperature",
                         parent_node_id="config").value = self.target
        add_property_string(self, "lights", parent_node_id="config").value = str(self.groups)
        add_property_boolean(self, "run",
                             property_name="Run now",
                             parent_node_id="service",
                             retained=False,
                             set_handler=self.run_now)

        scheduler.add_job(self.run, CronTrigger.from_crontab(config['schedule']))
        self.property_enabled.value = True

    def run(self):
        self.property_enabled.value = self.is_enabled
        self.run_now(True)

    def set_enabled(self, enabled):
        self.logger.info("Setting enabled to %s" % self.is_enabled)
        self.is_enabled = bool(enabled)

    def run_now(self, value):
        if value:
            for group_id in self.groups:
                if group_id in self.groups_on \
                        and self.groups_on[group_id] \
                        and group_id in self.groups_bri \
                        and self.groups_bri[group_id] > 90:
                    value = "%s,%s" % (self.target, self.duration)
                    self.publisher.publish("homie/philips-hue/%s/color-temperature-transition/set" % group_id, value)

    def accept_message(self, topic, payload):
        for group in self.groups:
            if topic == 'homie/philips-hue/%s/ison' % group:
                self.logger.debug("Message received: %-70s | %s" % (topic, payload))
                self.groups_on[group] = bool(payload)
            if topic == 'homie/philips-hue/%s/brightness' % group:
                self.logger.debug("Message received: %-70s | %s" % (topic, payload))
                self.groups_bri[group] = int(payload)
