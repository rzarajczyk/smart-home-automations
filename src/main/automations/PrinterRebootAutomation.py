from apscheduler.schedulers.base import BaseScheduler
from apscheduler.triggers.cron import CronTrigger

from automations.Automation import Automation, Publisher
from homie_helpers import add_property_boolean, add_property_string


class PrinterRebootAutomation(Automation):
    def __init__(self, mqtt_settings, config, scheduler: BaseScheduler, publisher: Publisher):
        super().__init__("printer-reboot-automation", "Reboot the printer at night", mqtt_settings)
        self.publisher = publisher

        self.turn_on_topics = config['turn-on']['topics']
        self.turn_off_topics = config['turn-off']['topics']

        self.property_enabled = add_property_boolean(self, "enabled", parent_node_id="service", set_handler=self.set_enabled, initial_value=True)
        add_property_string(self, "on-schedule", parent_node_id="config").value = config['turn-on']['schedule']
        add_property_string(self, "off-schedule", parent_node_id="config").value = config['turn-off']['schedule']
        add_property_string(self, "on-topics", parent_node_id="config").value = str(self.turn_on_topics)
        add_property_string(self, "off-topics", parent_node_id="config").value = str(self.turn_off_topics)

        add_property_boolean(self, "run-on-now", property_name="Turn on now", parent_node_id="service", retained=False, set_handler=self.turn_on_now)
        add_property_boolean(self, "run-off-now", property_name="Turn off now", parent_node_id="service", retained=False, set_handler=self.turn_off_now)

        scheduler.add_job(self.turn_on, CronTrigger.from_crontab(config['turn-on']['schedule'], "Europe/Warsaw"))
        scheduler.add_job(self.turn_off, CronTrigger.from_crontab(config['turn-off']['schedule'], "Europe/Warsaw"))

    def turn_on(self):
        enabled = self.property_enabled.value
        if enabled:
            self.turn_on_now(True)
        else:
            self.logger.warning('Turn ON skipped; enabled=%s' % enabled)

    def turn_off(self):
        enabled = self.property_enabled.value
        if enabled:
            self.turn_off_now(True)
        else:
            self.logger.warning('Turn OFF skipped; enabled=%s' % enabled)

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
