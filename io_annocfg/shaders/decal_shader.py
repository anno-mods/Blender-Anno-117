from .default_shader import AnnoDefaultShader

class DecalShader(AnnoDefaultShader):
    def __init__(self):
        super().__init__()
        self.shader_id = "AnnoDecalShader"
        self.material_properties["VertexFormat"] = "P3f_N3f_G3f_T2f_T1f_T1f_T1f"
        self.material_properties["ShaderID"] = "1"