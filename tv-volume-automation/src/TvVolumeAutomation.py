import logging

from homie_helpers import Homie, Node, BooleanProperty, IntProperty, StringProperty, MqttClient



class TvVolumeAutomation:
    def __init__(self, config, mqtt_settings):
        device_id = config['id']
        self.client = MqttClient(mqtt_settings)
        self.logger = logging.getLogger(device_id)

        self.max_volume = config['max-volume-level']

        self.volume = self.client.listen('homie/sony-bravia/volume/volume-level', int)

        self.property_enabled = BooleanProperty("enabled", set_handler=self.set_enabled, initial_value=True)
        self.property_interval = IntProperty("interval", unit="s", initial_value=config['recalculate-interval-seconds'])
        self.property_max_volume = IntProperty("max-volume-level", initial_value = self.max_volume)

        self.homie = Homie(mqtt_settings, device_id, "TvVolume Automation", nodes=[
            Node("service", properties=[self.property_enabled]),
            Node("config", properties=[
                self.property_interval,
                self.property_max_volume
            ])
        ])

    def run(self):
        enabled = self.property_enabled.value
        current_col = self.volume.value
        if enabled and current_col > self.max_volume:
            self.logger.info("Setting TV volume to %s" % self.max_volume)
            self.client.publish('homie/sony-bravia/volume/volume-level/set', self.max_volume)

    def set_enabled(self, enabled):
        self.logger.info("Setting enabled to %s" % enabled)
