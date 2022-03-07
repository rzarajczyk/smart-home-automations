from apscheduler.schedulers.base import BaseScheduler
from apscheduler.triggers.cron import CronTrigger

from automations.Automation import Automation, Publisher
from homie_helpers import add_property_boolean, add_property_string, add_property_int


class EveningColorTemperatureAutomation(Automation):
    def __init__(self, mqtt_settings, config, scheduler: BaseScheduler, publisher: Publisher):
        super().__init__("evening-lights-automation", "Change color temperature for the evening", mqtt_settings)
        self.publisher = publisher

        self.topics_to_change = config['topics']
        self.duration = round(config['duration-seconds'], 1)
        self.target = config['target-temperature-kelvin']

        self.groups_on = {}
        self.groups_bri = {}
        for topic in self.topics_to_change:
            self.groups_on[topic] = self.mqtt_collect('homie/philips-hue/%s/ison' % topic, bool)
            self.groups_bri[topic] = self.mqtt_collect('homie/philips-hue/%s/brightness' % topic, int)

        self.property_enabled = add_property_boolean(self, "enabled", parent_node_id="service", set_handler=self.set_enabled, initial_value=True)
        add_property_string(self, "schedule", parent_node_id="config").value = config['schedule']
        add_property_string(self, "topics", parent_node_id="config").value = str(self.topics_to_change)
        add_property_int(self, "duration", unit="s", parent_node_id="config").value = self.duration
        add_property_int(self, "target", unit="K", property_name="Target color temperature", parent_node_id="config").value = self.target
        add_property_boolean(self, "run", property_name="Run now", parent_node_id="service", retained=False, set_handler=self.run_now)

        scheduler.add_job(self.run, CronTrigger.from_crontab(config['schedule']))

    def run(self):
        enabled = self.property_enabled.value
        if enabled:
            self.run_now(True)
        else:
            self.logger.warning('Evening Color Transormation skipped; enabled=%s' % enabled)

    def set_enabled(self, enabled):
        self.logger.info("Setting enabled to %s" % enabled)

    def run_now(self, value):
        if value:
            for topic in self.topics_to_change:
                self.logger.info('Trying to start Color Temperature change for topic %s' % topic)
                if topic in self.groups_on \
                        and self.groups_on[topic].value \
                        and topic in self.groups_bri \
                        and self.groups_bri[topic].value > 90:
                    self.logger.info('Color Temperature should be changed! Sending command')
                    value = "%s,%s" % (self.target, self.duration)
                    self.publisher.publish("homie/philips-hue/%s/color-temperature-transition/set" % topic, value)
                else:
                    self.logger.info('Color Temperature SHOULD NOT be changed')
