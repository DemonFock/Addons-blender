bl_info = {
    "name": "Prompt2Rig for Blender",
    "author": "Prompt2Rig Blender Integration",
    "version": (0, 2, 0),
    "blender": (5, 3, 0),
    "location": "View3D > Sidebar > Prompt2Rig",
    "description": "Blender 5.3 bridge for the Prompt2Rig server and exported animated GLB takes",
    "category": "Animation",
}

import bpy
from . import properties, operators, ui

_CLASSES = (
    properties.P2R_Settings,
    operators.P2R_OT_check_server,
    operators.P2R_OT_start_server,
    operators.P2R_OT_open_web_app,
    operators.P2R_OT_generate_video,
    operators.P2R_OT_generate_image,
    operators.P2R_OT_import_glb,
    operators.P2R_OT_upload_reference_video,
    operators.P2R_OT_open_takes_folder,
    ui.P2R_PT_main,
    ui.P2R_PT_generation,
    ui.P2R_PT_import,
)

def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.prompt2rig = bpy.props.PointerProperty(type=properties.P2R_Settings)

def unregister():
    if hasattr(bpy.types.Scene, "prompt2rig"):
        del bpy.types.Scene.prompt2rig
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
