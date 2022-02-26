from apscheduler.schedulers.base import BaseScheduler
from apscheduler.triggers.cron import CronTrigger

from automations.Automation import Automation, Publisher
from homie_helpers import add_property_boolean, add_property_string


class NightLightsAutomation(Automation):
    def __init__(self, mqtt_settings, config, scheduler: BaseScheduler, publisher: Publisher):
        super().__init__("night-lights-automation", "Turn on and off night lights", mqtt_settings)
        self.publisher = publisher

        self.turn_on_topics = config['turn-on']['topics']
        self.turn_off_topics = config['turn-off']['topics']

        self.property_enabled = add_property_boolean(self, "enabled", parent_node_id="service", set_handler=self.set_enabled)
        add_property_string(self, "on-schedule", parent_node_id="config").value = config['turn-on']['schedule']
        add_property_string(self, "off-schedule", parent_node_id="config").value = config['turn-off']['schedule']
        add_property_string(self, "on-topics", parent_node_id="config").value = str(self.turn_on_topics)
        add_property_string(self, "off-topics", parent_node_id="config").value = str(self.turn_off_topics)

        add_property_boolean(self, "run-on-now", property_name="Turn on now", parent_node_id="service", retained=False, set_handler=self.turn_on_now)
        add_property_boolean(self, "run-off-now", property_name="Turn off now", parent_node_id="service", retained=False, set_handler=self.turn_off_now)
        self.property_enabled.value = True

        scheduler.add_job(self.turn_on, CronTrigger.from_crontab(config['turn-on']['schedule'], "Europe/Warsaw"))
        scheduler.add_job(self.turn_off, CronTrigger.from_crontab(config['turn-off']['schedule'], "Europe/Warsaw"))

    def turn_on(self):
        if self.property_enabled.value:
            self.turn_on_now(True)

    def turn_off(self):
        if self.property_enabled.value:
            self.turn_off_now(True)

    def set_enabled(self, enabled):
        self.logger.info("Setting enabled to %s" % enabled)

    def turn_on_now(self, value):
        if value:
            for topic in self.turn_on_topics:
                self.logger.info("Turning on group %s" % topic)
                self.publisher.publish("homie/philips-hue/%s/ison/set" % topic, "true")

    def turn_off_now(self, value):
        if value:
            for topic in self.turn_off_topics:
                self.logger.info("Turning off group %s" % topic)
                self.publisher.publish("homie/philips-hue/%s/ison/set" % topic, "false")
