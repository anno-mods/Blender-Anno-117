import bpy
import xml.etree.ElementTree as ET
from .shader_components import AbstractShaderComponent
from ..utils import xml_smart

class AnnoBasicShader: 
    def __init__(self):

        self.material_properties = {
            "ConfigType" : "MATERIAL",
            "Name" : "",
            "ShaderID" : 8,
            "VertexFormat" : "",
            "NumBonesPerVertex" : 0
        }

    def set_property(self, key, value):
        assert key in self.material_properties, "Invalid Property: " + key
        assert type(value) == type(self.material_properties[key]), "Type mismatch while setting property"
        self.material_properties[key] = value

    def compose(self, shaderComponent : AbstractShaderComponent):
        self.material_properties.update(shaderComponent.component_properties)

    def to_xml_node(self) -> ET.Element:
        root = ET.Element("Config")

        for key, value in self.material_properties.items(): 
            xml_smart(root, key, value)
        return root

    def create_anno_shader(self):
        return None

    def add_shader_node(self, node_tree, node_type, **kwargs):
        node = node_tree.nodes.new(node_type)
        positioning_unit = (300, 300)
        positioning_offset = (0, 3 * positioning_unit[1])
        x,y = kwargs.pop("position", (0,0))
        node.location.x = x* positioning_unit[0] - positioning_offset[0]
        node.location.y = y* positioning_unit[1] - positioning_offset[1]

        if "name" in kwargs and not "label" in kwargs:
            kwargs["label"] = kwargs["name"]

        for input_key, default_value in kwargs.pop("default_inputs", {}).items():
            print(input_key)

            nodeinput = None
            if type(input_key) is int: 
                nodeinput = node.inputs[input_key]
            elif type(input_key) is str:
                nodeinput = node.inputs.get(input_key)

            if(nodeinput is None):
                print("We aren't allowed to use this as a defaultInput: " + node_type + " | " + input_key)
                continue
            nodeinput.default_value = default_value

        for input_key, input_connector in kwargs.pop("inputs", {}).items():
                node_tree.links.new(node.inputs[input_key], input_connector)

        for attr, value in kwargs.items():
            setattr(node, attr, value)

        return node