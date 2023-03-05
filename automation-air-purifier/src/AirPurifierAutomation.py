import logging

from homie_helpers import Homie, Node, BooleanProperty, IntProperty, StringProperty, MqttClient

def homie_bool(value):
    return value == 'true'

class AirPurifierAutomation:
    def __init__(self, config, mqtt_settings):
        device_id = config['id']
        self.client = MqttClient(mqtt_settings)
        self.logger = logging.getLogger(device_id)

        self.history_size = config['moving-average-window-size']
        self.hysteresis = config['hysteresis']
        self.thresholds = config['thresholds']

        self.history = []
        self.current_threshold = 0
        self.pm25 = self.client.listen('homie/xiaomi-air-monitor/status/pm25', int)
        self.monitor_is_on = self.client.listen('homie/xiaomi-air-monitor/status/ison', homie_bool)
        self.current_speed = self.client.listen('homie/xiaomi-air-purifier/speed/speed')

        self.property_enabled = BooleanProperty("enabled", set_handler=self.set_enabled, initial_value=True)
        self.property_interval = IntProperty("interval", unit="s", initial_value=config['recalculate-interval-seconds'])
        self.property_hysteresis = IntProperty("hysteresis", initial_value=self.hysteresis)
        self.property_history_size = IntProperty("history-size", initial_value=self.history_size)
        self.property_threshold_levels = StringProperty("threshold-levels", initial_value=str([t['value'] for t in self.thresholds]))
        self.property_threshold_speeds = StringProperty("threshold-speeds", initial_value=str([t['speed'] for t in self.thresholds]))
        self.property_history = StringProperty("known-history")

        self.homie = Homie(mqtt_settings, device_id, "AirPurifier Automation", nodes=[
            Node("service", properties=[self.property_enabled, self.property_history]),
            Node("config", properties=[
                self.property_interval,
                self.property_hysteresis,
                self.property_history_size,
                self.property_threshold_levels,
                self.property_threshold_speeds
            ])
        ])

    def run(self):
        self.property_history.value = str(self.history)
        enabled = self.property_enabled.value
        is_on = self.monitor_is_on.value
        if enabled and is_on:
            self.recalculate_speed()
        else:
            self.logger.info(
                "Skipping AirPurifier recalculation - self.is_enabled = %s, monitor_is_on = %s" % (enabled, is_on))

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
        self.logger.info(f'Setting speed {target_speed}')

    def set_speed(self, speed):
        if speed != self.current_speed.value:
            self.logger.info("Setting new speed to %s" % speed)
            self.client.publish('homie/xiaomi-air-purifier/speed/speed/set', speed)

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
