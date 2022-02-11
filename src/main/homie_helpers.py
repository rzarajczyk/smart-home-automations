from enum import Enum, auto

from homie.device_base import Device_Base
from homie.node.node_base import Node_Base
from homie.node.property.property_base import Property_Base
from homie.node.property.property_boolean import Property_Boolean


class PropertyType(Enum):
    IS_ENABLED = auto()


def add_property(device: Device_Base, property_type: PropertyType, set_handler=None) -> Property_Base:
    if device.get_node("service") is None:
        node = Node_Service(device)
        device.add_node(node)
    node: Node_Base = device.get_node("service")
    if property_type == PropertyType.IS_ENABLED:
        property = Property_Enabled(node, set_value=set_handler)
        node.add_property(property)
        return property
    raise Exception("Unsupported property type: %s" % str(property_type))


class Node_Service(Node_Base):
    def __init__(self, device):
        super().__init__(device, "service", "service", "service", True, 1)


class Property_Enabled(Property_Boolean):
    def __init__(self, node, set_value=None):
        super().__init__(
            node=node,
            id="enabled",
            name="Service is enabled",
            settable=set_value is not None,
            retained=True,
            qos=1,
            unit=None,
            data_type=None,
            data_format=None,
            value=None,
            set_value=set_value,
            tags=[],
            meta={},
        )
