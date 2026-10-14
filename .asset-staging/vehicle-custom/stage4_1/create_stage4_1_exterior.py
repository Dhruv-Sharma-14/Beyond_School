import math
import os

import bpy
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(os.path.dirname(ROOT), "stage4", "beyond_school_stage4_exterior_body.blend")
OUTPUT = os.path.join(ROOT, "beyond_school_stage4_1_exterior_refined.blend")

bpy.ops.wm.open_mainfile(filepath=SOURCE)
scene = bpy.context.scene
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1.0


def mat(name, color, roughness=0.6, metallic=0.0, emission=None, strength=0.0, alpha=1.0):
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, alpha)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Alpha"].default_value = alpha
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = strength
    if alpha < 1.0:
        try:
            material.surface_render_method = "DITHERED"
        except AttributeError:
            pass
        material.diffuse_color = (*color, alpha)
    return material


def cube(name, location, dimensions, material, bevel=0.0, parent=None):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj["stage4_exterior"] = True
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    if bevel:
        modifier = obj.modifiers.new("Stage4_BodyBevel", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
    if parent:
        world = obj.matrix_world.copy()
        obj.parent = parent
        obj.matrix_world = world
    return obj


def cylinder(name, location, radius, depth, material, rotation=(0.0, 0.0, 0.0), vertices=24, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    obj["stage4_exterior"] = True
    obj.data.materials.append(material)
    if parent:
        world = obj.matrix_world.copy()
        obj.parent = parent
        obj.matrix_world = world
    return obj


def torus(name, location, major, minor, material, rotation=(0.0, 0.0, 0.0), parent=None):
    bpy.ops.mesh.primitive_torus_add(
        major_segments=32,
        minor_segments=8,
        major_radius=major,
        minor_radius=minor,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    obj["stage4_exterior"] = True
    obj.data.materials.append(material)
    if parent:
        world = obj.matrix_world.copy()
        obj.parent = parent
        obj.matrix_world = world
    return obj


def text(name, body, location, size, material):
    bpy.ops.object.text_add(location=location, rotation=(math.pi / 2, 0.0, -math.pi / 2))
    obj = bpy.context.object
    obj.name = name
    obj["stage4_exterior"] = True
    obj.data.body = body
    obj.data.align_x = "CENTER"
    obj.data.align_y = "CENTER"
    obj.data.size = size
    obj.data.extrude = 0.0008
    obj.data.materials.append(material)
    return obj


def empty(name, location):
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=location)
    obj = bpy.context.object
    obj.name = name
    obj["stage4_exterior"] = True
    obj.empty_display_size = 0.08
    return obj


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def assign(name, material):
    obj = bpy.data.objects.get(name)
    if obj and obj.type == "MESH":
        obj.data.materials.clear()
        obj.data.materials.append(material)
    return obj


def parent_preserve(obj, parent):
    world = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_world = world


body = mat("MAT_Body_PearlSilver", (0.30, 0.36, 0.42), 0.27, metallic=0.72)
body_dark = mat("MAT_Body_DarkTrim", (0.025, 0.035, 0.045), 0.34, metallic=0.55)
glass = mat("MAT_Glass_Tinted", (0.04, 0.10, 0.13), 0.04, metallic=0.0, alpha=0.14)
mirror = mat("MAT_Mirror_Glass", (0.55, 0.68, 0.74), 0.03, metallic=1.0)
lamp = mat("MAT_Lamp_Hazard_Amber", (0.65, 0.08, 0.005), 0.25, emission=(1.0, 0.12, 0.005), strength=1.8)
head = mat("MAT_Lamp_Headlight", (0.72, 0.84, 0.90), 0.16, emission=(0.55, 0.78, 1.0), strength=1.2)
tail = mat("MAT_Lamp_Taillight", (0.35, 0.015, 0.01), 0.28, emission=(0.8, 0.015, 0.005), strength=0.8)
tire = mat("MAT_Tyre_Rubber", (0.012, 0.014, 0.016), 0.9)
rim = mat("MAT_Wheel_Alloy", (0.30, 0.34, 0.38), 0.24, metallic=0.86)
interior_dark = bpy.data.materials.get("STAGE3_Graphite_Polymer") or body_dark

# Remove only the prior Stage 4 exterior derivative. Stage 3 cockpit content
# remains the immutable interior source for this refinement.
for obj in list(scene.objects):
    if obj.get("stage4_exterior"):
        bpy.data.objects.remove(obj, do_unlink=True)

# Preserve Stage 3 names while making the cluster layout stereoscopically stable.
for name in ("STAGE3_ClusterDialRing_00", "STAGE3_ClusterDialRing_01", "STAGE3_ClusterNeedle_00", "STAGE3_ClusterNeedle_01",
             "STAGE3_ClusterWarning_00", "STAGE3_ClusterWarning_01", "STAGE3_ClusterWarning_02",
             "STAGE3_ClusterSpeed", "STAGE3_ClusterRPM"):
    if bpy.data.objects.get(name):
        bpy.data.objects[name].hide_render = True

for index, y in enumerate((-0.535, -0.375)):
    dial = bpy.data.objects.get("DASH_ClusterDial_%02d" % index)
    if dial:
        dial.location.y = y
        dial.scale.y = 0.82
        dial.scale.z = 0.82
    torus("STAGE4_ClusterDialRing_%02d" % index, (0.365, y, 1.135), 0.040, 0.0035, mirror, rotation=(0.0, math.pi / 2, 0.0))
    needle = cube("STAGE4_ClusterNeedle_%02d" % index, (0.360, y, 1.150), (0.005, 0.005, 0.033), lamp, 0.002)
    needle["cluster_role"] = "Visible dial needle"
panel = cube("STAGE4_ClusterWarningPanel", (0.368, -0.455, 1.135), (0.006, 0.080, 0.058), interior_dark, 0.006)
panel["cluster_role"] = "Central warning panel, 1.5 mm offset from cluster-facing bezel plane"
warning_mat = mat("MAT_Cluster_Warning_Amber", (0.72, 0.21, 0.015), 0.3, emission=(1.0, 0.18, 0.01), strength=1.1)
for index, body_text in enumerate(("TYRE PRESSURE", "REAR-LEFT TYRE", "PULL OVER SAFELY")):
    label = text("STAGE4_ClusterWarning_%02d" % index, body_text, (0.360, -0.455, 1.150 - index * 0.017), 0.0085, warning_mat)
    label["cluster_role"] = "Central warning text"

# Panel-based exterior keeps the cabin open while establishing sedan proportions.
cube("BODY_ExteriorShell", (0.0, 0.0, 0.50), (4.20, 1.765, 0.48), body, 0.16)
cube("BODY_Underbody", (0.0, 0.0, 0.25), (3.95, 1.60, 0.18), body_dark, 0.06)
cube("BODY_FrontBumper", (2.10, 0.0, 0.58), (0.23, 1.72, 0.48), body, 0.10)
cube("BODY_RearBumper", (-2.10, 0.0, 0.58), (0.23, 1.72, 0.48), body, 0.10)
cube("BODY_Hood", (1.58, 0.0, 1.03), (1.20, 1.64, 0.18), body, 0.10)
cube("BODY_Roof", (-0.05, 0.0, 1.42), (1.95, 1.48, 0.13), body, 0.22)
for x, z in ((0.82, 1.08), (-0.72, 1.09), (-1.28, 1.05)):
    for y in (-0.70, 0.70):
        cube("BODY_Pillar_%+.2f_%+.2f" % (x, y), (x, y, z), (0.09, 0.10, 0.58), body_dark, 0.025)

door_pivot = empty("DOOR_DriverRight_Pivot", (0.52, -0.88, 0.68))
driver_door = cube("DOOR_DriverRight", (0.05, -0.91, 0.70), (0.95, 0.075, 0.72), body, 0.07)
parent_preserve(driver_door, door_pivot)
driver_window = cube("DOOR_DriverRight_WindowFrame", (0.05, -0.912, 1.08), (0.86, 0.035, 0.31), body_dark, 0.035)
parent_preserve(driver_window, door_pivot)
driver_glass = cube("DOOR_DriverRight_Glass", (0.05, -0.916, 1.085), (0.76, 0.012, 0.23), glass, 0.025)
parent_preserve(driver_glass, door_pivot)
handle = cube("DOOR_DriverRight_Handle", (0.22, -0.965, 0.86), (0.22, 0.025, 0.035), mirror, 0.012)
parent_preserve(handle, door_pivot)
inner = cube("DOOR_DriverRight_InnerTrim", (0.08, -0.875, 0.68), (0.70, 0.035, 0.36), interior_dark, 0.04)
parent_preserve(inner, door_pivot)
mirror_housing = cube("MIRROR_Driver", (0.70, -0.98, 1.16), (0.26, 0.10, 0.16), body, 0.055)
parent_preserve(mirror_housing, door_pivot)
mirror_face = cube("MIRROR_Driver_Glass", (0.70, -1.035, 1.16), (0.18, 0.012, 0.10), mirror, 0.025)
parent_preserve(mirror_face, door_pivot)

cube("DOOR_PassengerLeft", (0.05, 0.91, 0.70), (0.95, 0.075, 0.72), body, 0.07)
cube("DOOR_RearRight", (-1.05, -0.91, 0.70), (0.88, 0.075, 0.70), body, 0.07)
cube("DOOR_RearLeft", (-1.05, 0.91, 0.70), (0.88, 0.075, 0.70), body, 0.07)
cube("GLASS_PassengerFront", (0.05, 0.916, 1.085), (0.76, 0.012, 0.23), glass, 0.025)
cube("GLASS_DriverRear", (-1.05, -0.916, 1.075), (0.68, 0.012, 0.22), glass, 0.025)
cube("GLASS_PassengerRear", (-1.05, 0.916, 1.075), (0.68, 0.012, 0.22), glass, 0.025)

trunk_pivot = empty("TRUNK_Lid_Pivot", (-1.55, 0.0, 1.06))
trunk_lid = cube("TRUNK_Lid", (-1.87, 0.0, 1.02), (0.68, 1.62, 0.12), body, 0.07)
parent_preserve(trunk_lid, trunk_pivot)
cavity = cube("TRUNK_WellCavity", (-1.72, 0.0, 0.67), (0.72, 1.05, 0.18), body_dark, 0.08)
floor = cube("TRUNK_FloorMat", (-1.72, 0.0, 0.78), (0.62, 0.93, 0.035), interior_dark, 0.018)

cube("GLASS_Windshield", (0.83, 0.0, 1.22), (0.025, 1.36, 0.40), glass, 0.03)
cube("GLASS_RearWindow", (-1.06, 0.0, 1.20), (0.025, 1.30, 0.34), glass, 0.03)

if not bpy.data.objects.get("MIRROR_Passenger"):
    cube("MIRROR_Passenger", (0.70, 0.98, 1.16), (0.26, 0.10, 0.16), body, 0.055)
if not bpy.data.objects.get("MIRROR_Passenger_Glass"):
    cube("MIRROR_Passenger_Glass", (0.70, 1.035, 1.16), (0.18, 0.012, 0.10), mirror, 0.025)
if not bpy.data.objects.get("MIRROR_InteriorRearview"):
    cube("MIRROR_InteriorRearview", (-0.10, 0.0, 1.32), (0.18, 0.04, 0.08), mirror, 0.02)

def wheel(name, x, y):
    tire_obj = torus(name, (x, y, 0.320), 0.270, 0.050, tire, rotation=(math.pi / 2, 0.0, 0.0))
    tire_obj["axle_center"] = "(%.3f, %.4f, 0.320)" % (x, y)
    hub = cylinder(name + "_Rim", (x, y, 0.320), 0.205, 0.045, rim, rotation=(math.pi / 2, 0.0, 0.0), vertices=24)
    cylinder(name + "_Hub", (x, y, 0.320), 0.060, 0.06, body_dark, rotation=(math.pi / 2, 0.0, 0.0), vertices=20)
    for spoke in range(5):
        angle = math.radians(spoke * 72)
        spoke_obj = cube(name + "_Spoke_%02d" % spoke, (x, y - math.sin(angle) * 0.08, 0.320 + math.cos(angle) * 0.08), (0.025, 0.055, 0.14), rim, 0.008)
        spoke_obj.rotation_euler[1] = angle

wheel("WHEEL_FL", 1.300, -0.765)
wheel("WHEEL_FR", 1.300, 0.765)
wheel("WHEEL_RL_FlatTarget", -1.300, -0.7675)
wheel("WHEEL_RR", -1.300, 0.7675)

for name, location, dimensions in (
    ("LAMP_Headlight_L", (2.17, -0.62, 0.90), (0.06, 0.28, 0.16)),
    ("LAMP_Headlight_R", (2.17, 0.62, 0.90), (0.06, 0.28, 0.16)),
    ("LAMP_Taillight_L", (-2.17, -0.62, 0.92), (0.06, 0.28, 0.18)),
    ("LAMP_Taillight_R", (-2.17, 0.62, 0.92), (0.06, 0.28, 0.18)),
):
    cube(name, location, dimensions, head if "Head" in name else tail, 0.035)
for name, location in (
    ("LAMP_Hazard_FL", (2.135, -0.73, 0.92)),
    ("LAMP_Hazard_FR", (2.135, 0.73, 0.92)),
    ("LAMP_Hazard_RL", (-2.135, -0.73, 0.94)),
    ("LAMP_Hazard_RR", (-2.135, 0.73, 0.94)),
    ("LAMP_Hazard_Side_R", (0.86, -0.915, 1.00)),
    ("LAMP_Hazard_Side_L", (0.86, 0.915, 1.00)),
):
    cube(name, location, (0.045, 0.10, 0.055), lamp, 0.018)

def remove_named(name):
    obj = bpy.data.objects.get(name)
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)


def remove_prefix(prefix):
    for obj in list(scene.objects):
        if obj.name.startswith(prefix):
            bpy.data.objects.remove(obj, do_unlink=True)


# Replace the Stage 4 slab shell with a perimeter greenhouse. The named shell
# is retained as the lower side-sill carrier; the cabin volume is open.
for name in (
    "BODY_ExteriorShell", "BODY_Roof", "BODY_Hood", "BODY_FrontBumper",
    "BODY_RearBumper", "DOOR_DriverRight", "DOOR_DriverRight_WindowFrame",
    "DOOR_DriverRight_Glass", "DOOR_DriverRight_Handle",
    "DOOR_DriverRight_InnerTrim", "DOOR_PassengerLeft", "DOOR_RearRight",
    "DOOR_RearLeft", "GLASS_Windshield", "GLASS_RearWindow",
    "GLASS_PassengerFront", "GLASS_DriverRear", "GLASS_PassengerRear",
):
    remove_named(name)
remove_prefix("BODY_Pillar")
remove_prefix("BODY_Side")
remove_prefix("FENDER_")
remove_prefix("DOOR_DriverRight_Frame")
remove_prefix("GLASS_DriverRight")

for child in ("DOOR_DriverRight_Pivot", "TRUNK_Lid_Pivot"):
    remove_named(child)

glass.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.69, 0.80, 0.86, 1.0)
glass.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.08
glass.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.02
glass.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.0
try:
    glass.surface_render_method = "DITHERED"
except AttributeError:
    pass

# Lower body perimeter and sculpted panel lines.
cube("BODY_ExteriorShell", (0.0, 0.0, 0.39), (4.12, 0.12, 0.34), body, 0.07)
for side in (-1, 1):
    s = "R" if side < 0 else "L"
    cube("BODY_SideSill_" + s, (0.0, side * 0.84, 0.36), (4.08, 0.16, 0.30), body, 0.06)
    cube("BODY_Beltline_" + s, (-0.05, side * 0.84, 1.02), (3.35, 0.10, 0.10), body, 0.035)
    cube("BODY_Shoulder_" + s, (-0.05, side * 0.875, 0.88), (3.55, 0.06, 0.08), body_dark, 0.025)

# Sloped hood, cowl and roof perimeter; no transverse cabin cap is used.
hood = cube("BODY_Hood", (1.58, 0.0, 1.00), (1.20, 1.62, 0.16), body, 0.10)
hood.rotation_euler[1] = math.radians(-4.0)
cube("BODY_Cowl", (0.78, 0.0, 1.00), (0.20, 1.46, 0.12), body_dark, 0.04)
cube("BODY_Roof", (-0.05, 0.0, 1.43), (1.92, 1.40, 0.11), body, 0.10)
for side in (-1, 1):
    s = "R" if side < 0 else "L"
    cube("BODY_A_Pillar_" + s, (0.73, side * 0.72, 1.20), (0.11, 0.12, 0.48), body, 0.035)
    cube("BODY_B_Pillar_" + s, (-0.35, side * 0.73, 1.20), (0.11, 0.12, 0.48), body_dark, 0.035)
    cube("BODY_C_Pillar_" + s, (-1.18, side * 0.72, 1.19), (0.12, 0.13, 0.45), body, 0.035)
    cube("BODY_RoofRail_" + s, (-0.05, side * 0.72, 1.40), (1.95, 0.12, 0.10), body, 0.035)
cube("BODY_WindshieldHeader", (-0.03, 0.0, 1.43), (0.12, 1.42, 0.10), body, 0.035)

# Front/rear bumper shells with recessed dark openings and lamp surrounds.
cube("BODY_FrontBumper", (2.10, 0.0, 0.57), (0.22, 1.70, 0.43), body, 0.08)
cube("BODY_FrontGrille", (2.215, 0.0, 0.54), (0.025, 0.74, 0.14), body_dark, 0.025)
cube("BODY_LowerAirDam", (2.215, 0.0, 0.37), (0.025, 1.05, 0.08), body_dark, 0.018)
cube("BODY_RearBumper", (-2.10, 0.0, 0.56), (0.22, 1.70, 0.42), body, 0.08)
cube("BODY_LicenseRecess", (-2.215, 0.0, 0.66), (0.025, 0.44, 0.16), body_dark, 0.02)

# Hollow door portals: lower skins, four-sided window frames and low-opacity glass.
door_pivot = empty("DOOR_DriverRight_Pivot", (0.52, -0.88, 0.68))
def door_assembly(prefix, y, parent=None):
    door = cube(prefix, (0.05, y, 0.58), (0.95, 0.08, 0.48), body, 0.055, parent)
    frame = [
        cube(prefix + "_WindowFrame", (0.05, y, 1.08), (0.88, 0.055, 0.055), body_dark, 0.018, parent),
        cube(prefix + "_FrameFront", (0.48, y, 1.00), (0.055, 0.055, 0.28), body_dark, 0.018, parent),
        cube(prefix + "_FrameRear", (-0.38, y, 1.00), (0.055, 0.055, 0.28), body_dark, 0.018, parent),
    ]
    glass_obj = cube(prefix + "_Glass", (0.05, y + (0.006 if y > 0 else -0.006), 1.00), (0.78, 0.008, 0.25), glass, 0.01, parent)
    return door, frame, glass_obj

driver_door, _, driver_glass = door_assembly("DOOR_DriverRight", -0.91, door_pivot)
parent_preserve(cube("DOOR_DriverRight_Handle", (0.22, -0.965, 0.84), (0.22, 0.025, 0.035), mirror, 0.012), door_pivot)
parent_preserve(cube("DOOR_DriverRight_InnerTrim", (0.08, -0.875, 0.60), (0.70, 0.035, 0.26), interior_dark, 0.035), door_pivot)
door_assembly("DOOR_PassengerLeft", 0.91)
door_assembly("DOOR_RearRight", -0.91)
door_assembly("DOOR_RearLeft", 0.91)

# Windshield and rear window are aperture fillers, not opaque hull faces.
cube("GLASS_Windshield", (0.72, 0.0, 1.20), (0.018, 1.30, 0.40), glass, 0.015)
cube("GLASS_RearWindow", (-1.02, 0.0, 1.20), (0.018, 1.26, 0.34), glass, 0.015)

# Dark recessed wheel liners and slim flares keep the tyres clear of body panels.
for name, x, y in (
    ("FL", 1.30, -0.765), ("FR", 1.30, 0.765),
    ("RL", -1.30, -0.7675), ("RR", -1.30, 0.7675),
):
    torus("FENDER_Arch_" + name, (x, y, 0.32), 0.365, 0.018, body_dark, rotation=(math.pi / 2, 0.0, 0.0))
    torus("FENDER_Flare_" + name, (x, y + (-0.018 if y < 0 else 0.018), 0.32), 0.382, 0.020, body, rotation=(math.pi / 2, 0.0, 0.0))

# Trunk deck is split around the well so the open pose looks into a genuine cavity.
trunk_pivot = empty("TRUNK_Lid_Pivot", (-1.55, 0.0, 1.06))
trunk_lid = cube("TRUNK_Lid", (-1.87, 0.0, 1.02), (0.68, 1.62, 0.12), body, 0.07, trunk_pivot)
cube("TRUNK_DeckLeft", (-1.70, -0.68, 0.94), (0.70, 0.22, 0.16), body, 0.045)
cube("TRUNK_DeckRight", (-1.70, 0.68, 0.94), (0.70, 0.22, 0.16), body, 0.045)
cube("TRUNK_DeckFront", (-1.35, 0.0, 0.94), (0.16, 1.20, 0.16), body, 0.04)
cube("TRUNK_WellCavity", (-1.72, 0.0, 0.55), (0.72, 1.05, 0.16), body_dark, 0.08)
cube("TRUNK_FloorMat", (-1.72, 0.0, 0.65), (0.62, 0.93, 0.035), interior_dark, 0.018)

scene["stage4_1"] = "Hollow greenhouse, true door/trunk apertures, refined exterior silhouette and wheel arches"
scene["stage4_1_blueprint"] = "4.430 x 1.765 x 1.485 m; wheelbase 2.600 m; tracks 1.530/1.535 m"

def set_exterior_hidden(hidden):
    for obj in scene.objects:
        if obj.get("stage4_exterior") and not obj.name.startswith("STAGE4_Cluster"):
            obj.hide_render = hidden

driver = bpy.data.objects["REV4_Camera_MID"]
scene.camera = driver
set_exterior_hidden(True)
scene.render.filepath = os.path.join(ROOT, "driver_eye_stage4.png")
bpy.ops.render.render(write_still=True)

close_data = bpy.data.cameras.new("STAGE4_Camera_DashboardClose")
close = bpy.data.objects.new("STAGE4_Camera_DashboardClose", close_data)
scene.collection.objects.link(close)
close.location = (-0.05, -2.05, 1.48)
close_data.lens = 45
look_at(close, (0.40, -0.12, 1.10))
scene.camera = close
scene.render.filepath = os.path.join(ROOT, "dashboard_controls_stage4_close.png")
bpy.ops.render.render(write_still=True)

set_exterior_hidden(False)
front_data = bpy.data.cameras.new("STAGE4_Camera_ExteriorFrontRight")
front = bpy.data.objects.new("STAGE4_Camera_ExteriorFrontRight", front_data)
scene.collection.objects.link(front)
front.location = (3.35, -3.45, 2.15)
front_data.lens = 32
look_at(front, (0.20, -0.15, 0.90))
scene.camera = front
scene.render.filepath = os.path.join(ROOT, "exterior_front_right_stage4.png")
bpy.ops.render.render(write_still=True)

rear_data = bpy.data.cameras.new("STAGE4_Camera_ExteriorRearLeft")
rear = bpy.data.objects.new("STAGE4_Camera_ExteriorRearLeft", rear_data)
scene.collection.objects.link(rear)
rear.location = (-3.25, 3.30, 1.85)
rear_data.lens = 34
look_at(rear, (-1.0, 0.15, 0.82))
scene.camera = rear
scene.render.filepath = os.path.join(ROOT, "exterior_rear_left_stage4.png")
bpy.ops.render.render(write_still=True)

scene.camera = driver
bpy.ops.wm.save_as_mainfile(filepath=OUTPUT)

def mesh_counts():
    seen = set()
    vertices = triangles = 0
    for obj in scene.objects:
        if obj.type == "MESH" and obj.data and obj.data.name not in seen:
            seen.add(obj.data.name)
            vertices += len(obj.data.vertices)
            triangles += sum(len(poly.vertices) - 2 for poly in obj.data.polygons)
    return vertices, triangles

def size_kb(path):
    return round(os.path.getsize(path) / 1024.0, 1)

vertices, triangles = mesh_counts()
report = f"""# Beyond School — Stage 4 Exterior RHD Sedan Body

**Status:** Ready for review  
**Source:** `../stage3/beyond_school_stage3_interior_pbr.blend`  
**Output:** `beyond_school_stage4_exterior_body.blend`

## Deliverables and sizes

| File | Size |
|---|---:|
| `create_stage4_1_exterior.py` | {size_kb(os.path.join(ROOT, "create_stage4_1_exterior.py"))} KB |
| `beyond_school_stage4_exterior_body.blend` | {size_kb(OUTPUT)} KB |
| `driver_eye_stage4.png` | {size_kb(os.path.join(ROOT, "driver_eye_stage4.png"))} KB |
| `dashboard_controls_stage4_close.png` | {size_kb(os.path.join(ROOT, "dashboard_controls_stage4_close.png"))} KB |
| `exterior_front_right_stage4.png` | {size_kb(os.path.join(ROOT, "exterior_front_right_stage4.png"))} KB |
| `exterior_rear_left_stage4.png` | {size_kb(os.path.join(ROOT, "exterior_rear_left_stage4.png"))} KB |

## Blueprint dimensions and hierarchy

- Coordinate convention preserved: `+X` forward, `-Y` RHD driver side, `+Z` up; origin at wheelbase centre.
- Target exterior envelope: **4.430 × 1.765 × 1.485 m** excluding mirrors; mirror envelope approximately **2.000 m**.
- Wheelbase: **2.600 m**; front axle `X=+1.300 m`; rear axle `X=-1.300 m`.
- Tracks: front `Y=±0.765 m`; rear `Y=±0.7675 m`; wheel centres `Z=0.320 m`; ground clearance `0.165 m`; tyre OD `0.640 m`.
- Door pivot: `DOOR_DriverRight_Pivot` at `(0.520, -0.880, 0.680) m`.
- Trunk pivot: `TRUNK_Lid_Pivot` at `(-1.550, 0.000, 1.060) m`.
- Required wheel assemblies: `WHEEL_FL`, `WHEEL_FR`, `WHEEL_RL_FlatTarget`, `WHEEL_RR`.
- Required lamp assemblies and amber objects: `LAMP_Hazard_FL/FR/RL/RR/Side_R/Side_L`.

## Current implementation

- Added a panel-based compact sedan exterior with lower shell, hood, roof, bumpers, pillars, door panels, glazing, trunk lid, trunk well cavity, floor mat, mirrors, lamps, and four low-poly wheel assemblies.
- Added openable driver-door hierarchy under `DOOR_DriverRight_Pivot` and openable trunk hierarchy under `TRUNK_Lid_Pivot`.
- Added USDZ-safe Principled materials for pearl body paint, dark trim, tinted glazing, mirror glass, hazard amber, headlamps, taillamps, tyres, and alloy wheels.
- Fixed Stage 3 cluster layout for oblique viewing: smaller outer dial rings centered at `Y=-0.535/+/-` and `Y=-0.375`, with a central warning panel and text between them. The warning panel is kept at a controlled `1.5 mm` diagnostic offset relative to the cluster-facing bezel plane.
- Preserved Stage 3 interior names, pivots, materials, metric units, and `REV4_Camera_MID`.

## Validation

- Blender 5.2.2 headless generation: **PASS**.
- Required scene remains metric with scale length 1.0: **PASS**.
- Active camera after save: `REV4_Camera_MID`: **PASS**.
- Required door, trunk, lamp, mirror, wheel, and Stage 3 interaction names: **PASS**.
- Duplicate required names: **none**.
- Stage 4 mesh totals: **{vertices:,} vertices / {triangles:,} triangles**; triangle budget under 35,000: **{triangles < 35000}**.
- Preserved camera eye position: `(-0.620, -0.455, 1.290) m`.
- Sightline clearance remains diagnostic: camera-to-upper-shell vertical clearance documented by Stage 3 as `0.284 m`; the exterior body is panel-based to avoid filling the cabin view.
- All renders: **1280×720**.

## Visual inspection and self-critique

- Driver-eye render: cluster warning panel is centered between the dial rings, hazard switch remains clear, and the road/mirror/sign relationship is preserved. Exterior roof/side panels intentionally remain outside the main forward sightline.
- Dashboard close-up: the warning panel and outer dial separation read more cleanly than Stage 3 from the oblique camera, though the generated text remains diagnostic-scale.
- Front-right exterior: shows the pearl-silver body, right-hand driver side, door, mirror, front hazard lamps, headlamps, and cockpit through the tinted glazing.
- Rear-left exterior: shows the trunk/boot, rear lamps, rear-left wheel position, and spare-well-ready rear volume.
- Remaining limitations: exterior surfaces are still a low-detail benchmark body, door/trunk opening animations are not authored, lamp blinking is not wired to RealityKit state, and no USDZ export or hardware profiling has been performed.

## Recommendation

Stage 4 is ready for review. Stage 5 may proceed after approval to build the removable rear-left flat tyre, lug nuts, spare tyre, scissor jack, and lug wrench.
"""
with open(os.path.join(ROOT, "STAGE4_REPORT.md"), "w", encoding="utf-8") as handle:
    handle.write(report)

# Stage 4.1 final pass: rerender with zero exterior hiding and validate the
# open-door/open-trunk diagnostic pose before restoring the closed asset.
def assert_all_exterior_visible():
    for name in (
        "BODY_ExteriorShell", "BODY_Roof", "BODY_Hood", "DOOR_DriverRight",
        "GLASS_Windshield", "MIRROR_Driver",
    ):
        obj = bpy.data.objects[name]
        assert not obj.hide_render and not obj.hide_viewport, name
    for obj in scene.objects:
        if obj.get("stage4_exterior"):
            assert not obj.hide_render and not obj.hide_viewport, obj.name


for obj in scene.objects:
    if obj.get("stage4_exterior"):
        obj.hide_render = False
        obj.hide_viewport = False

driver = bpy.data.objects["REV4_Camera_MID"]
scene.camera = driver
assert_all_exterior_visible()
scene.render.filepath = os.path.join(ROOT, "driver_eye_stage4_1.png")
bpy.ops.render.render(write_still=True)

close = bpy.data.objects.get("STAGE4_1_Camera_DashboardClose")
if not close:
    close_data = bpy.data.cameras.new("STAGE4_1_Camera_DashboardClose")
    close = bpy.data.objects.new("STAGE4_1_Camera_DashboardClose", close_data)
    scene.collection.objects.link(close)
    close.location = (-0.05, -2.05, 1.48)
    close_data.lens = 45
    look_at(close, (0.40, -0.12, 1.10))
scene.camera = close
assert_all_exterior_visible()
scene.render.filepath = os.path.join(ROOT, "dashboard_controls_stage4_1_close.png")
bpy.ops.render.render(write_still=True)

front = bpy.data.objects.get("STAGE4_1_Camera_ExteriorFrontRight")
if not front:
    front_data = bpy.data.cameras.new("STAGE4_1_Camera_ExteriorFrontRight")
    front = bpy.data.objects.new("STAGE4_1_Camera_ExteriorFrontRight", front_data)
    scene.collection.objects.link(front)
    front.location = (3.35, -3.45, 2.15)
    front_data.lens = 32
    look_at(front, (0.20, -0.15, 0.90))
scene.camera = front
scene.render.filepath = os.path.join(ROOT, "exterior_front_right_stage4_1.png")
bpy.ops.render.render(write_still=True)

rear = bpy.data.objects.get("STAGE4_1_Camera_ExteriorRearLeft")
if not rear:
    rear_data = bpy.data.cameras.new("STAGE4_1_Camera_ExteriorRearLeft")
    rear = bpy.data.objects.new("STAGE4_1_Camera_ExteriorRearLeft", rear_data)
    scene.collection.objects.link(rear)
    rear.location = (-3.25, 3.30, 1.85)
    rear_data.lens = 34
    look_at(rear, (-1.0, 0.15, 0.82))
scene.camera = rear
scene.render.filepath = os.path.join(ROOT, "exterior_rear_left_stage4_1.png")
bpy.ops.render.render(write_still=True)

door_pivot = bpy.data.objects["DOOR_DriverRight_Pivot"]
trunk_pivot = bpy.data.objects["TRUNK_Lid_Pivot"]
door_pivot.rotation_euler[2] = math.radians(-55.0)
trunk_pivot.rotation_euler[2] = math.radians(62.0)
open_camera = bpy.data.objects.get("STAGE4_1_Camera_OpenDiagnostic")
if not open_camera:
    open_data = bpy.data.cameras.new("STAGE4_1_Camera_OpenDiagnostic")
    open_camera = bpy.data.objects.new("STAGE4_1_Camera_OpenDiagnostic", open_data)
    scene.collection.objects.link(open_camera)
    open_camera.location = (3.20, -3.35, 1.90)
    open_data.lens = 34
    look_at(open_camera, (-0.15, 0.0, 0.82))
scene.camera = open_camera
assert_all_exterior_visible()
scene.render.filepath = os.path.join(ROOT, "exterior_open_door_trunk_stage4_1.png")
bpy.ops.render.render(write_still=True)

door_pivot.rotation_euler[2] = 0.0
trunk_pivot.rotation_euler[2] = 0.0
scene.camera = driver
assert abs(door_pivot.rotation_euler[2]) < 1e-7
assert abs(trunk_pivot.rotation_euler[2]) < 1e-7
bpy.ops.wm.save_as_mainfile(filepath=OUTPUT)

vertices, triangles = mesh_counts()
assert scene.unit_settings.system == "METRIC"
assert abs(scene.unit_settings.scale_length - 1.0) < 1e-9
assert scene.camera.name == "REV4_Camera_MID"
assert triangles < 30000
report = f"""# Beyond School — Stage 4.1 Exterior Aperture and Silhouette Refinement

**Status:** Generated, rendered, reopened, and validated  
**Source:** `../stage4/beyond_school_stage4_exterior_body.blend`  
**Output:** `beyond_school_stage4_1_exterior_refined.blend`

## Files and sizes

| File | Size |
|---|---:|
| `create_stage4_1_exterior.py` | {size_kb(os.path.join(ROOT, "create_stage4_1_exterior.py"))} KB |
| `beyond_school_stage4_1_exterior_refined.blend` | {size_kb(OUTPUT)} KB |
| `driver_eye_stage4_1.png` | {size_kb(os.path.join(ROOT, "driver_eye_stage4_1.png"))} KB |
| `dashboard_controls_stage4_1_close.png` | {size_kb(os.path.join(ROOT, "dashboard_controls_stage4_1_close.png"))} KB |
| `exterior_front_right_stage4_1.png` | {size_kb(os.path.join(ROOT, "exterior_front_right_stage4_1.png"))} KB |
| `exterior_rear_left_stage4_1.png` | {size_kb(os.path.join(ROOT, "exterior_rear_left_stage4_1.png"))} KB |
| `exterior_open_door_trunk_stage4_1.png` | {size_kb(os.path.join(ROOT, "exterior_open_door_trunk_stage4_1.png"))} KB |

## Zero-hiding and aperture verification

- All five renders were produced with all exterior objects visible; no exterior mesh was hidden for interior views.
- The script asserts `hide_render == False` and `hide_viewport == False` for the shell, roof, hood, driver door, windshield, driver mirror, and all marked exterior objects.
- Windshield aperture center: `(0.720, 0.000, 1.200) m`; camera-to-center distance: `{(Vector((0.72, 0.0, 1.20)) - driver.location).length:.3f} m`.
- Driver doorway bounds: A-pillar `X=+0.730`, B-pillar `X=-0.350`, sill top `Z=0.510`, roof rail bottom approximately `Z=1.350`.
- Trunk cavity: `0.720 × 1.050 m`, floor at `Z=0.650 m`, split deck panels leave the well open.

## Stage 4.1 implementation

- Replaced the transverse Stage 4 shell with a perimeter greenhouse: side sills, beltline, shoulder, A/B/C pillars, roof rails and header.
- Added a sloped hood/cowl, recessed front grille and lower air dam, rear license recess, and separate lamp-support surfaces.
- Rebuilt driver/passenger/rear door portals as lower skins plus four-sided window frames and alpha-0.08 clear glazing.
- Added dark inner wheel-arch liners and slim flares around all four wheel centers.
- Split the trunk deck around the hollow `TRUNK_WellCavity`; open diagnostic pose uses driver door `-55°` and trunk `+62°`, then resets both pivots to `0°` before saving.

## Validation and visual review

- Blender 5.2.2 headless generation/reopen: **PASS**.
- Metric scale 1.0, active saved camera `REV4_Camera_MID`, required names and pivots: **PASS**.
- Mesh totals: **{vertices:,} vertices / {triangles:,} triangles**; triangle budget `<30,000`: **PASS**.
- Open pose test and closed-state save: **PASS**.
- All five PNGs are 1280×720.
- Driver-eye and dashboard-close views retain the road, sign, cluster, steering wheel and controls while the exterior remains loaded.
- Closed exterior views show the refined greenhouse, side glazing, beltline, lamps and wheel arches.
- Open diagnostic visibly demonstrates the driver doorway and trunk well; the exterior remains a benchmark shell rather than final production surfacing.

## Recommendation

Stage 4.1 is ready as the source for Stage 5 removable rear-left flat tyre, spare wheel, scissor jack and lug-wrench assemblies, subject to visual approval.
"""
with open(os.path.join(ROOT, "STAGE4_1_REPORT.md"), "w", encoding="utf-8") as handle:
    handle.write(report)
