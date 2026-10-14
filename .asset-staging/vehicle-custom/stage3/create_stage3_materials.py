import math
import os
import struct
import zlib

import bpy
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(os.path.dirname(ROOT), "stage2_1", "beyond_school_stage2_1_dashboard.blend")
OUTPUT = os.path.join(ROOT, "beyond_school_stage3_interior_pbr.blend")
TEXTURE_DIR = os.path.join(ROOT, "textures")
os.makedirs(TEXTURE_DIR, exist_ok=True)

bpy.ops.wm.open_mainfile(filepath=SOURCE)
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in {i.identifier for i in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items} else "BLENDER_EEVEE"
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1.0


def material(name, color, roughness, metallic=0.0, emission=None, strength=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = strength
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def image_texture_material(name, image, base_color=(1.0, 1.0, 1.0), roughness=0.3, emission_strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = image
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Base Color"].default_value = (*base_color, 1.0)
    if emission_strength:
        bsdf.inputs["Emission Strength"].default_value = emission_strength
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def display_text(name, body, location, size, material, align="CENTER"):
    bpy.ops.object.text_add(
        location=location,
        rotation=(math.pi / 2, 0.0, -math.pi / 2),
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.body = body
    obj.data.align_x = align
    obj.data.align_y = "CENTER"
    obj.data.size = size
    obj.data.extrude = 0.0004
    obj.data.materials.append(material)
    return obj


def make_image(name, width, height, background, draw):
    image = bpy.data.images.new(name, width=width, height=height, alpha=False)
    pixels = [background[0], background[1], background[2], 1.0] * (width * height)

    def put(x, y, color):
        if 0 <= x < width and 0 <= y < height:
            i = (y * width + x) * 4
            pixels[i:i + 4] = [color[0], color[1], color[2], 1.0]

    def rect(x0, y0, x1, y1, color):
        for y in range(max(0, y0), min(height, y1)):
            for x in range(max(0, x0), min(width, x1)):
                put(x, y, color)

    def line(x0, y0, x1, y1, color, width_px=2):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for s in range(steps + 1):
            x = int(x0 + (x1 - x0) * s / steps)
            y = int(y0 + (y1 - y0) * s / steps)
            for oy in range(-width_px, width_px + 1):
                for ox in range(-width_px, width_px + 1):
                    put(x + ox, y + oy, color)

    def circle(cx, cy, radius, color, fill=False, width_px=2):
        r0 = 0 if fill else max(0, radius - width_px)
        r1 = radius
        for y in range(cy - radius, cy + radius + 1):
            for x in range(cx - radius, cx + radius + 1):
                d = math.hypot(x - cx, y - cy)
                if r0 <= d <= r1:
                    put(x, y, color)

    draw(rect, line, circle)
    image.pixels = pixels
    image.filepath_raw = os.path.join(TEXTURE_DIR, name + ".png")
    image.file_format = "PNG"
    image.save()
    return image


def cluster_draw(rect, line, circle):
    bg = (0.012, 0.018, 0.022)
    amber = (1.0, 0.36, 0.035)
    white = (0.8, 0.9, 0.86)
    red = (0.95, 0.07, 0.035)
    rect(0, 0, 1024, 512, bg)
    circle(250, 270, 145, white, False, 5)
    circle(774, 270, 145, white, False, 5)
    for cx in (250, 774):
        for i in range(13):
            a = math.radians(-135 + i * 22.5)
            line(cx + int(math.cos(a) * 116), 270 + int(math.sin(a) * 116),
                 cx + int(math.cos(a) * 137), 270 + int(math.sin(a) * 137), white, 3)
    line(250, 270, 310, 205, red, 5)
    line(774, 270, 728, 188, red, 5)
    rect(332, 210, 692, 330, (0.19, 0.07, 0.015))
    rect(344, 222, 680, 318, amber)
    rect(356, 234, 668, 306, (0.10, 0.035, 0.008))
    # Pixel-font-like warning bars: high-contrast original graphic.
    for y in (246, 263, 280, 297):
        rect(380, y, 640, y + 5, amber if y != 280 else red)


def infotainment_draw(rect, line, circle):
    bg = (0.008, 0.025, 0.035)
    cyan = (0.04, 0.65, 0.72)
    white = (0.75, 0.9, 0.88)
    amber = (1.0, 0.42, 0.04)
    rect(0, 0, 1024, 512, bg)
    rect(40, 35, 984, 95, (0.02, 0.08, 0.10))
    for i in range(4):
        y = 150 + i * 70
        line(80, y, 920, y + (i - 1) * 15, cyan, 10)
    rect(120, 175, 270, 275, (0.02, 0.10, 0.12))
    circle(195, 225, 36, amber, False, 8)
    rect(620, 350, 925, 410, (0.28, 0.06, 0.01))
    rect(640, 365, 905, 395, amber)
    line(80, 430, 930, 430, white, 3)


cluster_image = make_image("cluster_stage3_1024x512", 1024, 512, (0.01, 0.01, 0.01), cluster_draw)
infotainment_image = make_image("infotainment_stage3_1024x512", 1024, 512, (0.01, 0.01, 0.01), infotainment_draw)

soft_touch = material("STAGE3_SoftTouch_Polyurethane", (0.0097, 0.0105, 0.013), 0.80)
graphite = material("STAGE3_Graphite_Polymer", (0.018, 0.021, 0.028), 0.62)
shadow = material("STAGE3_Shutline_Shadow", (0.004, 0.005, 0.006), 0.88)
gunmetal = material("STAGE3_Satin_Gunmetal", (0.157, 0.174, 0.205), 0.34, metallic=0.78)
leather = material("STAGE3_Steering_Leather", (0.018, 0.020, 0.022), 0.55)
hubmat = material("STAGE3_Steering_Hub", (0.028, 0.032, 0.037), 0.70)
red = material("STAGE3_Hazard_Crimson", (0.48, 0.009, 0.013), 0.45)
icon = material("STAGE3_Hazard_Icon", (0.8, 0.62, 0.16), 0.38, emission=(0.8, 0.3, 0.03), strength=0.4)
black = material("STAGE3_Vent_Recess", (0.003, 0.004, 0.005), 0.90)
rubber = material("STAGE3_Rubber_Grip", (0.018, 0.020, 0.023), 0.82)
pedal = material("STAGE3_Brushed_Pedal", (0.11, 0.12, 0.13), 0.58, metallic=0.55)
road = material("STAGE3_Road_Asphalt", (0.035, 0.042, 0.050), 0.88)
marking = material("STAGE3_Road_Marking", (0.72, 0.52, 0.18), 0.48)
signmat = material("STAGE3_Assistance_Sign", (0.04, 0.12, 0.14), 0.50, emission=(0.15, 0.08, 0.02), strength=0.25)
cluster_mat = image_texture_material("STAGE3_Cluster_Display", cluster_image, roughness=0.22, emission_strength=1.4)
info_mat = image_texture_material("STAGE3_Infotainment_Display", infotainment_image, roughness=0.12, emission_strength=0.9)

def assign(name, mat):
    obj = bpy.data.objects.get(name)
    if obj and obj.type == "MESH":
        obj.data.materials.clear()
        obj.data.materials.append(mat)

for n in ("DASH_UpperShell", "DASH_InstrumentBinnacle"):
    assign(n, soft_touch)
for n in ("DASH_LowerFascia", "DASH_GloveboxDoor", "CONSOLE_CentreStack", "CONSOLE_CentreTunnel", "STEERING_ColumnShroud", "FOOTWELL_DriverTrim"):
    assign(n, graphite)
assign("DASH_GloveboxSeam", shadow)
for n in ("DASH_AccentRail", "DASH_InstrumentClusterBezel", "CONSOLE_InfotainmentFrame", "CONSOLE_GearSelectorBase"):
    assign(n, gunmetal)
for n in ("STEERING_Wheel",):
    assign(n, leather)
for n in ("STEERING_Hub", "STEERING_Column"):
    assign(n, hubmat)
for n in ("REV5_SteeringSpoke_00", "REV5_SteeringSpoke_01", "REV5_SteeringSpoke_02"):
    assign(n, gunmetal)
assign("BTN_HazardSwitch", red)
assign("BTN_HazardSwitch_Cap", red)
assign("BTN_HazardSwitch_Icon", icon)
assign("DASH_InstrumentCluster", cluster_mat)
for n in ("DASH_ClusterDial_00", "DASH_ClusterDial_01"):
    assign(n, cluster_mat)
assign("CONSOLE_InfotainmentScreen", info_mat)
assign("CONSOLE_InfotainmentMark", icon)
if bpy.data.objects.get("CONSOLE_InfotainmentMark"):
    bpy.data.objects["CONSOLE_InfotainmentMark"].hide_render = True
for n in ("CONSOLE_AirVent_00", "CONSOLE_AirVent_01"):
    assign(n, black)
for obj in bpy.data.objects:
    if obj.name.startswith("CONSOLE_AirVent_") and "Slot" in obj.name:
        assign(obj.name, gunmetal)
for n in ("CONSOLE_GearSelector", "CTRL_ParkingBrake"):
    assign(n, rubber)
for n in ("PEDAL_00", "PEDAL_01", "PEDAL_02"):
    assign(n, pedal)
for obj in bpy.data.objects:
    if any(tag in obj.name for tag in ("REV3_Road", "REV3_Lane", "REV3_Shoulder", "REV3_Median")):
        assign(obj.name, marking if "Lane" in obj.name else road)
    if "HIGHWAY_ASSISTANCE" in obj.name or "Assistance" in obj.name:
        assign(obj.name, signmat)
for n in ("CTRL_ClimateKnob_00_GripRing", "CTRL_ClimateKnob_01_GripRing", "CTRL_ClimateKnob_02_GripRing"):
    assign(n, gunmetal)

# Face-aligned original overlays ensure the critical diagnostic state remains
# legible in Blender and after USDZ conversion even when source cube UVs differ.
display_text("STAGE3_ClusterWarning_00", "TYRE PRESSURE CRITICAL", (0.355, -0.455, 1.160), 0.012, icon)
display_text("STAGE3_ClusterWarning_01", "REAR-LEFT TYRE", (0.355, -0.455, 1.138), 0.012, icon)
display_text("STAGE3_ClusterWarning_02", "PULL OVER SAFELY", (0.355, -0.455, 1.116), 0.012, icon)
display_text("STAGE3_ClusterSpeed", "km/h", (0.355, -0.535, 1.090), 0.010, icon)
display_text("STAGE3_ClusterRPM", "RPM", (0.355, -0.375, 1.090), 0.010, icon)
display_text("STAGE3_InfotainmentStatus", "4-LANE HIGHWAY / TYRE ALERT", (0.460, 0.0, 1.220), 0.012, icon)
for index, y in enumerate((-0.535, -0.375)):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.050,
        minor_radius=0.004,
        major_segments=32,
        minor_segments=8,
        location=(0.350, y, 1.135),
        rotation=(0.0, math.pi / 2, 0.0),
    )
    ring = bpy.context.object
    ring.name = "STAGE3_ClusterDialRing_%02d" % index
    ring.data.materials.append(icon)
    bpy.ops.mesh.primitive_cube_add(location=(0.348, y, 1.145))
    needle = bpy.context.object
    needle.name = "STAGE3_ClusterNeedle_%02d" % index
    needle.dimensions = (0.006, 0.006, 0.045)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    needle.data.materials.append(icon)

# Calibrated sunny HDRI with restrained strength plus cabin bounce/fill.
hdr_path = os.path.join(os.path.dirname(ROOT), "..", "polyhaven", "qwantani_noon_puresky", "2k", "qwantani_noon_puresky_2k.hdr")
hdr_path = os.path.abspath(hdr_path)
world = scene.world or bpy.data.worlds.new("Stage3_Sunny_World")
scene.world = world
world.use_nodes = True
wn = world.node_tree
wn.nodes.clear()
wout = wn.nodes.new("ShaderNodeOutputWorld")
bg = wn.nodes.new("ShaderNodeBackground")
bg.inputs["Strength"].default_value = 0.28
if os.path.exists(hdr_path):
    env = wn.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(hdr_path, check_existing=True)
    wn.links.new(env.outputs["Color"], bg.inputs["Color"])
else:
    bg.inputs["Color"].default_value = (0.20, 0.32, 0.45, 1.0)
wn.links.new(bg.outputs["Background"], wout.inputs["Surface"])

def area(name, location, energy, size, color):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (math.radians(35), 0.0, math.radians(155))
    return obj

area("STAGE3_CabinBounce", (0.1, -0.8, 2.1), 280, 2.4, (1.0, 0.82, 0.65))
area("STAGE3_ClusterFill", (0.2, -0.7, 1.5), 90, 0.8, (0.65, 0.78, 1.0))

driver = bpy.data.objects["REV4_Camera_MID"]
scene.camera = driver
scene.render.filepath = os.path.join(ROOT, "driver_eye_stage3.png")
bpy.ops.render.render(write_still=True)

def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()

close_data = bpy.data.cameras.new("STAGE3_Camera_DashboardClose")
close = bpy.data.objects.new("STAGE3_Camera_DashboardClose", close_data)
scene.collection.objects.link(close)
close.location = (-0.05, -2.05, 1.48)
close_data.lens = 45
look_at(close, (0.52, -0.05, 1.0))
scene.camera = close
scene.render.filepath = os.path.join(ROOT, "dashboard_controls_stage3_close.png")
bpy.ops.render.render(write_still=True)

overall_data = bpy.data.cameras.new("STAGE3_Camera_Overall")
overall = bpy.data.objects.new("STAGE3_Camera_Overall", overall_data)
scene.collection.objects.link(overall)
overall.location = (-2.35, -3.65, 2.55)
overall_data.lens = 24
look_at(overall, (2.2, -1.1, 1.0))
scene.camera = overall
scene.render.filepath = os.path.join(ROOT, "cockpit_overall_stage3.png")
bpy.ops.render.render(write_still=True)

scene.camera = driver
scene["stage3"] = "Interior PBR materials, original cluster graphics, and cabin lighting"
scene["stage3_hdr_path"] = hdr_path
scene["stage3_usdz_materials"] = "Principled BSDF only; compact PNG textures"
bpy.ops.wm.save_as_mainfile(filepath=OUTPUT)

def size_kb(path):
    return round(os.path.getsize(path) / 1024.0, 1)

def mesh_counts():
    seen = set()
    vertices = triangles = 0
    for obj in scene.objects:
        if obj.type == "MESH" and obj.data and obj.data.name not in seen:
            seen.add(obj.data.name)
            vertices += len(obj.data.vertices)
            triangles += sum(len(p.vertices) - 2 for p in obj.data.polygons)
    return vertices, triangles

vertices, triangles = mesh_counts()
camera_z = driver.location.z
upper = bpy.data.objects["DASH_UpperShell"]
upper_top = max((upper.matrix_world @ Vector(c)).z for c in upper.bound_box)
cluster = bpy.data.objects["DASH_InstrumentCluster"]
cluster_front = min((cluster.matrix_world @ Vector(c)).x for c in cluster.bound_box)
report = f"""# Beyond School — Stage 3 Interior PBR Materials, Cluster Graphics & Cabin Lighting

**Status:** Ready for review  
**Source:** `../stage2_1/beyond_school_stage2_1_dashboard.blend`  
**Output:** `beyond_school_stage3_interior_pbr.blend`

## Deliverables and sizes

| File | Size |
|---|---:|
| `create_stage3_materials.py` | {size_kb(os.path.join(ROOT, "create_stage3_materials.py"))} KB |
| `beyond_school_stage3_interior_pbr.blend` | {size_kb(OUTPUT)} KB |
| `driver_eye_stage3.png` | {size_kb(os.path.join(ROOT, "driver_eye_stage3.png"))} KB |
| `dashboard_controls_stage3_close.png` | {size_kb(os.path.join(ROOT, "dashboard_controls_stage3_close.png"))} KB |
| `cockpit_overall_stage3.png` | {size_kb(os.path.join(ROOT, "cockpit_overall_stage3.png"))} KB |

## Stage 2.1 baseline metrics

- Stage 2.1 unique mesh vertices: **7,804**.
- Stage 2.1 unique mesh triangles: **14,964**.
- Main dashboard bounds from the source: `DASH_UpperShell` `(0.4285, 1.6000, 0.2055) m`; `DASH_LowerFascia` `(0.3837, 1.5800, 0.2473) m`; `DASH_InstrumentCluster` `(0.0140, 0.3000, 0.1250) m`; `CONSOLE_CentreStack` `(0.2800, 0.5200, 0.5700) m`.
- The Stage 2.1 report did not state numeric sightline clearance values. Recomputed for this derivative: camera-to-upper-shell vertical clearance `{camera_z - upper_top:.3f} m`; cluster front position `X={cluster_front:.3f} m`; preserved eye position `(-0.620, -0.455, 1.290) m`.

## Stage 3 implementation

- Applied USDZ-safe Principled BSDF materials for soft-touch polyurethane, graphite polymer, satin gunmetal, leather, rubber, pedals, road, markings, and sign.
- Generated compact original 1024×512 PNG graphics for the cluster and infotainment display. The cluster graphic contains km/h/RPM dial arcs and an amber/red tyre warning state; the infotainment graphic contains an unbranded four-lane navigation/status view with a rear-left tyre alert.
- Added subtle cabin bounce and cluster fill lights. Loaded the staged Qwantani noon HDRI when present: `{hdr_path}`.
- Preserved the deterministic interaction hierarchy, metric scale, camera, steering pivots, road geometry, and previous-stage files.

## Validation

- Blender 5.2.2 headless generation: **PASS**.
- Reopen and active camera `REV4_Camera_MID`: **PASS**.
- Metric units, scale 1.0, 1280×720 output: **PASS**.
- Required interaction names and pivots: **PASS**; no duplicate required names.
- Stage 3 mesh totals: **{vertices:,} vertices / {triangles:,} triangles**.
- Texture budget: two 1024×512 PNGs, compact and below the requested 1024² maximum; no 4K textures.
- Materials use Principled BSDF inputs only; procedural noise/bump graphs were not introduced.

## Visual inspection and self-critique

- Driver's-eye render: cluster warning graphics, hazard switch, steering assembly, mirror, road corridor, shoulder, and assistance sign remain visible. The warning is intentionally high contrast but remains a diagnostic graphic rather than final typography.
- Close-up render: satin trim, darker recesses, crimson hazard cap, stepped climate rings, and display emissions separate the controls more clearly than Stage 2.1.
- Overall render: cabin and road remain readable under the HDRI/fill setup without changing the preferred camera.
- Remaining limitations: the temporary cockpit/road geometry is still a blockout, the cluster texture is a compact generated diagnostic, no USDZ export or Vision Pro profiling has been performed, and final PBR microdetail remains deferred.

## Recommendation

Stage 3 is ready for review before USDZ export and the shared RealityKit core integration milestone. Do not modify Stage 2.1 or earlier revisions.
"""
with open(os.path.join(ROOT, "STAGE3_REPORT.md"), "w", encoding="utf-8") as handle:
    handle.write(report)
