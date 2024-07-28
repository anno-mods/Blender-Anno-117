import xml.etree.ElementTree as ET
import mathutils
from ..utils import to_data_path, data_path_to_absolute_path
import os
from pathlib import Path
from ..prefs import IO_AnnocfgPreferences
import bpy
import subprocess

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

    def to_blender(self, shader, material_node : ET.Element, blender_material):
        return 

    def get_input(self, blender_material):
        group = [n for n in blender_material.node_tree.nodes if n.bl_idname == "ShaderNodeGroup"]
        return group[0].inputs.get(self.link_key)

class StaticFakeLink(AbstractLink):
    def __init__(self, link_key, flag_key, static_value : str, is_invalid = False):
        super().__init__(static_value, is_invalid)
        self.socket_type = "NoSocket"
        self.link_key = link_key
        self.flag_key = flag_key

    def to_xml(self, parent : ET.Element, blender_material):
        flag = ET.SubElement(parent, self.flag_key)
        flag.text = self.default_value

    def to_blender(self, shader, material_node : ET.Element, blender_material):
        return 

class TextureLink(AbstractLink): 
    def __init__(self, link_key, flag_key, texture_key, is_invalid = False, default_value = None, alpha_link = None):
        super().__init__(default_value, is_invalid)
        self.socket_type = "NodeSocketColor"
        self.flag_key = flag_key 
        self.texture_key = texture_key
        self.link_key = link_key
        self.alpha_link = alpha_link

    def has_alpha_link(self):
        return self.alpha_link is not None

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

    def to_blender(self, shader, material_node : ET.Element, blender_material):

        flag_xmlnode = material_node.find(self.flag_key)
        if flag_xmlnode is None:
            return 
        # Check if the thing is enabled first
        if not flag_xmlnode.text == "1":
            return 
        
        texture_xmlnode = material_node.find(self.texture_key)
        print(texture_xmlnode.text)

        texture_node = blender_material.node_tree.nodes.new('ShaderNodeTexImage')

        texture_path = Path(texture_xmlnode.text)
        texture = self.get_texture(texture_path)

        if texture is not None: 
            texture_node.image = texture
            if "Norm" in self.texture_key or "Metal" in self.texture_key or "Height" in self.texture_key:
                    texture_node.image.colorspace_settings.name = 'Non-Color'

        texture_node.name = self.texture_key
        texture_node.label = self.texture_key

        # create link: 
        blender_material.node_tree.links.new(shader.inputs[self.link_key], texture_node.outputs["Color"])

        if self.has_alpha_link():
            blender_material.node_tree.links.new(shader.inputs[self.alpha_link], texture_node.outputs["Alpha"])

    def get_texture(self, texture_path: Path):
        """Tries to find the texture texture_path with ending "_0.png" (quality setting can be changed) in the list of loaded textures.
        Otherwise loads it. If it is not existing but the corresponding .dds exists, converts it first.

        Args:
            texture_path (str): f.e. "data/.../texture_diffuse.psd"

        Returns:
            [type]: The texture or None.
        """
        if texture_path == Path(""):
            return None
        texture_path = Path(texture_path)
        texture_path = Path(texture_path.parent, texture_path.stem + texture_quality_suffix()+".dds")
        png_file = texture_path.with_suffix(".png")
        fullpath = data_path_to_absolute_path(texture_path)
        png_fullpath = data_path_to_absolute_path(png_file)
        image = bpy.data.images.get(str(png_file.name), None)
        if image is not None:
            image_path_full = os.path.normpath(bpy.path.abspath(image.filepath, library=image.library))
            if str(image_path_full) == str(png_fullpath):
                return image
        if not png_fullpath.exists():
            success = self.convert_to_png(fullpath)
            if not success:
                print("Failed to convert texture", fullpath)
                return None
        image = bpy.data.images.load(str(png_fullpath))
        return image

    def convert_to_png(self, fullpath: Path) -> bool:
        """Converts the .dds file to .png. Returns True if successful, False otherwise.

        Args:
            fullpath (str): .dds file

        Returns:
            bool: Successful
        """
        if not IO_AnnocfgPreferences.get_path_to_texconv().exists():
            return False
        if not fullpath.exists():
            return False
        try:
            proc_args = f"\"{IO_AnnocfgPreferences.get_path_to_texconv()}\" -ft PNG -sepalpha -y -o \"{fullpath.parent}\" \"{fullpath}\""
            subprocess.call(proc_args)
        except:
            return False
        return fullpath.with_suffix(".png").exists()
      
class FlagLink(AbstractLink): 
    def __init__(self, link_key, flag_key, is_invalid = False, default_value = None):
        super().__init__(default_value, is_invalid)
        self.socket_type = "NodeSocketBool"
        self.flag_key = flag_key
        self.link_key = link_key
        
    def to_xml(self, parent : ET.Element, blender_material):
        input = self.get_input(blender_material)
        value = False 
        if(input is not None):
            value = input.default_value

        flag = ET.SubElement(parent, self.flag_key)
        flag.text = "1" if value else "0"

    def to_blender(self, shader, material_node : ET.Element, blender_material):
        input = self.get_input(blender_material)
        subnode = material_node.find(self.flag_key)
        input.default_value = True if subnode is not None and subnode.text == "1" else False

class FloatLink(AbstractLink): 
    def __init__(self, link_key, flag_key, is_invalid = False, default_value = None):
        super().__init__(default_value, is_invalid)
        self.socket_type = "NodeSocketFloat"
        self.flag_key = flag_key
        self.link_key = link_key

    def to_xml(self, parent : ET.Element, blender_material):
        input = self.get_input(blender_material)
        value = 0.0
        if(input is not None):
            value = input.default_value

        flag = ET.SubElement(parent, self.flag_key)
        flag.text = str(round(value, 6))

    def to_blender(self, shader, material_node : ET.Element, blender_material):
        input = self.get_input(blender_material)
        subnode = material_node.find(self.flag_key)
        if subnode is None:
            input.default_value = 0.0 
        try:
            input.default_value = float(subnode.text)
        except: 
            input.default_value = self.default_value if self.has_default_value() else 0.0

class ColorLink(AbstractLink): 
    def __init__(self, link_key, flag_key, is_invalid = False, default_value = None):
        super().__init__(default_value, is_invalid)
        self.socket_type = "NodeSocketColor"
        self.flag_key = flag_key
        self.link_key = link_key

        self.color_keys = ["r", "g", "b"]
    
    def to_xml(self, parent : ET.Element, blender_material):
        input = self.get_input(blender_material)
        value = (0.0, 0.0, 0.0, 0.0)
        if(input is not None):
            value = input.default_value

        for i, val in enumerate(self.color_keys):
            r = ET.SubElement(parent, self.flag_key + "." + val)
            r.text = str(round(value[i], 6))

    def to_blender(self, shader, material_node : ET.Element, blender_material):
        input = self.get_input(blender_material)

        color_arr = [0.0, 0.0, 0.0, 1.0]

        for i, val in enumerate(self.color_keys):
            subnode = material_node.find(self.flag_key + "." + val)
            if subnode is None:
                color_arr[i] = 0.0
            try:
                color_arr[i] = float(subnode.text)
            except: 
                color_arr[i] = self.default_value if self.has_default_value() else 0.0

        input.default_value = tuple(color_arr)
        
class AbstractShaderComponent:
    def __init__():
        self.component_properties = {}
        self.links = []

class DefaultPropComponent(AbstractShaderComponent): 
    def __init__(self):
        self.links = [
            TextureLink("cMetallic", "METALLIC_TEX_ENABLED", "cModelMetallicTex"),
            FloatLink("Metalness Factor", "cMetallic"),
            FloatLink("AO Factor", "cAmbientOcclusion"),
            FlagLink("TerrainTint", "cUseTerrainTinting"),
            FlagLink("TerrainGrit", "cUseTerrainGrit"),
            TextureLink("cSeperateAO", "SEPARATE_AO_TEXTURE", "cSeparateAOTex"),
            TextureLink("Specular Occlusion", "SPEC_OCCLUSION_TEX_ENABLED", "cModelSpecOcclusionTex"),
            FlagLink("Specular uses 2nd UV set", "SPEC_OCCLUSION_USE_2ND_UV")
        ]

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
            TextureLink("cDiffuse", "DIFFUSE_ENABLED", "cModelDiffTex", alpha_link="Alpha"),  
            FloatLink("Alpha", "", is_invalid=True, default_value=1.0),
            TextureLink("cNormal", "NORMAL_ENABLED", "cModelNormalTex", alpha_link="Glossiness"),
            FloatLink("Glossiness", "", is_invalid=True),
            ColorLink("cDiffuseMultiplier", "cDiffuseColor", default_value=(1.0, 1.0, 1.0, 1.0)),
            FloatLink("Gloss Factor", "cGlossinessFactor", default_value=1.0),
            FloatLink("Opacity", "cOpacity", default_value=1.0),
            FloatLink("Texture Scroll Speed", "cTexScrollSpeed", default_value=0.0),
            TextureLink("cDyeMask", "DYE_MASK_ENABLED", "cDyeMask"),
        ]

class AdditionalPBRShaderComponent(AbstractShaderComponent):
    def __init__(self):
        self.links = [
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
class PropShadowsComponent(AbstractShaderComponent):
    def __init__(self):
        self.links = [
            FlagLink("Linear Shadow Interpolation", "LINEAR_SHADOW_INTERPOLATION_ENABLED"),
            FloatLink("Shadow Bias", "cModelShadowBias", default_value=0.0),            
            FlagLink("Exclude from SSR", "EXCLUDE_FROM_SSR_ENABLED"),
            FlagLink("Late Pre-Depth", "LATE_PRE_DEPTH")
        ]