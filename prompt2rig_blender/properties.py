import bpy
from bpy.types import PropertyGroup
from bpy.props import (
    StringProperty, IntProperty, BoolProperty, EnumProperty, FloatProperty
)

class P2R_Settings(PropertyGroup):
    server_url: StringProperty(
        name="Server URL", default="http://127.0.0.1:5177",
        description="URL of the original Prompt2Rig Node server"
    )
    backend_dir: StringProperty(
        name="Prompt2Rig folder", subtype="DIR_PATH", default="",
        description="Folder containing the original server.mjs"
    )
    status: StringProperty(name="Status", default="Not checked")
    prompt: StringProperty(
        name="Motion prompt",
        default="A person performs a clear, energetic dance with visible arms and legs",
        description="Text prompt sent to the Prompt2Rig video model"
    )
    video_model: EnumProperty(
        name="Video model",
        items=[
            ("h3", "H3 Max Turbo", "Faster generation"),
            ("flux3", "FLUX 3 Max", "Higher fidelity")
        ],
        default="h3"
    )
    duration: IntProperty(name="Duration", default=5, min=1, max=20, subtype="UNSIGNED")
    resolution: EnumProperty(
        name="Resolution",
        items=[
            ("480P", "480P", "H3 supported"),
            ("768P", "768P", "H3 supported"),
            ("1080P", "1080P", "Higher resolution where supported"),
        ],
        default="480P"
    )
    aspect_ratio: EnumProperty(
        name="Aspect ratio",
        items=[("16:9", "Landscape 16:9", ""), ("9:16", "Portrait 9:16", "")],
        default="16:9"
    )
    image_url: StringProperty(
        name="Image URL (optional)", default="",
        description="Optional public image URL for image-to-video generation"
    )
    use_seed: BoolProperty(name="Use seed", default=False)
    seed: IntProperty(name="Seed", default=42, min=0, max=2147483647)
    reasoning_level: EnumProperty(
        name="Reasoning", items=[("low", "Low", ""), ("high", "High", "")], default="low"
    )
    image_prompt: StringProperty(
        name="Performer image prompt",
        default="Full-body photograph of one person standing in a neutral pose, facing camera, entire body visible, plain studio background"
    )
    reference_video_path: bpy.props.StringProperty(
        name="Reference video (upload)", subtype="FILE_PATH", default="",
        description="Local video file to upload and use as motion reference (i2v)"
    )
    reference_video_url: bpy.props.StringProperty(
        name="Reference video URL", default="",
        description="Uploaded video URL returned by /api/upload (used for i2v)"
    )
    image_size: EnumProperty(
        name="Image size",
        items=[
            ("landscape_16_9", "Landscape 16:9", ""),
            ("portrait_16_9", "Portrait", ""),
            ("square", "Square", ""),
        ],
        default="landscape_16_9"
    )
    last_video_url: StringProperty(name="Last generated video", default="")
    last_image_url: StringProperty(name="Last generated image", default="")
    glb_path: StringProperty(name="Animated GLB", subtype="FILE_PATH", default="")
    auto_import: BoolProperty(name="Import GLB after selecting path", default=False)
    request_timeout: IntProperty(name="HTTP timeout (seconds)", default=180, min=10, max=1800)
