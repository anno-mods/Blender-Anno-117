import xml.etree.ElementTree as ET

class TextureLink: 
    def __init__(self, flag_key, texture_key):
        self.flag_key = flag_key 
        self.texture_key = texture_key

class AbstractShaderComponent:
    def __init__():
        self.component_properties = {}
        self.texture_links = {}

class DefaultShaderFakeComponent(AbstractShaderComponent): 
    def __init__(self):
        self.component_properties = {
            "METALLIC_TEX_ENABLED" : False,
            "cModelMetallicTex" : "",
            "cUseTerrainTinting" : False,
            "SEPARATE_AO_TEXTURE" : False,
            "cSeparateAOTex" : ""
        }
        self.texture_links = {
            "cMetallic" : TextureLink("METALLIC_TEX_ENABLED", "cModelMetallicTex")
        }

class CommonShaderComponent(AbstractShaderComponent): 
    def __init__(self):
        self.component_properties = {
            "Common" : "Common",
            "DIFFUSE_ENABLED" : False,
            "cModelDiffTex" : "",
            "NORMAL_ENABLED" : False,
            "cModelNormalTex" : "",
            "cDiffuseColor" : {"r" : 1.0, "g": 1.0, "b" : 1.0},
            "cGlossinessFactor" : 1.0,
            "cOpacity" : 1.0,
            "cTexScrollSpeed" : 0.0,
            "DYE_MASK_ENABLED" : False,
            "cDyeMask" : "",
            "HEIGHT_MAP_ENABLED" : False,
            "cHeightMap" : "",
            "cParallaxScale" : 1.0,
            "PARALLAX_MAPPING_ENABLED" : False,
            "SELF_SHADOWING_ENABLED" : False, 
            "WATER_CUTOUT_ENABLED" : False
        }
        self.texture_links = {
            "cDiffuse" : TextureLink("DIFFUSE_ENABLED", "cModelDiffTex"),            
            "cNormal" : TextureLink("NORMAL_ENABLED", "cModelNormalTex"),
            "cDyeMask" : TextureLink("DYE_MASK_ENABLED", "cDyeMask"),
            "cHeight" : TextureLink("HEIGHT_MAP_ENABLED", "cHeightMap"),
        }

class TerrainAdaptionShaderComponent(AbstractShaderComponent):
    def __init__(self):
        self.component_properties = {
            "TerrainAdaption" : "TerrainAdaption",
            "ADJUST_TO_TERRAIN_HEIGHT" : False,
            "VERTEX_COLORED_TERRAIN_ADAPTION" : False,
            "ABSOLUTE_TERRAIN_ADAPTION" : False
        }
        self.texture_links = {}

class EnvironmentShaderComponent(AbstractShaderComponent): 
    def __init__(self): 
        self.component_properties = {
            "Environment" : "Environment",
            "cUseLocalEnvironmentBox" : True,
            "cEnvironmentBoundingBox" : {"x" : 0.0, "y" : 0.0, "z" : 0.0, "w" : 4.0}
        }
        self.texture_links = {}

class GlowShaderComponent(AbstractShaderComponent): 
    def __init__(self):
        self.component_properties = {
            "Glow" : "Glow",
            "GLOW_ENABLED" : True,
            "cEmissiveColor" : {"r" : 1.0, "g" : 1.0, "b": 1.0},
            "NIGHT_GLOW_ENABLED" : False,
            "cNightGlowMap" : ""
        }
        self.texture_links = {
            "cNightGlow" : TextureLink("NIGHT_GLOW_ENABLED", "cNightGlowMap")
        }