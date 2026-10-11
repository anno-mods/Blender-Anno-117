from .shader_base import AnnoBasicShader

from .shader_node_templates import ShaderTemplate

from .shader_components import A8_DiffuseComponent, A8_DyeMaskComponent, A8_GlossFactorComponent, A8_GlowComponent, A8_HeightComponent, A8_MaterialBlendingComponent, A8_MetallicComponent, A8_NightGlowComponent, A8_NormalComponent, A8_OpacityComponent, A8_SheenComponent, A8_TerrainAdaptionComponent, A8_TerrainTintingComponent, A8_UvMappingComponent, AdditionalPBRShaderComponent, CommonShaderComponent, DefaultShaderFakeComponent, DyeMaskTexScrollShaderComponent, EnumLink, EnvironmentShaderComponent, GlowShaderComponent, IntegerLink, StringLink, TerrainAdaptionShaderComponent, VertexFormatShaderComponent

class A8_DecalShader(AnnoBasicShader):
    def __init__(self):
        super().__init__()
        self.shader_id = "A8_DecalShader"
        self.material_properties["ShaderID"] = "1"        
        self.material_properties["NumBonesPerVertex"] = "0"
        self.add_link(EnumLink("VertexFormat", "VertexFormat", { "Decal (P3f_N3f_G3f_T2f_T1f_T1f_T1f)": "P3f_N3f_G3f_T2f_T1f_T1f_T1f" }))
        self.compose(VertexFormatShaderComponent())
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
    
    def create_anno_shader(self):
        anno_shader = self.setup_empty_shader()                
        shader_template = ShaderTemplate(anno_shader)
        diff = shader_template.add_diffuse("cDiffuse", "cDiffuseMultiplier")
        shader_template.add_dye(diff)
        shader_template.add_normal("cNormal", add_height=True)
        shader_template.add_gloss("Glossiness")
        shader_template.add_metallic("cMetallic")
        shader_template.add_emission(diff, "cEmissiveColor", "cNightGlow")