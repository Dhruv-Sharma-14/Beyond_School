import math
import os

import bpy
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(
    os.path.dirname(ROOT),
    "revision5",
    "beyond_school_cockpit_blockout_revision5.blend",
)
OUTPUT = os.path.join(ROOT, "beyond_school_stage2_dashboard.blend")

bpy.ops.wm.open_mainfile(filepath=SOURCE)
scene = bpy.context.scene


def material(name, color, roughness=0.7, metallic=0.0, emission=None):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 0.35
    return mat


def hide_legacy(names):
    for name in names:
        obj = bpy.data.objects.get(name)
        if obj:
            obj.hide_render = True
            obj.hide_viewport = True
            obj["stage2_legacy_hidden"] = True
            obj.name = "LEGACY_STAGE2_" + name


def cube(name, location, dimensions, mat, bevel=0.0, parent=None):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("Stage2_SoftContour", "BEVEL")
        mod.width = bevel
        mod.segments = 3
    if parent:
        world = obj.matrix_world.copy()
        obj.parent = parent
        obj.matrix_world = world
    return obj


def cylinder(name, location, radius, depth, mat, rotation=(0.0, 0.0, 0.0), vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    if mat:
        obj.data.materials.append(mat)
    return obj


def torus(name, location, major, minor, mat, rotation=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major,
        minor_radius=minor,
        major_segments=48,
        minor_segments=12,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    return obj


def text(name, body, location, size, mat, rotation=(math.pi / 2, 0.0, -math.pi / 2)):
    bpy.ops.object.text_add(location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.body = body
    obj.data.align_x = "CENTER"
    obj.data.align_y = "CENTER"
    obj.data.size = size
    obj.data.extrude = 0.002
    obj.data.materials.append(mat)
    return obj


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def set_pivot(obj, location):
    obj["interaction_pivot_m"] = "(%.3f, %.3f, %.3f)" % tuple(location)
    obj["interactive"] = True


hide_legacy(
    [
        "DASH_Shell",
        "DASH_UpperPad",
        "DASH_InstrumentBinnacle",
        "DASH_InstrumentCluster",
        "CONSOLE_CentreStack",
        "CONSOLE_InfotainmentScreen",
        "CONSOLE_GearSelector",
        "BTN_HazardSwitch",
        "BTN_HazardSwitch_Icon",
        "MARKER_HazardSwitch",
    ]
)

dashboard = material("STAGE2_Dashboard_SoftTouch", (0.075, 0.085, 0.09), 0.78)
fascia = material("STAGE2_Fascia_Satin", (0.16, 0.18, 0.19), 0.52)
trim = material("STAGE2_Trim_Satin", (0.28, 0.30, 0.31), 0.38, metallic=0.35)
screen = material("STAGE2_Display_Blank", (0.025, 0.10, 0.13), 0.28, emission=(0.02, 0.12, 0.16))
white = material("STAGE2_Display_Markings", (0.75, 0.82, 0.82), 0.42, emission=(0.06, 0.08, 0.08))
red = material("STAGE2_Hazard_Red", (0.72, 0.025, 0.018), 0.32, emission=(0.18, 0.01, 0.005))
rubber = material("STAGE2_Rubber", (0.025, 0.028, 0.03), 0.84)
metal = material("STAGE2_Control_Metal", (0.26, 0.28, 0.29), 0.32, metallic=0.65)

# Main dashboard architecture: layered shells keep the silhouette curved and
# leave the existing steering wheel, cluster location, and road view intact.
upper = cube("DASH_UpperShell", (0.74, 0.0, 0.90), (0.46, 1.62, 0.20), dashboard, 0.085)
upper["design_role"] = "Continuous upper dashboard shell"
lower = cube("DASH_LowerFascia", (0.68, 0.0, 0.64), (0.42, 1.64, 0.34), fascia, 0.075)
lower["design_role"] = "Lower fascia and footwell transition"
accent = cube("DASH_AccentRail", (0.475, 0.0, 0.91), (0.035, 1.42, 0.055), trim, 0.018)

# Driver instrument binnacle, bezel, and two neutral dial surfaces.
binnacle = cube("DASH_InstrumentBinnacle", (0.54, -0.455, 1.14), (0.25, 0.43, 0.20), dashboard, 0.055)
binnacle["design_role"] = "Driver instrument hood"
bezel = cube("DASH_InstrumentClusterBezel", (0.405, -0.455, 1.145), (0.035, 0.34, 0.17), trim, 0.025)
cluster = cube("DASH_InstrumentCluster", (0.382, -0.455, 1.145), (0.018, 0.285, 0.12), screen, 0.012)
cluster["display_placeholder"] = "Neutral diagnostic display; production graphics deferred"
for index, y in enumerate((-0.535, -0.375)):
    dial = cylinder(
        "DASH_ClusterDial_%02d" % index,
        (0.365, y, 1.145),
        0.048,
        0.012,
        white,
        rotation=(0.0, math.pi / 2, 0.0),
        vertices=32,
    )
    dial["display_role"] = "Instrument dial surface"

# Centre stack with separate vents, screen, hazard assembly, and climate bank.
stack = cube("CONSOLE_CentreStack", (0.70, 0.0, 1.02), (0.34, 0.56, 0.62), fascia, 0.055)
stack["design_role"] = "Centre-stack structural surround"
screen_frame = cube("CONSOLE_InfotainmentFrame", (0.505, 0.0, 1.23), (0.025, 0.40, 0.24), trim, 0.025)
infotainment = cube("CONSOLE_InfotainmentScreen", (0.487, 0.0, 1.23), (0.014, 0.34, 0.18), screen, 0.012)
infotainment["display_placeholder"] = "Original neutral infotainment surface"
text("CONSOLE_InfotainmentMark", "BEYOND", (0.475, 0.0, 1.23), 0.065, white)

for index, y in enumerate((-0.17, 0.17)):
    vent = cube("CONSOLE_AirVent_%02d" % index, (0.47, y, 1.02), (0.025, 0.18, 0.075), rubber, 0.025)
    vent["interaction_role"] = "Adjustable air vent"
    for slot in range(3):
        cube(
            "CONSOLE_AirVent_%02d_Slot_%02d" % (index, slot),
            (0.448, y - 0.05 + slot * 0.05, 1.02),
            (0.012, 0.018, 0.045),
            trim,
            0.006,
        )

hazard_pivot = cylinder("BTN_HazardSwitch_Pivot", (0.445, 0.0, 1.075), 0.036, 0.035, rubber, rotation=(0.0, math.pi / 2, 0.0))
hazard_pivot.rotation_euler[1] = math.pi / 2
hazard_pivot["pivot_role"] = "Hazard cap press pivot"
hazard_cap = cube("BTN_HazardSwitch_Cap", (0.414, 0.0, 1.075), (0.018, 0.115, 0.052), red, 0.016)
hazard_cap["interaction_role"] = "Pressable hazard switch cap"
hazard_icon = text("BTN_HazardSwitch_Icon", "△", (0.392, 0.0, 1.075), 0.052, white)
hazard = cube("BTN_HazardSwitch", (0.43, 0.0, 1.075), (0.035, 0.13, 0.065), red, 0.018)
hazard["interactive"] = True
hazard["interaction_pivot"] = "BTN_HazardSwitch_Pivot"
hazard["control_type"] = "momentary push"
set_pivot(hazard, (0.445, 0.0, 1.075))

for index, y in enumerate((-0.16, 0.0, 0.16)):
    climate = cylinder("CTRL_ClimateKnob_%02d" % index, (0.455, y, 0.88), 0.052, 0.035, metal, rotation=(0.0, math.pi / 2, 0.0))
    climate["interactive"] = True
    climate["control_role"] = "Climate control knob"
    set_pivot(climate, (0.455, y, 0.88))
    mark = cube("CTRL_ClimateMark_%02d" % index, (0.432, y, 0.93), (0.012, 0.014, 0.018), white, 0.004)

climate_panel = cube("CTRL_ClimatePanel", (0.47, 0.0, 0.88), (0.025, 0.50, 0.16), fascia, 0.02)
climate_panel["control_role"] = "Separate climate-control bank"

# Lower console, selector and configurable parking-brake control.
console = cube("CONSOLE_CentreTunnel", (0.10, 0.08, 0.43), (1.30, 0.48, 0.18), fascia, 0.055)
gear_base = cube("CONSOLE_GearSelectorBase", (0.12, 0.08, 0.55), (0.28, 0.24, 0.10), trim, 0.03)
gear = cube("CONSOLE_GearSelector", (0.10, 0.08, 0.66), (0.10, 0.13, 0.24), rubber, 0.035)
gear["interactive"] = True
gear["variant"] = "manual_or_automatic"
gear["interaction_pivot"] = "CONSOLE_GearSelector_Pivot"
gear_pivot = bpy.data.objects.new("CONSOLE_GearSelector_Pivot", None)
scene.collection.objects.link(gear_pivot)
gear_pivot.location = (0.10, 0.08, 0.55)
gear.parent = gear_pivot
set_pivot(gear, (0.10, 0.08, 0.55))

handbrake_base = cube("CTRL_ParkingBrakeBase", (-0.20, 0.18, 0.47), (0.30, 0.16, 0.08), trim, 0.025)
handbrake = cube("CTRL_ParkingBrake", (-0.20, 0.18, 0.57), (0.08, 0.10, 0.20), rubber, 0.03)
handbrake["interactive"] = True
handbrake["variant"] = "manual_handbrake_or_electronic_switch"
handbrake["interaction_pivot"] = "CTRL_ParkingBrake_Pivot"
brake_pivot = bpy.data.objects.new("CTRL_ParkingBrake_Pivot", None)
scene.collection.objects.link(brake_pivot)
brake_pivot.location = (-0.20, 0.18, 0.47)
handbrake.parent = brake_pivot
set_pivot(handbrake, (-0.20, 0.18, 0.47))

# Glovebox seam, passenger trim, column shroud, pedal surfaces and footwell.
glove = cube("DASH_GloveboxDoor", (0.42, 0.49, 0.78), (0.035, 0.55, 0.25), fascia, 0.035)
glove["interaction_role"] = "Future glovebox door"
cube("DASH_GloveboxSeam", (0.397, 0.49, 0.78), (0.012, 0.50, 0.012), trim, 0.004)
cube("STEERING_ColumnShroud", (0.34, -0.455, 0.91), (0.28, 0.16, 0.16), rubber, 0.04)
cube("FOOTWELL_DriverTrim", (0.40, -0.46, 0.38), (0.48, 0.58, 0.06), rubber, 0.025)
for index, y in enumerate((-0.60, -0.45, -0.30)):
    pedal = cube("PEDAL_%02d" % index, (0.25, y, 0.36), (0.06, 0.08, 0.16), metal, 0.018)
    pedal["interaction_role"] = "Pedal surface placeholder"

# Review cameras. The approved MID camera remains unchanged and active after
# rendering; these are derivative diagnostic views only.
driver_camera = bpy.data.objects["REV4_Camera_MID"]
scene.camera = driver_camera
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.filepath = os.path.join(ROOT, "driver_eye_stage2.png")
bpy.ops.render.render(write_still=True)

close_data = bpy.data.cameras.new("STAGE2_Camera_DashboardClose")
close = bpy.data.objects.new("STAGE2_Camera_DashboardClose", close_data)
scene.collection.objects.link(close)
close.location = (-0.05, -2.05, 1.48)
close_data.lens = 45
look_at(close, (0.52, -0.05, 1.02))
scene.camera = close
scene.render.filepath = os.path.join(ROOT, "dashboard_controls_stage2_close.png")
bpy.ops.render.render(write_still=True)

overall_data = bpy.data.cameras.new("STAGE2_Camera_Overall")
overall = bpy.data.objects.new("STAGE2_Camera_Overall", overall_data)
scene.collection.objects.link(overall)
overall.location = (-2.35, -3.65, 2.55)
overall_data.lens = 24
look_at(overall, (2.2, -1.1, 1.0))
scene.camera = overall
scene.render.filepath = os.path.join(ROOT, "cockpit_overall_stage2.png")
bpy.ops.render.render(write_still=True)

scene.camera = driver_camera
scene["stage2"] = "Dashboard detailing and control separation"
scene["stage2_source"] = "Revision 5 preserved as input"
scene["stage2_coordinate_system"] = "+X forward, -Y driver, +Y passenger, +Z up; metres"
scene["stage2_preserved_objects"] = "STEERING_ROOT, STEERING_Wheel, STEERING_Hub, STEERING_Column, MARKER_DriverEye, MIRROR_Driver, REV3 road/sign geometry"
scene["stage2_control_variants"] = "Gear selector supports manual_or_automatic; parking brake supports manual_handbrake_or_electronic_switch"
bpy.ops.wm.save_as_mainfile(filepath=OUTPUT)
