import logging

from apscheduler.schedulers.base import BaseScheduler

from homie_helpers import PropertyType
from homie_helpers import add_property
from automations.Automation import Automation, Publisher


class AirPurifierAutomation(Automation):
    def __init__(self, mqtt_settings, config, scheduler: BaseScheduler, publisher: Publisher):
        super().__init__("air-purifier-automation", "AirPurifier Automation", mqtt_settings)
        self.publisher = publisher
        self.logger = logging.getLogger("AirPurifierAutomation")
        self.history_size = config['moving-average-window-size']
        self.hysteresis = config['hysteresis']
        self.thresholds = config['thresholds']

        self.history = []
        self.current_threshold = 0
        self.is_enabled = True
        self.pm25 = 0
        self.monitor_is_on = False
        self.current_speed = None

        self.property_enabled = add_property(self, PropertyType.IS_ENABLED, set_handler=self.set_enabled)

        self.start()
        scheduler.add_job(self.run, 'interval', seconds=config['recalculate-interval-seconds'])
        self.property_enabled.value = True

    def accept_message(self, topic, payload):
        if topic == 'homie/xiaomi-air-monitor/status/ison':
            self.monitor_is_on = bool(payload)
            self.logger.debug("Message received: %-70s | %s" % (topic, payload))
        if topic == 'homie/xiaomi-air-monitor/status/pm25':
            self.pm25 = int(payload)
            self.logger.debug("Message received: %-70s | %s" % (topic, payload))
        if topic == 'homie/xiaomi-air-purifier/speed/speed':
            self.current_speed = payload
            self.logger.debug("Message received: %-70s | %s" % (topic, payload))

    def run(self):
        self.property_enabled.value = self.is_enabled
        if self.is_enabled and self.monitor_is_on:
            self.recalculate_speed()

    def recalculate_speed(self):
        self.history.append(self.pm25)
        if len(self.history) > self.history_size:
            self.history.pop(0)
        avg = sum(self.history) / len(self.history)

        threshold_values = [threshold['value'] for threshold in self.thresholds]
        target_index = calculate_threshold_index(avg, self.current_threshold, threshold_values, self.hysteresis)
        target_speed = self.thresholds[target_index]['speed']

        self.set_speed(target_speed)
        self.current_threshold = target_index

    def set_speed(self, speed):
        if speed != self.current_speed:
            self.logger.info("Setting new speed to %s" % speed)
            self.publisher.publish('homie/xiaomi-air-purifier/speed/speed/set', speed)

    def set_enabled(self, enabled):
        self.is_enabled = bool(enabled)
        self.logger.info("Setting enabled to %s" % self.is_enabled)


def calculate_threshold_index(avg, current_threshold, thresholds, hysteresis):
    target_index = 0
    for index, threshold in enumerate(thresholds):
        value = threshold
        if index == current_threshold:
            value -= hysteresis
        if avg >= value:
            target_index = index
    return target_index