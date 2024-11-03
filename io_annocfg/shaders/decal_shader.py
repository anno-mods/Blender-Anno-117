from .default_shader import AnnoDefaultShader
from .shader_components import IntegerLink, StringLink

class DecalShader(AnnoDefaultShader):
    def __init__(self):
        super().__init__()
        self.shader_id = "AnnoDecalShader"
        self.material_properties["ShaderID"] = "1"
        #self.add_link(StringLink("VertexFormat", "VertexFormat", "P3f_N3f_G3f_T2f_T1f_T1f_T1f"))