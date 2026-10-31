import bpy

class P2R_PT_main(bpy.types.Panel):
    bl_label = "Prompt2Rig"
    bl_idname = "P2R_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Prompt2Rig"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.prompt2rig_settings

        col = layout.column(align=True)
        col.label(text="Estúdio original", icon='WORLD')
        col.prop(settings, "project_dir")
        row = col.row(align=True)
        row.prop(settings, "port")
        row.operator("prompt2rig.start_server", text="Iniciar", icon='PLAY')
        col.operator("prompt2rig.check_server", icon='FILE_REFRESH')
        col.operator("prompt2rig.open_studio", icon='URL')

        layout.separator()
        col = layout.column(align=True)
        col.label(text="Animação / Takes", icon='ANIM')
        col.operator("prompt2rig.import_latest", icon='IMPORT')
        col.operator("prompt2rig.import_glb", icon='FILE_FOLDER')
        col.prop(settings, "auto_import")
        col.operator("prompt2rig.auto_import", icon='TIME')

        layout.separator()
        box = layout.box()
        box.label(text="Estado")
        box.label(text=settings.status or "—")
        if settings.last_imported:
            box.label(
                text="Último: " + settings.last_imported.split("/")[-1],
                icon='CHECKMARK',
            )

        layout.separator()
        layout.label(text="Pipeline original:", icon='INFO')
        layout.label(text="Vídeo local → MediaPipe → retarget")
        layout.label(text="Preview 3D no navegador → export GLB")
        layout.label(text="GLB animado → Blender")
