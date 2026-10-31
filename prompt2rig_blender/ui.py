import bpy
from bpy.types import Panel

class P2R_PT_main(Panel):
    bl_label = "Prompt2Rig"
    bl_idname = "P2R_PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Prompt2Rig"

    def draw(self, context):
        s = context.scene.prompt2rig
        layout = self.layout
        layout.label(text=s.status, icon="INFO")
        col = layout.column(align=True)
        col.prop(s, "server_url")
        col.prop(s, "backend_dir")
        row = col.row(align=True)
        row.operator("prompt2rig.start_server", icon="PLAY")
        row.operator("prompt2rig.check_server", icon="URL")
        layout.operator("prompt2rig.open_web_app", icon="WORLD")

class P2R_PT_generation(Panel):
    bl_label = "Generation"
    bl_idname = "P2R_PT_generation"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Prompt2Rig"
    bl_parent_id = "P2R_PT_main"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        s = context.scene.prompt2rig
        layout = self.layout
        layout.prop(s, "prompt")
        layout.prop(s, "video_model")
        layout.prop(s, "duration")
        layout.prop(s, "resolution")
        layout.prop(s, "aspect_ratio")
        layout.prop(s, "image_url")
        layout.separator()
        box = layout.box()
        box.label(text="Reference video (optional)")
        box.prop(s, "reference_video_path")
        box.operator("prompt2rig.upload_reference_video", icon="FILE_VIDEO")
        if s.reference_video_url:
            box.label(text="Uploaded URL: " + s.reference_video_url[:50] + ("..." if len(s.reference_video_url) > 50 else ""))
        layout.prop(s, "use_seed")
        if s.use_seed:
            layout.prop(s, "seed")
        if s.video_model == "flux3":
            layout.prop(s, "reasoning_level")
        layout.operator("prompt2rig.generate_video", icon="RENDER_ANIMATION")
        layout.separator()
        box = layout.box()
        box.label(text="Generate performer image")
        box.prop(s, "image_prompt")
        box.prop(s, "image_size")
        box.operator("prompt2rig.generate_image", icon="IMAGE")

        if s.last_video_url:
            box = layout.box()
            box.label(text="Last generated video")
            box.label(text=s.last_video_url[:42] + ("..." if len(s.last_video_url) > 42 else ""))

class P2R_PT_import(Panel):
    bl_label = "Import / Takes"
    bl_idname = "P2R_PT_import"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Prompt2Rig"
    bl_parent_id = "P2R_PT_main"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        s = context.scene.prompt2rig
        layout = self.layout
        layout.prop(s, "glb_path")
        layout.operator("prompt2rig.import_glb", icon="IMPORT")
        layout.operator("prompt2rig.open_takes_folder", icon="FILE_FOLDER")
        layout.label(text="Import requires a GLB exported by the Prompt2Rig web app.")
