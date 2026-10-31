import bpy
import os
import subprocess
import webbrowser
from pathlib import Path
from bpy.types import Operator
from bpy.props import StringProperty
from . import network

def _settings(context):
    return context.scene.prompt2rig

class P2R_OT_check_server(Operator):
    bl_idname = "prompt2rig.check_server"
    bl_label = "Check server"
    bl_description = "Check whether the original Prompt2Rig Node server is reachable"

    def execute(self, context):
        s = _settings(context)
        try:
            network.check_server(s.server_url, timeout=5)
            s.status = "Server online"
            self.report({"INFO"}, s.status)
            return {"FINISHED"}
        except Exception as exc:
            s.status = f"Server offline: {exc}"
            self.report({"ERROR"}, s.status)
            return {"CANCELLED"}

class P2R_OT_start_server(Operator):
    bl_idname = "prompt2rig.start_server"
    bl_label = "Start Prompt2Rig server"
    bl_description = "Start node server.mjs from the configured Prompt2Rig folder"

    def execute(self, context):
        s = _settings(context)
        root = bpy.path.abspath(s.backend_dir).strip()
        server_file = Path(root) / "server.mjs" if root else None
        if not server_file or not server_file.is_file():
            self.report({"ERROR"}, "Configure the Prompt2Rig folder; server.mjs was not found.")
            return {"CANCELLED"}
        try:
            # Keep the backend independent. The process inherits its .env and working directory.
            subprocess.Popen(
                ["node", "server.mjs"],
                cwd=str(server_file.parent),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            s.status = "Server start requested; checking in a moment"
            self.report({"INFO"}, s.status)
            return {"FINISHED"}
        except Exception as exc:
            s.status = f"Could not start server: {exc}"
            self.report({"ERROR"}, s.status)
            return {"CANCELLED"}

class P2R_OT_open_web_app(Operator):
    bl_idname = "prompt2rig.open_web_app"
    bl_label = "Open Prompt2Rig app"
    bl_description = "Open the original Prompt2Rig web interface; it contains the complete live retargeting workflow"

    def execute(self, context):
        url = _settings(context).server_url.rstrip("/") + "/"
        try:
            webbrowser.open(url)
            return {"FINISHED"}
        except Exception as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}

class P2R_OT_generate_video(Operator):
    bl_idname = "prompt2rig.generate_video"
    bl_label = "Generate video"
    bl_description = "Submit a text-to-video or image-to-video request to the original server"

    def execute(self, context):
        s = _settings(context)
        body = {
            "prompt": s.prompt,
            "model": s.video_model,
            "duration": s.duration,
            "resolution": s.resolution,
            "aspect_ratio": s.aspect_ratio,
            "reasoning_level": s.reasoning_level,
        }
        if s.image_url.strip():
            body["image_url"] = s.image_url.strip()
        if s.reference_video_url.strip():
            body["image_url"] = s.reference_video_url.strip()
        if s.use_seed:
            body["seed"] = s.seed
        try:
            result = network.request_json(s.server_url, "/api/video", body, timeout=s.request_timeout)
            video_url = result.get("video_url")
            if not video_url:
                raise RuntimeError(f"Server returned no video_url: {result}")
            s.last_video_url = video_url
            s.status = f"Video generated ({result.get('elapsed', '?')}s)"
            self.report({"INFO"}, s.status)
            return {"FINISHED"}
        except Exception as exc:
            s.status = f"Generation failed: {exc}"
            self.report({"ERROR"}, s.status)
            return {"CANCELLED"}

class P2R_OT_generate_image(Operator):
    bl_idname = "prompt2rig.generate_image"
    bl_label = "Generate performer image"
    bl_description = "Generate a performer reference image through the original fal.ai proxy"

    def execute(self, context):
        s = _settings(context)
        try:
            result = network.request_json(
                s.server_url, "/api/image",
                {"prompt": s.image_prompt, "image_size": s.image_size},
                timeout=s.request_timeout
            )
            image_url = result.get("image_url")
            if not image_url:
                raise RuntimeError(f"Server returned no image_url: {result}")
            s.last_image_url = image_url
            s.image_url = image_url
            s.status = "Performer image generated and assigned as video reference"
            self.report({"INFO"}, s.status)
            return {"FINISHED"}
        except Exception as exc:
            s.status = f"Image generation failed: {exc}"
            self.report({"ERROR"}, s.status)
            return {"CANCELLED"}

class P2R_OT_upload_reference_video(Operator):
    bl_idname = "prompt2rig.upload_reference_video"
    bl_label = "Upload reference video (i2v)"
    bl_description = "Upload a local video file to /api/upload and store the URL for image/video-to-video generation"

    def execute(self, context):
        s = _settings(context)
        file_path = bpy.path.abspath(s.reference_video_path)
        if not file_path or not os.path.isfile(file_path):
            self.report({"ERROR"}, f"Reference video file not found: {file_path}")
            return {"CANCELLED"}
        try:
            res = network.upload_file(s.server_url, file_path)
            url = res.get("url") or res.get("video_url") or res.get("path")
            if not url:
                self.report({"ERROR"}, f"Upload returned no URL: {res}")
                return {"CANCELLED"}
            s.reference_video_url = url
            s.status = f"Reference video uploaded: {url}"
            self.report({"INFO"}, s.status)
            return {"FINISHED"}
        except Exception as exc:
            s.status = f"Upload failed: {exc}"
            self.report({"ERROR"}, s.status)
            return {"CANCELLED"}


class P2R_OT_import_glb(Operator):
    bl_idname = "prompt2rig.import_glb"
    bl_label = "Import animated GLB"
    bl_description = "Import a Prompt2Rig exported .glb take into the current Blender scene"
    filepath: StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        s = _settings(context)
        if s.glb_path:
            self.filepath = bpy.path.abspath(s.glb_path)
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        path = bpy.path.abspath(self.filepath or _settings(context).glb_path)
        if not path or not os.path.isfile(path):
            self.report({"ERROR"}, f"File not found: {path}")
            return {"CANCELLED"}
        before = set(bpy.data.objects)
        try:
            # Blender 5.3 glTF importer operator (provided by Blender's glTF I/O extension).
            bpy.ops.import_scene.gltf(filepath=path)
            imported = [obj for obj in bpy.data.objects if obj not in before]
            armatures = [obj for obj in imported if obj.type == "ARMATURE"]
            meshes = [obj for obj in imported if obj.type == "MESH"]
            msg = f"Imported {len(imported)} objects, {len(armatures)} armature(s), {len(meshes)} mesh(es)"
            _settings(context).glb_path = path
            _settings(context).status = msg
            self.report({"INFO"}, msg)
            return {"FINISHED"}
        except Exception as exc:
            self.report({"ERROR"}, f"GLB import failed: {exc}. Check that glTF 2.0 I/O is enabled.")
            return {"CANCELLED"}

class P2R_OT_open_takes_folder(Operator):
    bl_idname = "prompt2rig.open_takes_folder"
    bl_label = "Open takes folder"

    def execute(self, context):
        s = _settings(context)
        root = bpy.path.abspath(s.backend_dir).strip()
        takes = Path(root) / "takes" if root else None
        if not takes or not takes.is_dir():
            self.report({"WARNING"}, "No takes/ folder found in the configured backend directory.")
            return {"CANCELLED"}
        try:
            if os.name == "nt":
                os.startfile(str(takes))
            else:
                subprocess.Popen(["xdg-open", str(takes)])
            return {"FINISHED"}
        except Exception as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
