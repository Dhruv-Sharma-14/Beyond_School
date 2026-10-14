import math
import os

import bpy
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(
    os.path.dirname(ROOT),
    "stage2",
    "beyond_school_stage2_dashboard.blend",
)
OUTPUT = os.path.join(ROOT, "beyond_school_stage2_1_dashboard.blend")

bpy.ops.wm.open_mainfile(filepath=SOURCE)
scene = bpy.context.scene


def mat(name, color, roughness=0.7, emission=None):
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 0.22
    return material


def hide_legacy(prefixes):
    for obj in bpy.data.objects:
        if any(obj.name == prefix or obj.name.startswith(prefix + "_") for prefix in prefixes):
            obj.hide_render = True
            obj.hide_viewport = True
            obj["stage2_1_legacy_hidden"] = True
            if not obj.name.startswith("LEGACY_STAGE2_1_"):
                obj.name = "LEGACY_STAGE2_1_" + obj.name


def cube(name, location, dimensions, material, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    if bevel:
        modifier = obj.modifiers.new("Stage2_1_Contour", "BEVEL")
        modifier.width = bevel
        modifier.segments = 4
    return obj


def swept_profile(name, y_sections, profile, material, bevel=0.0):
    verts = []
    count = len(profile)
    for y, x_offset, z_offset in y_sections:
        verts.extend((x + x_offset, y, z + z_offset) for x, z in profile)
    faces = []
    for section in range(len(y_sections) - 1):
        base = section * count
        next_base = (section + 1) * count
        for point in range(count - 1):
            faces.append((base + point, base + point + 1, next_base + point + 1, next_base + point))
    faces.append(tuple(range(count - 1, -1, -1)))
    last = (len(y_sections) - 1) * count
    faces.append(tuple(last + point for point in range(count)))
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(material)
    for poly in mesh.polygons:
        poly.use_smooth = True
    if bevel:
        modifier = obj.modifiers.new("Stage2_1_ProfileBevel", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
    return obj


def torus(name, location, major, minor, material, rotation=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major,
        minor_radius=minor,
        major_segments=40,
        minor_segments=10,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    return obj


def cylinder(name, location, radius, depth, material, rotation=(0.0, 0.0, 0.0), vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    return obj


def uv_sphere(name, location, scale, material):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=32,
        ring_count=16,
        location=location,
    )
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    return obj


def text(name, body, location, size, material, rotation=(math.pi / 2, 0.0, -math.pi / 2)):
    bpy.ops.object.text_add(location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.body = body
    obj.data.align_x = "CENTER"
    obj.data.align_y = "CENTER"
    obj.data.size = size
    obj.data.extrude = 0.0015
    obj.data.materials.append(material)
    return obj


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def pivot_metadata(obj, position, role):
    obj["interactive"] = True
    obj["interaction_pivot_m"] = "(%.3f, %.3f, %.3f)" % tuple(position)
    obj["interaction_role"] = role


def empty_pivot(name, location):
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=location)
    obj = bpy.context.object
    obj.name = name
    obj.empty_display_size = 0.06
    obj["pivot_role"] = "Stable interaction pivot"
    return obj


hide_legacy(
    [
        "DASH_UpperShell",
        "DASH_LowerFascia",
        "DASH_AccentRail",
        "DASH_InstrumentBinnacle",
        "DASH_InstrumentClusterBezel",
        "DASH_InstrumentCluster",
        "DASH_ClusterDial",
        "DASH_GloveboxDoor",
        "DASH_GloveboxSeam",
        "CONSOLE_CentreStack",
        "CONSOLE_InfotainmentFrame",
        "CONSOLE_InfotainmentScreen",
        "CONSOLE_InfotainmentMark",
        "CONSOLE_AirVent",
        "CTRL_ClimatePanel",
        "CTRL_ClimateKnob",
        "CTRL_ClimateMark",
        "CONSOLE_CentreTunnel",
        "CONSOLE_GearSelectorBase",
        "CONSOLE_GearSelector",
        "CTRL_ParkingBrakeBase",
        "CTRL_ParkingBrake",
        "STEERING_ColumnShroud",
        "FOOTWELL_DriverTrim",
        "PEDAL",
    ]
)

dark = mat("STAGE2_1_Dashboard_Dark", (0.045, 0.052, 0.058), 0.83)
soft = mat("STAGE2_1_Dashboard_Soft", (0.095, 0.105, 0.11), 0.74)
fascia = mat("STAGE2_1_Fascia", (0.19, 0.20, 0.20), 0.49)
trim = mat("STAGE2_1_Trim", (0.32, 0.34, 0.34), 0.34)
glass = mat("STAGE2_1_DisplayGlass", (0.008, 0.038, 0.044), 0.22, emission=(0.01, 0.08, 0.09))
mark = mat("STAGE2_1_DisplayMark", (0.62, 0.72, 0.70), 0.4, emission=(0.03, 0.05, 0.04))
red = mat("STAGE2_1_HazardRed", (0.66, 0.018, 0.012), 0.3)
rubber = mat("STAGE2_1_Rubber", (0.025, 0.027, 0.029), 0.86)
metal = mat("STAGE2_1_ControlMetal", (0.26, 0.27, 0.27), 0.3)

# Sculptural dashboard layers. Overlapping radiused shells form a continuous
# shoulder instead of a stack of independent cuboids.
upper = swept_profile(
    "DASH_UpperShell",
    [(-0.80, 0.035, 0.00), (-0.46, 0.00, 0.015), (0.0, -0.015, 0.03), (0.46, 0.0, 0.015), (0.80, 0.035, 0.00)],
    [(0.49, 0.80), (0.53, 0.88), (0.64, 0.96), (0.78, 0.98), (0.88, 0.91), (0.84, 0.84)],
    soft,
    0.025,
)
upper["design_role"] = "Continuous swept upper dashboard shoulder"
lower = swept_profile(
    "DASH_LowerFascia",
    [(-0.79, 0.03, 0.0), (-0.45, 0.0, 0.0), (0.0, -0.02, 0.0), (0.45, 0.0, 0.0), (0.79, 0.03, 0.0)],
    [(0.50, 0.52), (0.53, 0.66), (0.62, 0.75), (0.78, 0.77), (0.84, 0.68), (0.81, 0.55)],
    fascia,
    0.022,
)
lower["design_role"] = "Shaped lower fascia with footwell transition"
rail = cube("DASH_AccentRail", (0.49, 0.0, 0.89), (0.035, 1.43, 0.045), trim, 0.02)
rail.rotation_euler[2] = math.radians(-2.0)
cube("DASH_UpperContourInset", (0.49, 0.0, 0.82), (0.028, 1.26, 0.09), dark, 0.035)

# Driver binnacle: hood, recessed bezel, and replaceable instrument surfaces.
binnacle = cube("DASH_InstrumentBinnacle", (0.535, -0.455, 1.135), (0.23, 0.42, 0.18), dark, 0.075)
binnacle.rotation_euler[1] = math.radians(-4.0)
binnacle["design_role"] = "Recessed instrument binnacle"
bezel = cube("DASH_InstrumentClusterBezel", (0.405, -0.455, 1.135), (0.07, 0.36, 0.17), trim, 0.035)
bezel.rotation_euler[1] = math.radians(-4.0)
cluster = cube("DASH_InstrumentCluster", (0.435, -0.455, 1.135), (0.014, 0.30, 0.125), glass, 0.025)
cluster.rotation_euler[1] = math.radians(-4.0)
cluster["display_placeholder"] = "Replaceable runtime instrument surface"
for index, y in enumerate((-0.535, -0.375)):
    dial = cylinder(
        "DASH_ClusterDial_%02d" % index,
        (0.416, y, 1.135),
        0.043,
        0.008,
        mark,
        rotation=(0.0, math.pi / 2, 0.0),
    )
    dial["display_role"] = "Replaceable dial surface"
    for tick in range(4):
        theta = math.radians(-55 + tick * 36)
        uv_sphere(
            "DASH_ClusterTick_%02d_%02d" % (index, tick),
            (0.356, y + math.sin(theta) * 0.031, 1.135 + math.cos(theta) * 0.031),
            (0.004, 0.004, 0.004),
            mark,
        )

# Integrated centre stack with a soft surround, recessed display, vents, and
# climate panel following the fascia rather than floating in front of it.
stack = cube("CONSOLE_CentreStack", (0.67, 0.0, 1.02), (0.28, 0.52, 0.57), soft, 0.085)
stack.rotation_euler[2] = math.radians(-4.0)
stack["design_role"] = "Integrated centre-stack surround"
frame = cube("CONSOLE_InfotainmentFrame", (0.505, 0.0, 1.22), (0.024, 0.37, 0.22), trim, 0.04)
frame.rotation_euler[2] = math.radians(-4.0)
screen = cube("CONSOLE_InfotainmentScreen", (0.488, 0.0, 1.22), (0.012, 0.315, 0.16), glass, 0.02)
screen.rotation_euler[2] = math.radians(-4.0)
screen["display_placeholder"] = "Neutral replaceable infotainment surface"
text("CONSOLE_InfotainmentMark", "READY", (0.478, 0.0, 1.22), 0.045, mark)

for index, y in enumerate((-0.16, 0.16)):
    vent = cube("CONSOLE_AirVent_%02d" % index, (0.472, y, 1.015), (0.022, 0.15, 0.065), dark, 0.03)
    vent["interaction_role"] = "Adjustable air vent"
    for slot in range(3):
        sl = cube(
            "CONSOLE_AirVent_%02d_Slot_%02d" % (index, slot),
            (0.452, y - 0.042 + slot * 0.042, 1.015),
            (0.008, 0.018, 0.04),
            trim,
            0.004,
        )
        sl["interaction_role"] = "Vent directional slat"

# Recessed surrounds prevent the vents and hazard from reading as floating
# blocks on the fascia.
cube("CONSOLE_VentSurround", (0.455, 0.0, 1.015), (0.035, 0.43, 0.18), fascia, 0.045)
cube("CONSOLE_HazardRecess", (0.452, 0.0, 1.065), (0.035, 0.17, 0.09), dark, 0.025)

# Keep the required hazard object names stable by moving the visible Stage 2
# controls aside only through legacy hiding, then rebuilding them here.
hazard_pivot = cylinder("BTN_HazardSwitch_Pivot", (0.445, 0.0, 1.065), 0.032, 0.028, rubber, rotation=(0.0, math.pi / 2, 0.0))
hazard_pivot["pivot_role"] = "Hazard cap press pivot"
hazard_cap = cube("BTN_HazardSwitch_Cap", (0.414, 0.0, 1.065), (0.018, 0.105, 0.05), red, 0.014)
hazard_icon = text("BTN_HazardSwitch_Icon", "△", (0.391, 0.0, 1.065), 0.042, mark)
hazard = cube("BTN_HazardSwitch", (0.429, 0.0, 1.065), (0.032, 0.12, 0.06), red, 0.016)
pivot_metadata(hazard, (0.445, 0.0, 1.065), "Physical hazard switch press")
hazard["interaction_pivot"] = "BTN_HazardSwitch_Pivot"

climate_panel = cube("CTRL_ClimatePanel", (0.47, 0.0, 0.87), (0.022, 0.46, 0.15), dark, 0.035)
for index, y in enumerate((-0.15, 0.0, 0.15)):
    knob = cylinder("CTRL_ClimateKnob_%02d" % index, (0.447, y, 0.87), 0.047, 0.03, metal, rotation=(0.0, math.pi / 2, 0.0))
    pivot_metadata(knob, (0.447, y, 0.87), "Rotary climate-control knob")
    knob["interaction_axis"] = "local X rotation"
    torus("CTRL_ClimateKnob_%02d_GripRing" % index, (0.427, y, 0.87), 0.052, 0.008, trim, rotation=(0.0, math.pi / 2, 0.0))
    cylinder("CTRL_ClimateKnob_%02d_InnerFace" % index, (0.423, y, 0.87), 0.030, 0.008, dark, rotation=(0.0, math.pi / 2, 0.0))
    cube("CTRL_ClimateMark_%02d" % index, (0.424, y, 0.914), (0.008, 0.012, 0.016), mark, 0.003)

# A tapered-looking console stack supports the selector and brake rather than
# leaving them on an isolated flat tunnel.
console = cube("CONSOLE_CentreTunnel", (0.02, 0.08, 0.43), (1.18, 0.46, 0.16), fascia, 0.075)
console.rotation_euler[2] = math.radians(-2.0)
gear_base = cube("CONSOLE_GearSelectorBase", (0.10, 0.08, 0.54), (0.25, 0.21, 0.09), trim, 0.04)
gear_pivot = bpy.data.objects.get("CONSOLE_GearSelector_Pivot")
if gear_pivot is None:
    gear_pivot = empty_pivot("CONSOLE_GearSelector_Pivot", (0.10, 0.08, 0.55))
gear_pivot.location = (0.10, 0.08, 0.55)
gear = cube("CONSOLE_GearSelector", (0.10, 0.08, 0.66), (0.095, 0.12, 0.22), rubber, 0.045)
gear.parent = gear_pivot
gear.location = (0.0, 0.0, 0.11)
gear["variant"] = "manual_or_automatic"
gear["interaction_pivot"] = "CONSOLE_GearSelector_Pivot"
pivot_metadata(gear, (0.10, 0.08, 0.55), "Configurable gear selector")

brake_base = cube("CTRL_ParkingBrakeBase", (-0.18, 0.17, 0.47), (0.27, 0.15, 0.075), trim, 0.03)
brake_pivot = bpy.data.objects.get("CTRL_ParkingBrake_Pivot")
if brake_pivot is None:
    brake_pivot = empty_pivot("CTRL_ParkingBrake_Pivot", (-0.18, 0.17, 0.47))
brake_pivot.location = (-0.18, 0.17, 0.47)
brake = cube("CTRL_ParkingBrake", (-0.18, 0.17, 0.56), (0.075, 0.095, 0.17), rubber, 0.035)
brake.parent = brake_pivot
brake.location = (0.0, 0.0, 0.09)
brake["variant"] = "manual_handbrake_or_electronic_switch"
brake["interaction_pivot"] = "CTRL_ParkingBrake_Pivot"
pivot_metadata(brake, (-0.18, 0.17, 0.47), "Configurable parking brake")

glove = cube("DASH_GloveboxDoor", (0.40, 0.48, 0.76), (0.03, 0.52, 0.22), fascia, 0.05)
glove["interaction_role"] = "Future glovebox door"
cube("DASH_GloveboxSeam", (0.381, 0.48, 0.76), (0.01, 0.47, 0.01), trim, 0.003)
cube("STEERING_ColumnShroud", (0.34, -0.455, 0.91), (0.25, 0.15, 0.14), rubber, 0.05)
cube("FOOTWELL_DriverTrim", (0.38, -0.46, 0.37), (0.45, 0.54, 0.055), rubber, 0.03)
for index, y in enumerate((-0.59, -0.45, -0.31)):
    pedal = cube("PEDAL_%02d" % index, (0.24, y, 0.35), (0.055, 0.07, 0.14), metal, 0.016)
    pedal["interaction_role"] = "Pedal surface placeholder"

# Diagnostic cameras only; the approved MID driver's-eye camera remains active
# after rendering and its transform is not changed.
driver = bpy.data.objects["REV4_Camera_MID"]
scene.camera = driver
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.filepath = os.path.join(ROOT, "driver_eye_stage2_1.png")
bpy.ops.render.render(write_still=True)

close_data = bpy.data.cameras.new("STAGE2_1_Camera_DashboardClose")
close = bpy.data.objects.new("STAGE2_1_Camera_DashboardClose", close_data)
scene.collection.objects.link(close)
close.location = (-0.05, -2.05, 1.48)
close_data.lens = 45
look_at(close, (0.52, -0.05, 1.00))
scene.camera = close
scene.render.filepath = os.path.join(ROOT, "dashboard_controls_stage2_1_close.png")
bpy.ops.render.render(write_still=True)

overall_data = bpy.data.cameras.new("STAGE2_1_Camera_Overall")
overall = bpy.data.objects.new("STAGE2_1_Camera_Overall", overall_data)
scene.collection.objects.link(overall)
overall.location = (-2.35, -3.65, 2.55)
overall_data.lens = 24
look_at(overall, (2.2, -1.1, 1.0))
scene.camera = overall
scene.render.filepath = os.path.join(ROOT, "cockpit_overall_stage2_1.png")
bpy.ops.render.render(write_still=True)

scene.camera = driver
scene["stage2_1"] = "Dashboard geometry refinement"
scene["stage2_1_source"] = "Stage 2 preserved as input"
scene["stage2_1_camera"] = "REV4_Camera_MID"
scene["stage2_1_preserved"] = "Revision 5 steering, seats, mirrors, road, lane markings and assistance sign"
scene["stage2_1_interaction_names"] = "Hazard, climate, gear selector and parking brake names preserved"
bpy.ops.wm.save_as_mainfile(filepath=OUTPUT)
