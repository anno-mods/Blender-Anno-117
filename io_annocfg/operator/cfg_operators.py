import bpy

from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty,CollectionProperty
from bpy.types import Operator, AddonPreferences
from bpy.types import Object as BlenderObject
from bpy_extras.object_utils import AddObjectHelper

from ..anno_objects import MainFile, Model, Propcontainer, Prop, Cloth, Decal, SubFile, ClothMaterial
from ..material import Material
from ..shaders.default_shader import AnnoDefaultShader

class generic_cfg_object(Operator, AddObjectHelper):
    bl_idname = "mesh.add_anno_cfgobj"
    bl_options = {'REGISTER', 'UNDO'}
    bl_label = "Add Anno Object"

    def __init__(self):
        self.filename = ""
        self.TargetObject : AnnoObject = MainFile()

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        self.parent = context.active_object
        obj = self.TargetObject.from_default()
        if self.parent:
            obj.parent = self.parent

        return {'FINISHED'}

class cfg_mainfile(generic_cfg_object):
    bl_idname = "mesh.add_anno_mainfile"
    def __init__(self):
        super().__init__()
        self.TargetObject = MainFile()

class cfg_model(generic_cfg_object):
    bl_idname = "mesh.add_anno_model"
    def __init__(self):
        super().__init__()
        self.TargetObject = Model()

class cfg_propcontainer(generic_cfg_object):
    bl_idname = "mesh.add_anno_propcontainer"
    def __init__(self):
        super().__init__()
        self.TargetObject = Propcontainer()

class cfg_prop(generic_cfg_object):
    bl_idname = "mesh.add_anno_prop"
    def __init__(self):
        super().__init__()
        self.TargetObject = Prop()

class cfg_cloth(generic_cfg_object):
    bl_idname = "mesh.add_anno_cloth"
    def __init__(self):
        super().__init__()
        self.TargetObject = Cloth()

class cfg_decal(generic_cfg_object):
    bl_idname = "mesh.add_anno_decal"
    def __init__(self):
        super().__init__()
        self.TargetObject = Decal()

class cfg_subfile(generic_cfg_object):
    bl_idname = "mesh.add_anno_subfile"
    def __init__(self):
        super().__init__()
        self.TargetObject = SubFile()

class cfg_menu(bpy.types.Menu):
    bl_idname="add.anno_objects"
    bl_label="Anno Objects"

    def draw(self, context):
        layout = self.layout

        layout.operator(
            cfg_mainfile.bl_idname,
            text="Empty MainFile",
            icon='FILE_BLANK'
        )
        layout.operator(
            cfg_subfile.bl_idname,
            text="Empty SubFile",
            icon='APPEND_BLEND'
        )
        layout.operator(
            cfg_model.bl_idname,
            text="Empty Model",
            icon='MESH_CUBE'
        )
        layout.operator(
            cfg_propcontainer.bl_idname,
            text="Empty Propcontainer",
            icon='FILE_VOLUME'
        )
        layout.operator(
            cfg_decal.bl_idname,
            text="Empty Decal",
            icon='MESH_PLANE'
        )
        layout.operator(
            cfg_cloth.bl_idname,
            text="Empty Cloth",
            icon='MOD_CLOTH'
        )
        #layout.operator(
        #    cfg_prop.bl_idname,
        #    text="Empty Prop",
        #    icon='PLUGIN'
        #)


class shader_menu(bpy.types.Menu):
    bl_idname="add.anno_shaders"
    bl_label="Anno Shaders"

    def draw(self, context):
        layout = self.layout

        layout.operator(
            shader_default.bl_idname,
            text="Default (8)",
            icon='FILE_BLANK'
        )

def add_anno_object_menu(self, context):
    self.layout.menu(
        cfg_menu.bl_idname,
        text="Anno Objects",
        icon='FILE_BLEND')

def add_anno_shader_menu(self, context):
    self.layout.menu(
        shader_menu.bl_idname,
        text="Anno Shaders",
        icon='FILE_BLEND')

class shader_default(bpy.types.Operator):
    bl_idname = "node.add_anno_shader"
    bl_label  = "Add Default Anno Shader"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == "NODE_EDITOR"

    def execute(self, context):
        node_tree = context.object.active_material.node_tree
        my_group = AnnoDefaultShader().add_anno_shader(node_tree.nodes)
        return {"FINISHED"}


# todo (Taube) this is broken, reimplement this operator for actual cloth when shaders are rewritten.
class shader_cloth(bpy.types.Operator):
    bl_idname = "node.add_anno_shader_cloth"
    bl_label  = "Add Custom Node Group"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == "NODE_EDITOR"

    def execute(self, context):
        node_tree = context.object.active_material.node_tree
        my_group = AnnoDefaultShader().add_anno_shader(node_tree.nodes)
        return {"FINISHED"}

classes = (
    cfg_mainfile,
    cfg_model,
    cfg_subfile,
    cfg_propcontainer,
    cfg_prop,
    cfg_cloth,
    cfg_decal,
    cfg_menu,
    shader_menu,
    shader_default,
    shader_cloth
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.VIEW3D_MT_add.append(add_anno_object_menu)
    bpy.types.NODE_MT_add.append(add_anno_shader_menu)

def unregister():
    from bpy.utils import unregister_class
    bpy.types.VIEW3D_MT_add.remove(add_anno_object_menu)
    bpy.types.NODE_MT_add.remove(add_anno_shader_menu)
    for cls in classes:
        unregister_class(cls)
        