import bpy
from bpy.props import StringProperty, IntProperty, BoolProperty

class P2R_Settings(bpy.types.PropertyGroup):
    project_dir: StringProperty(
        name="Pasta do Prompt2Rig",
        description="Pasta raiz do repositório original, onde está server.mjs",
        subtype="DIR_PATH",
        default="",
    )
    port: IntProperty(
        name="Porta",
        description="Porta HTTP do servidor Prompt2Rig",
        default=5177,
        min=1,
        max=65535,
    )
    auto_import: BoolProperty(
        name="Importar GLB automaticamente",
        description="Monitora takes/ e importa GLBs novos após a gravação terminar",
        default=False,
    )
    status: StringProperty(name="Estado", default="Configure a pasta do Prompt2Rig.")
    last_imported: StringProperty(name="Último arquivo importado", default="")
