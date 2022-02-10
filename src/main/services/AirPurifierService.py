import logging

from apscheduler.schedulers.base import BaseScheduler

from services.Service import Service, Publisher


class AirPurifierService(Service):
    def __init__(self, config, scheduler: BaseScheduler, publisher: Publisher):
        self.publisher = publisher
        self.logger = logging.getLogger("AirPurifierService")
        self.history_size = config['moving-average-window-size']
        self.hysteresis = config['hysteresis']
        self.thresholds = config['thresholds']

        self.history = []
        self.current_threshold = 0
        self.automation = True
        self.pm25 = 0
        self.monitor_is_on = False
        self.current_speed = None
        scheduler.add_job(self.recalculate, 'interval', seconds=config['recalculate-interval-seconds'])

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

    def recalculate(self):
        if self.automation and self.monitor_is_on:
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


def calculate_threshold_index(avg, current_threshold, thresholds, hysteresis):
    target_index = 0
    for index, threshold in enumerate(thresholds):
        value = threshold
        if index == current_threshold:
            value -= hysteresis
        if avg >= value:
            target_index = index
    return target_index
