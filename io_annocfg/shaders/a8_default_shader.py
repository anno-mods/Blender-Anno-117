import bpy
from .shader_base import AnnoBasicShader
from .shader_components import *
from .shader_node_templates import ShaderTemplate

from ..utils import to_data_path
import os
from pathlib import Path
from ..prefs import IO_AnnocfgPreferences

class A8_DefaultShader(AnnoBasicShader):

    def __init__(self):
        super().__init__()

        self.shader_id = "A8_DefaultShader"     
        self.add_link(VectorLink("Uv Map", "UvMap"))   
        self.add_link(IntegerLink("NumBonesPerVertex", "NumBonesPerVertex", 0))
        self.compose(A8_MetallicComponent())
        self.compose(A8_DiffuseComponent())
        self.compose(A8_NormalComponent())
        self.compose(A8_DyeMaskComponent())
        self.compose(A8_GlossFactorComponent())
        self.compose(A8_OpacityComponent())
        self.compose(A8_HeightComponent())
        self.compose(A8_TerrainAdaptionComponent())
        self.compose(A8_TerrainTintingComponent())
        self.compose(A8_GlowComponent())
        self.compose(A8_NightGlowComponent())
        self.compose(A8_UvMappingComponent())
        self.compose(A8_SheenComponent())
        self.compose(A8_MaterialBlendingComponent())

        # override default vertexformat
        self.material_properties["VertexFormat"] = "P4h_N4b_G4b_B4b_T2h"
        self.material_properties["ShaderID"] = "8"

    def create_anno_shader(self):
        anno_shader = self.setup_empty_shader()
                
        shader_template = ShaderTemplate(anno_shader)
        diff = shader_template.add_diffuse("cDiffuse", "cDiffuseMultiplier")
        shader_template.add_dye(diff)
        shader_template.add_normal("cNormal", add_height=True)
        shader_template.add_gloss("Glossiness")
        shader_template.add_metallic("cMetallic")
        shader_template.add_emission(diff, "cEmissiveColor", "cNightGlow")