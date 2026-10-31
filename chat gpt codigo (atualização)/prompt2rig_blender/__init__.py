bl_info = {
    "name": "Prompt2Rig Bridge",
    "author": "DemonFock / ChatGPT",
    "version": (0, 3, 0),
    "blender": (4, 5, 0),
    "location": "View3D > Sidebar > Prompt2Rig",
    "description": "Integra o estúdio Prompt2Rig original ao Blender e importa takes GLB",
    "category": "Animation",
}

import bpy
from . import properties, operators, ui

_CLASSES = (
    properties.P2R_Settings,
    operators.P2R_OT_check_server,
    operators.P2R_OT_start_server,
    operators.P2R_OT_open_studio,
    operators.P2R_OT_import_latest,
    operators.P2R_OT_import_glb,
    operators.P2R_OT_auto_import,
    ui.P2R_PT_main,
)

def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.prompt2rig_settings = bpy.props.PointerProperty(
        type=properties.P2R_Settings
    )

def unregister():
    if hasattr(bpy.types.Scene, "prompt2rig_settings"):
        del bpy.types.Scene.prompt2rig_settings
    for cls in reversed(_CLASSES):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
