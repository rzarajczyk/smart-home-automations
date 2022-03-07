from apscheduler.schedulers.base import BaseScheduler

from automations.Automation import Automation, Publisher
from homie_helpers import add_property_boolean, add_property_int, add_property_string


class AirPurifierAutomation(Automation):
    def __init__(self, mqtt_settings, config, scheduler: BaseScheduler, publisher: Publisher):
        super().__init__("air-purifier-automation", "Air Purifier", mqtt_settings)
        self.publisher = publisher

        self.history_size = config['moving-average-window-size']
        self.hysteresis = config['hysteresis']
        self.thresholds = config['thresholds']

        self.history = []
        self.current_threshold = 0
        self.pm25 = self.mqtt_collect('homie/xiaomi-air-monitor/status/pm25', int)
        self.monitor_is_on = self.mqtt_collect('homie/xiaomi-air-monitor/status/ison', bool)
        self.current_speed = self.mqtt_collect('homie/xiaomi-air-purifier/speed/speed')

        self.property_enabled = add_property_boolean(self, "enabled", parent_node_id="service", set_handler=self.set_enabled, initial_value=True)
        add_property_int(self, "interval", parent_node_id="config", unit="s").value = config['recalculate-interval-seconds']
        add_property_int(self, "hysteresis", parent_node_id="config").value = self.hysteresis
        add_property_int(self, "history-size", parent_node_id="config").value = self.history_size
        add_property_string(self, "threshold-levels", parent_node_id="config").value = str([t['value'] for t in self.thresholds])
        add_property_string(self, "threshold-speeds", parent_node_id="config").value = str([t['speed'] for t in self.thresholds])
        self.property_history = add_property_string(self, "known-history", parent_node_id="service")

        scheduler.add_job(self.run, 'interval', seconds=config['recalculate-interval-seconds'])

    def run(self):
        self.property_history.value = str(self.history)
        enabled = self.property_enabled.value
        is_on = self.monitor_is_on.value
        if enabled and is_on:
            self.recalculate_speed()
        else:
            self.logger.info("Skipping AirPurifier recalculation - self.is_enabled = %s, monitor_is_on = %s" % (enabled, is_on))

    def recalculate_speed(self):
        self.history.append(self.pm25.value)
        if len(self.history) > self.history_size:
            self.history.pop(0)
        avg = sum(self.history) / len(self.history)

        threshold_values = [threshold['value'] for threshold in self.thresholds]
        target_index = calculate_threshold_index(avg, self.current_threshold, threshold_values, self.hysteresis)
        target_speed = self.thresholds[target_index]['speed']

        self.set_speed(target_speed)
        self.current_threshold = target_index

    def set_speed(self, speed):
        if speed != self.current_speed.value:
            self.logger.info("Setting new speed to %s" % speed)
            self.publisher.publish('homie/xiaomi-air-purifier/speed/speed/set', speed)

    def set_enabled(self, enabled):
        self.logger.info("Setting enabled to %s" % enabled)


def calculate_threshold_index(avg, current_threshold, thresholds, hysteresis):
    target_index = 0
    for index, threshold in enumerate(thresholds):
        value = threshold
        if index == current_threshold:
            value -= hysteresis
        if avg >= value:
            target_index = index
    return target_index
