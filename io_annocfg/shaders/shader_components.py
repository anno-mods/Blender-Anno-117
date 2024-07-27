import xml.etree.ElementTree as ET
import mathutils
from ..utils import to_data_path
import os
from pathlib import Path
from ..prefs import IO_AnnocfgPreferences
import bpy

def texture_quality_suffix():
    return "_"+IO_AnnocfgPreferences.get_texture_quality()

class AbstractLink: 
    def __init__(self, default_value = None, is_invalid = False):
        self.socket_type = ""
        self.link_key = ""
        self.is_invalid = is_invalid 
        self.default_value = default_value

    def has_socket(self):
        return self.socket_type is not "NoSocket"

    def has_default_value(self):
        return self.default_value is not None

    # todo pass in only the shader node to the material.
    def to_xml(self, parent, blender_material):
        return None

class StaticFakeLink(AbstractLink):
    def __init__(self, link_key, flag_key, static_value : str, is_invalid = False):
        super().__init__(static_value, is_invalid)
        self.socket_type = "NoSocket"
        self.link_key = link_key
        self.flag_key = flag_key

    def to_xml(self, parent : ET.Element, blender_material):
        flag = ET.SubElement(parent, self.flag_key)
        flag.text = self.default_value

class TextureLink(AbstractLink): 
    def __init__(self, link_key, flag_key, texture_key, is_invalid = False, default_value = None):
        super().__init__(default_value, is_invalid)
        self.socket_type = "NodeSocketColor"
        self.flag_key = flag_key 
        self.texture_key = texture_key
        self.link_key = link_key

    def to_xml(self, parent : ET.Element, blender_material):
        flag = ET.SubElement(parent, self.flag_key)

        # get links
        links = blender_material.node_tree.links 
        # there should only ever be one link where the key is equal to the socketname.
        link = [l for l in links if self.link_key == l.to_socket.name]
        if len(link) <= 0:
            flag.text = "0"
            return 
        
        texture_node = link[0].from_node
        
        if not texture_node.image:
            flag.text = "0"
            return 

        flag.text = "1"

        filepath_full = os.path.realpath(bpy.path.abspath(texture_node.image.filepath, library=texture_node.image.library))
        texture_path = to_data_path(filepath_full)
        #Rename "data/.../some_diff_0.png" to "data/.../some_diff.psd"
        extension = ".psd"
        texture_path = Path(texture_path.as_posix().replace(texture_quality_suffix()+".", ".")).with_suffix(extension)

        tex = ET.SubElement(parent, self.texture_key)
        tex.text = str(texture_path)

class FlagLink(AbstractLink): 
    def __init__(self, link_key, flag_key, is_invalid = False, default_value = None):
        super().__init__(default_value, is_invalid)
        self.socket_type = "NodeSocketBool"
        self.flag_key = flag_key
        self.link_key = link_key
        
    def to_xml(self, parent : ET.Element, blender_material):

        group = [n for n in blender_material.node_tree.nodes if n.bl_idname == "ShaderNodeGroup"]
        input = group[0].inputs.get(self.link_key)
        value = False 
        if(input is not None):
            value = input.default_value

        flag = ET.SubElement(parent, self.flag_key)
        flag.text = "1" if value else "0"

class FloatLink(AbstractLink): 
    def __init__(self, link_key, flag_key, is_invalid = False, default_value = None):
        super().__init__(default_value, is_invalid)
        self.socket_type = "NodeSocketFloat"
        self.flag_key = flag_key
        self.link_key = link_key

    def to_xml(self, parent : ET.Element, blender_material):
        group = [n for n in blender_material.node_tree.nodes if n.bl_idname == "ShaderNodeGroup"]
        input = group[0].inputs.get(self.link_key)
        value = 0.0
        if(input is not None):
            value = input.default_value

        flag = ET.SubElement(parent, self.flag_key)
        flag.text = str(round(value, 6))

class ColorLink(AbstractLink): 
    def __init__(self, link_key, flag_key, is_invalid = False, default_value = None):
        super().__init__(default_value, is_invalid)
        self.socket_type = "NodeSocketColor"
        self.flag_key = flag_key
        self.link_key = link_key
    
    def to_xml(self, parent : ET.Element, blender_material):
        group = [n for n in blender_material.node_tree.nodes if n.bl_idname == "ShaderNodeGroup"]
        input = group[0].inputs.get(self.link_key)
        value = (0.0, 0.0, 0.0, 0.0)
        if(input is not None):
            value = input.default_value

        r = ET.SubElement(parent, self.link_key + ".r")
        r.text = str(round(value[0], 6))
        g = ET.SubElement(parent, self.link_key + ".g")
        g.text = str(round(value[1], 6))
        b = ET.SubElement(parent, self.link_key +  ".b")
        b.text = str(round(value[2], 6))

class AbstractShaderComponent:
    def __init__():
        self.component_properties = {}
        self.links = []

class DefaultShaderFakeComponent(AbstractShaderComponent): 
    def __init__(self):
        self.links = [
            TextureLink("cMetallic", "METALLIC_TEX_ENABLED", "cModelMetallicTex"),
            TextureLink("cSeperateAO", "SEPARATE_AO_TEXTURE", "cSeparateAOTex"),
            FlagLink("TerrainTint", "cUseTerrainTinting")
        ]

class CommonShaderComponent(AbstractShaderComponent): 
    def __init__(self):
        self.links = [
            StaticFakeLink("Common", "Common", "Common"),
            TextureLink("cDiffuse", "DIFFUSE_ENABLED", "cModelDiffTex"),  
            FloatLink("Alpha", "", is_invalid=True, default_value=1.0),
            TextureLink("cNormal", "NORMAL_ENABLED", "cModelNormalTex"),
            FloatLink("Glossiness", "", is_invalid=True),
            ColorLink("cDiffuseMultiplier", "cDiffuseColor", default_value=(1.0, 1.0, 1.0, 1.0)),
            FloatLink("Gloss Factor", "cGlossinessFactor", default_value=1.0),
            FloatLink("Opacity", "cOpacity", default_value=1.0),
            FloatLink("Texture Scroll Speed", "cTexScrollSpeed", default_value=0.0),
            TextureLink("cDyeMask", "DYE_MASK_ENABLED", "cDyeMask"),
            TextureLink("cHeight", "HEIGHT_MAP_ENABLED", "cHeightMap"),
            FloatLink("Parallax Scale", "cParallaxScale", default_value=1.0),
            FlagLink("Parallax Mapping", "PARALLAX_MAPPING_ENABLED", default_value=True),
            FlagLink("Self Shadowing", "SELF_SHADOWING_ENABLED"),
            FlagLink("Cutout Water", "WATER_CUTOUT_ENABLED")
        ]

class TerrainAdaptionShaderComponent(AbstractShaderComponent):
    def __init__(self):
        self.links = [            
            StaticFakeLink("TerrainAdaption", "TerrainAdaption", "TerrainAdaption"),
            FlagLink("Adapt to Terrain", "ADJUST_TO_TERRAIN_HEIGHT"),
            FlagLink("Use Vertex Colors", "VERTEX_COLORED_TERRAIN_ADAPTION"),
            FlagLink("Absolute TerrainAdaption", "ABSOLUTE_TERRAIN_ADAPTION")
        ]

class EnvironmentShaderComponent(AbstractShaderComponent): 
    def __init__(self): 
        self.links = [
            StaticFakeLink("Environment", "Environment", "Environment"),
            FlagLink("Use Local Environment Box", "cUseLocalEnvironmentBox", default_value=True),
            FloatLink("BBox Min X", "cEnvironmentBoundingBox.x", default_value=0.0),
            FloatLink("BBox Min Y", "cEnvironmentBoundingBox.y", default_value=0.0),          
            FloatLink("BBox Max X", "cEnvironmentBoundingBox.z", default_value=0.0),
            FloatLink("BBox Max Y", "cEnvironmentBoundingBox.w", default_value=4.0),        
        ]

class GlowShaderComponent(AbstractShaderComponent): 
    def __init__(self):
        self.links = [
            StaticFakeLink("Glow", "Glow", "Glow"),
            FlagLink("Enable Glow", "GLOW_ENABLED"),
            ColorLink("cEmissiveColor", "cEmissiveColor", default_value=(2.0, 2.0, 2.0, 1.0)),
            TextureLink("cNightGlow", "NIGHT_GLOW_ENABLED", "cNightGlowMap")
        ]