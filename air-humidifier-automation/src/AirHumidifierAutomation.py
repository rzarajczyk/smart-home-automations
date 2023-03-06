import logging

from homie_helpers import Homie, Node, BooleanProperty, IntProperty, StringProperty, MqttClient



class AirHumidifierAutomation:
    def __init__(self, config, mqtt_settings):
        device_id = config['id']
        self.client = MqttClient(mqtt_settings)
        self.logger = logging.getLogger(device_id)

        self.speed = self.client.listen('homie/sony-bravia/volume/volume-level')

        self.property_enabled = BooleanProperty("enabled", set_handler=self.set_enabled, initial_value=True)
        self.property_schedule = StringProperty("shutdown-schedule", initial_value=config['shutdown-schedule'])

        self.homie = Homie(mqtt_settings, device_id, "TvVolume Automation", nodes=[
            Node("service", properties=[self.property_enabled]),
            Node("config", properties=[self.property_schedule])
        ])

    def run(self):
        enabled = self.property_enabled.value
        speed = self.speed.value
        if enabled and speed != 'off':
            self.logger.info("Setting humidifier speed to off")
            self.client.publish('homie/xiaomi-air-humidifier/speed/speed/set', 'off')
        else:
            self.logger.warning('Shutdown skipped; enabled=%s, speed=%s' % (enabled, speed))

    def set_enabled(self, enabled):
        self.logger.info("Setting enabled to %s" % enabled)
