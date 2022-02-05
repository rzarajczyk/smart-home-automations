from apscheduler.schedulers.base import BaseScheduler

from services.Service import Service


class AirPurifierService(Service):
    def __init__(self, config, scheduler: BaseScheduler):
        self.pm25 = 0
        self.monitor_is_on = False
        scheduler.add_job(self.recalculate, 'interval', seconds=config['recalculate-interval-seconds'])

    def accepts_prefixes(self) -> list[str]:
        return ['homie/xiaomi-air-purifier', 'homie/xiaomi-air-monitor']

    def on_message(self, topic, payload):
        print("%-60s | %s" % (topic, payload))
        if topic == 'homie/xiaomi-air-monitor/status/ison':
            self.monitor_is_on = bool(payload)
        if topic == 'homie/xiaomi-air-monitor/status/pm25':
            self.pm25 = int(payload)

    def recalculate(self):
        print("RECALCULATE")
