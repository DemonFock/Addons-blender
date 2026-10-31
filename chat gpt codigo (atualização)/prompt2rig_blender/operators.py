import bpy
import os
import glob
import time
import subprocess
import webbrowser
import urllib.request
from pathlib import Path

_SERVER_PROCESS = None
_AUTO_TIMER_RUNNING = False
_LAST_SEEN = {}
_PENDING = {}

def _settings(context):
    return context.scene.prompt2rig_settings

def _root(settings):
    raw = bpy.path.abspath(settings.project_dir).strip()
    return Path(raw).expanduser() if raw else None

def _base_url(settings):
    return f"http://127.0.0.1:{settings.port}"

def _server_ok(settings):
    try:
        request = urllib.request.Request(_base_url(settings) + "/", method="GET")
        with urllib.request.urlopen(request, timeout=1.5) as response:
            return response.status < 500
    except Exception:
        return False

def _takes_dir(settings):
    root = _root(settings)
    return root / "takes" if root else None

def _latest_glb(settings):
    folder = _takes_dir(settings)
    if not folder or not folder.is_dir():
        return None
    candidates = [Path(p) for p in glob.glob(str(folder / "*.glb"))]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)

def _import_glb(filepath):
    filepath = str(Path(filepath).expanduser().resolve())
    if not os.path.isfile(filepath):
        raise FileNotFoundError(filepath)
    bpy.ops.import_scene.gltf(filepath=filepath)
    return filepath

class P2R_OT_check_server(bpy.types.Operator):
    bl_idname = "prompt2rig.check_server"
    bl_label = "Verificar servidor"
    bl_description = "Verifica se o servidor local original está respondendo"

    def execute(self, context):
        settings = _settings(context)
        root = _root(settings)
        if not root or not (root / "server.mjs").is_file():
            settings.status = "Pasta inválida: não encontrei server.mjs."
            self.report({'ERROR'}, settings.status)
            return {'CANCELLED'}
        if _server_ok(settings):
            settings.status = f"Servidor ativo em {_base_url(settings)}"
            self.report({'INFO'}, settings.status)
            return {'FINISHED'}
        settings.status = "Servidor não está respondendo."
        self.report({'WARNING'}, settings.status)
        return {'CANCELLED'}

class P2R_OT_start_server(bpy.types.Operator):
    bl_idname = "prompt2rig.start_server"
    bl_label = "Iniciar servidor original"
    bl_description = "Executa node server.mjs na pasta do repositório original"

    def execute(self, context):
        global _SERVER_PROCESS
        settings = _settings(context)
        root = _root(settings)
        if not root or not (root / "server.mjs").is_file():
            settings.status = "Pasta inválida: selecione a raiz que contém server.mjs."
            self.report({'ERROR'}, settings.status)
            return {'CANCELLED'}
        if _server_ok(settings):
            settings.status = f"Servidor já ativo em {_base_url(settings)}"
            return {'FINISHED'}
        try:
            log_path = Path("/tmp/prompt2rig-blender-server.log")
            with open(log_path, "a", encoding="utf-8") as log:
                env = os.environ.copy()
                env["PORT"] = str(settings.port)
                _SERVER_PROCESS = subprocess.Popen(
                    ["node", "server.mjs"],
                    cwd=str(root),
                    env=env,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
            settings.status = (
                f"Servidor iniciado (PID {_SERVER_PROCESS.pid}). "
                "Aguarde alguns segundos e verifique."
            )
            self.report({'INFO'}, settings.status)
            return {'FINISHED'}
        except FileNotFoundError:
            settings.status = "Node.js não encontrado no PATH do Blender."
        except Exception as exc:
            settings.status = f"Falha ao iniciar servidor: {exc}"
        self.report({'ERROR'}, settings.status)
        return {'CANCELLED'}

class P2R_OT_open_studio(bpy.types.Operator):
    bl_idname = "prompt2rig.open_studio"
    bl_label = "Abrir estúdio Prompt2Rig"
    bl_description = "Abre o frontend original no navegador padrão"

    def execute(self, context):
        settings = _settings(context)
        if not _server_ok(settings):
            settings.status = "Servidor offline. Inicie e verifique primeiro."
            self.report({'ERROR'}, settings.status)
            return {'CANCELLED'}
        try:
            url = _base_url(settings)
            webbrowser.open(url)
            settings.status = f"Estúdio aberto: {url}"
            return {'FINISHED'}
        except Exception as exc:
            settings.status = f"Não foi possível abrir navegador: {exc}"
            self.report({'ERROR'}, settings.status)
            return {'CANCELLED'}

class P2R_OT_import_glb(bpy.types.Operator):
    bl_idname = "prompt2rig.import_glb"
    bl_label = "Importar arquivo GLB"
    bl_description = "Importa um take GLB exportado pelo estúdio original"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.glb", options={'HIDDEN'})

    def execute(self, context):
        settings = _settings(context)
        try:
            path = _import_glb(self.filepath)
            settings.last_imported = path
            settings.status = f"Importado: {Path(path).name}"
            self.report({'INFO'}, settings.status)
            return {'FINISHED'}
        except Exception as exc:
            settings.status = f"Falha ao importar GLB: {exc}"
            self.report({'ERROR'}, settings.status)
            return {'CANCELLED'}

    def invoke(self, context, event):
        root = _root(_settings(context))
        takes = root / "takes" if root else None
        if takes and takes.is_dir():
            self.filepath = str(takes / "")
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class P2R_OT_import_latest(bpy.types.Operator):
    bl_idname = "prompt2rig.import_latest"
    bl_label = "Importar último take"
    bl_description = "Importa o GLB mais recente da pasta takes"

    def execute(self, context):
        settings = _settings(context)
        latest = _latest_glb(settings)
        if not latest:
            settings.status = "Nenhum .glb encontrado na pasta takes."
            self.report({'WARNING'}, settings.status)
            return {'CANCELLED'}
        try:
            path = _import_glb(latest)
            settings.last_imported = path
            settings.status = f"Importado: {latest.name}"
            self.report({'INFO'}, settings.status)
            return {'FINISHED'}
        except Exception as exc:
            settings.status = f"Falha ao importar: {exc}"
            self.report({'ERROR'}, settings.status)
            return {'CANCELLED'}

def _auto_import_tick():
    try:
        scene = bpy.context.scene if bpy.context else None
        if scene is None:
            return 2.0
        settings = scene.prompt2rig_settings
        if not settings.auto_import:
            return 2.0
        folder = _takes_dir(settings)
        if not folder or not folder.is_dir():
            return 2.0

        now = time.monotonic()
        for path in folder.glob("*.glb"):
            try:
                stat = path.stat()
            except OSError:
                continue
            key = str(path.resolve())
            signature = (stat.st_mtime_ns, stat.st_size)
            if _LAST_SEEN.get(key) != signature:
                _LAST_SEEN[key] = signature
                _PENDING[key] = (now, stat.st_size)

        for key, (last_change, old_size) in list(_PENDING.items()):
            path = Path(key)
            try:
                stat = path.stat()
            except OSError:
                _PENDING.pop(key, None)
                continue
            if stat.st_size == old_size and now - last_change >= 2.5:
                if settings.last_imported != key:
                    try:
                        _import_glb(key)
                        settings.last_imported = key
                        settings.status = f"Importação automática: {path.name}"
                    except Exception as exc:
                        settings.status = f"Autoimport falhou ({path.name}): {exc}"
                _PENDING.pop(key, None)
            else:
                _PENDING[key] = (now, stat.st_size)
    except Exception:
        # Não permitir que falhas no monitor interrompam a interface do Blender.
        pass
    return 2.0

class P2R_OT_auto_import(bpy.types.Operator):
    bl_idname = "prompt2rig.auto_import"
    bl_label = "Ativar monitoramento"
    bl_description = "Ativa o monitoramento automático da pasta takes"

    def execute(self, context):
        global _AUTO_TIMER_RUNNING
        settings = _settings(context)
        settings.auto_import = True
        if not bpy.app.timers.is_registered(_auto_import_tick):
            bpy.app.timers.register(
                _auto_import_tick,
                first_interval=2.0,
                persistent=True,
            )
        _AUTO_TIMER_RUNNING = True
        settings.status = "Monitoramento ativo: aguardando novo GLB em takes/."
        self.report({'INFO'}, settings.status)
        return {'FINISHED'}
