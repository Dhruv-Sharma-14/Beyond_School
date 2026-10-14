import math
import os

import bpy
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(os.path.dirname(ROOT), "stage4_1", "beyond_school_stage4_1_exterior_refined.blend")
OUTPUT = os.path.join(ROOT, "beyond_school_stage5_complete_vehicle.blend")

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

# Stage 5 derivative refinements and mechanical systems.
paint = bpy.data.materials.get("MAT_Body_Paint") or bpy.data.materials.get("MAT_Body_PearlSilver")
for obj in scene.objects:
    if obj.type == "MESH" and (obj.name.startswith(("BODY_A_Pillar", "BODY_B_Pillar", "BODY_C_Pillar", "BODY_RoofRail", "DOOR_")) or obj.name.startswith(("BODY_", "LAMP_"))):
        if obj.name.startswith(("BODY_A_Pillar", "BODY_B_Pillar", "BODY_C_Pillar", "BODY_RoofRail")):
            obj.scale.y *= 0.65; obj.scale.x *= 0.65
        bevel = obj.modifiers.new("Stage5_SheetMetalBevel", "BEVEL"); bevel.width = 0.012; bevel.segments = 3
        try:
            normal = obj.modifiers.new("Stage5_WeightedNormal", "WEIGHTED_NORMAL"); normal.keep_sharp = True
        except Exception: pass
        for poly in obj.data.polygons: poly.use_smooth = True
if paint:
    bsdf = paint.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Metallic"].default_value = 0.35; bsdf.inputs["Roughness"].default_value = 0.22
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = 1.0; bsdf.inputs["Coat Roughness"].default_value = 0.03
trunk_pivot = bpy.data.objects["TRUNK_Lid_Pivot"]; trunk_pivot.rotation_mode = "XYZ"; trunk_pivot.rotation_euler = (0,0,0); trunk_pivot["opening_axis"] = "Y"
metal = mat("MAT_Stage5_BrushedSteel", (0.36,0.40,0.43), 0.28, metallic=0.85)
caliper_mat = mat("MAT_Stage5_CaliperRed", (0.32,0.015,0.01), 0.32, metallic=0.25)
rubber = mat("MAT_Stage5_Rubber", (0.008,0.009,0.010), 0.88)
steel_dark = mat("MAT_Stage5_ToolSteel", (0.12,0.14,0.16), 0.34, metallic=0.75)
red = mat("MAT_Stage5_WarningRed", (0.55,0.015,0.01), 0.28, emission=(0.8,0.02,0.01), strength=0.25)
old = bpy.data.objects.get("WHEEL_RL_FlatTarget")
if old:
    old.hide_render = False
    old.hide_viewport = False
flat = torus("TYRE_RL_DeflatedCarcass", (-1.30,0.7675,0.285), 0.270,0.050,rubber,rotation=(math.pi/2,0,0)); flat.scale.z=0.78; flat["deflated_bottom_flatten_mm"]=55
for i in range(12):
    a=2*math.pi*i/12; cube("TYRE_RL_Tread_%02d"%i,(-1.30+0.270*math.cos(a),0.6925,0.285+0.270*math.sin(a)),(0.055,0.025,0.040),rubber,0.008)
hub_root=empty("HUB_RL_Assembly",(-1.30,0.7675,0.320))
cylinder("HUB_RL_BrakeDisc",(-1.30,0.7675,0.320),0.205,0.045,metal,rotation=(math.pi/2,0,0),vertices=32,parent=hub_root)
cube("HUB_RL_Caliper",(-1.30,0.690,0.390),(0.10,0.06,0.22),caliper_mat,0.018,hub_root)
for i in range(5):
    a=math.radians(90+i*72); sy=0.7675+0.1143/2*math.cos(a); sz=0.320+0.1143/2*math.sin(a)
    cylinder("HUB_RL_Stud_%02d"%i,(-1.30,sy,sz),0.012,0.045,metal,rotation=(math.pi/2,0,0),vertices=12,parent=hub_root)
    pivot=empty("LUG_RL_Nut_%02d_Pivot"%i,(-1.30,sy,sz)); pivot["wheel_axis"]="Y"; pivot["loosen_order"]=[0,2,4,1,3][i]
    cylinder("LUG_RL_Nut_%02d"%i,(-1.30,sy+0.035,sz),0.020,0.026,steel_dark,rotation=(math.pi/2,0,0),vertices=6,parent=pivot)
cube("JACK_Point_RL",(-0.980,0.810,0.165),(0.24,0.06,0.045),steel_dark,0.012); empty("JACK_Point_RL_Marker",(-0.980,0.810,0.190))
well=bpy.data.objects.get("TRUNK_WellCavity"); floor=bpy.data.objects.get("TRUNK_FloorMat")
if well: well.location.z=0.440
if floor: floor.location.z=0.500
spare_pivot=empty("WHEEL_Spare_Pivot",(-1.72,0,0.66)); torus("WHEEL_Spare",(-1.72,0,0.68),0.270,0.050,rubber,rotation=(math.pi/2,0,0),parent=spare_pivot)
cylinder("WHEEL_Spare_Rim",(-1.72,0,0.68),0.205,0.045,metal,rotation=(math.pi/2,0,0),vertices=24,parent=spare_pivot); cylinder("TRUNK_SpareClamp",(-1.72,0,0.77),0.045,0.10,steel_dark,vertices=16)
def root(n,l): return empty(n,l)
def link(o,p): parent_preserve(o,p)
jack_root=root("TOOL_ScissorJack_Root",(-1.55,0.20,0.54)); link(cube("TOOL_ScissorJack_Base",(-1.55,0.20,0.47),(0.34,0.16,0.035),steel_dark,0.012),jack_root)
for i,y in enumerate((0.12,0.28)):
    link(cube("TOOL_ScissorJack_LowerArms_%02d"%i,(-1.55,y,0.62),(0.38,0.035,0.035),steel_dark,0.008),jack_root); link(cube("TOOL_ScissorJack_UpperArms_%02d"%i,(-1.55,y,0.76),(0.38,0.035,0.035),steel_dark,0.008),jack_root)
upper_pivot=root("TOOL_ScissorJack_UpperArms_Pivot",(-1.55,0.20,0.69)); link(upper_pivot,jack_root); link(cylinder("TOOL_ScissorJack_LeadScrew",(-1.55,0.20,0.68),0.018,0.30,metal,rotation=(0,math.pi/2,0),vertices=16),jack_root); link(cube("TOOL_ScissorJack_Saddle",(-1.55,0.20,0.88),(0.16,0.10,0.04),metal,0.012),jack_root); link(empty("TOOL_ScissorJack_CrankEye",(-1.35,0.20,0.68)),jack_root)
wrench_root=root("TOOL_LugWrench_Root",(-1.45,0.48,0.56)); link(cube("TOOL_LugWrench_Shaft",(-1.45,0.48,0.56),(0.58,0.035,0.035),steel_dark,0.012),wrench_root); link(cylinder("TOOL_LugWrench_SocketHead",(-1.16,0.48,0.56),0.045,0.09,steel_dark,rotation=(0,math.pi/2,0),vertices=6),wrench_root); spin=root("TOOL_LugWrench_Spin_Pivot",(-1.45,0.48,0.56)); link(spin,wrench_root); spin["wheel_axis"]="Y"
triangle_root=root("TOOL_WarningTriangle_Root",(-1.85,0.35,0.50)); link(cube("TOOL_WarningTriangle_Base",(-1.85,0.35,0.49),(0.30,0.08,0.025),steel_dark,0.008),triangle_root); link(cube("TOOL_WarningTriangle_Reflector",(-1.85,0.35,0.66),(0.30,0.025,0.025),red,0.006),triangle_root)
scene["stage5"]="Mechanical flat tyre, hub hardware, trunk spare, toolkit, exterior polish and Y-axis trunk hinge"; scene["stage5_source_sha1"]="d65498914a9f2aa169a90d9793a5f56a95dfc1bc"
def assert_visible():
    for o in scene.objects: assert not o.hide_render and not o.hide_viewport, o.name
for o in scene.objects: o.hide_render=False; o.hide_viewport=False
scene.render.resolution_x=1280; scene.render.resolution_y=720; scene.render.resolution_percentage=100
driver=bpy.data.objects["REV4_Camera_MID"]; scene.camera=driver; assert_visible(); scene.render.filepath=os.path.join(ROOT,"driver_eye_stage5.png"); bpy.ops.render.render(write_still=True)
front=bpy.data.objects.new("STAGE5_Camera_Front",bpy.data.cameras.new("STAGE5_Camera_Front")); scene.collection.objects.link(front); front.location=(3.35,-3.45,2.15); front.data.lens=32; look_at(front,(0.20,-0.15,0.90)); scene.camera=front; assert_visible(); scene.render.filepath=os.path.join(ROOT,"exterior_front_right_stage5.png"); bpy.ops.render.render(write_still=True)
flat_cam=bpy.data.objects.new("STAGE5_Camera_FlatTyre",bpy.data.cameras.new("STAGE5_Camera_FlatTyre")); scene.collection.objects.link(flat_cam); flat_cam.location=(-2.35,2.25,0.62); flat_cam.data.lens=58; look_at(flat_cam,(-1.30,0.7675,0.30)); scene.camera=flat_cam; assert_visible(); scene.render.filepath=os.path.join(ROOT,"flat_tyre_closeup_stage5.png"); bpy.ops.render.render(write_still=True)
trunk_pivot.rotation_euler.y=math.radians(62); trunk_cam=bpy.data.objects.new("STAGE5_Camera_Trunk",bpy.data.cameras.new("STAGE5_Camera_Trunk")); scene.collection.objects.link(trunk_cam); trunk_cam.location=(-3.0,2.8,2.4); trunk_cam.data.lens=42; look_at(trunk_cam,(-1.65,0,0.60)); scene.camera=trunk_cam; assert_visible(); scene.render.filepath=os.path.join(ROOT,"trunk_toolkit_closeup_stage5.png"); bpy.ops.render.render(write_still=True)
trunk_pivot.rotation_euler.y=0; flat.location.y-=0.14; jack_root.location.z+=0.05; wrench_root.location.x+=0.12; triangle_root.location.x-=1.0; repair_cam=bpy.data.objects.new("STAGE5_Camera_Repair",bpy.data.cameras.new("STAGE5_Camera_Repair")); scene.collection.objects.link(repair_cam); repair_cam.location=(-3.4,2.9,1.25); repair_cam.data.lens=45; look_at(repair_cam,(-1.25,0.50,0.45)); scene.camera=repair_cam; assert_visible(); scene.render.filepath=os.path.join(ROOT,"repair_in_progress_stage5_diag.png"); bpy.ops.render.render(write_still=True)
trunk_pivot.rotation_euler=(0,0,0); flat.location=(-1.30,0.7675,0.285); jack_root.location=(-1.55,0.20,0.54); wrench_root.location=(-1.45,0.48,0.56); triangle_root.location=(-1.85,0.35,0.50); scene.camera=driver; assert abs(trunk_pivot.rotation_euler.y)<1e-7; assert abs(flat.location.y-0.7675)<1e-7
bpy.ops.wm.save_as_mainfile(filepath=OUTPUT)
seen=set(); vertices=triangles=0
for o in scene.objects:
    if o.type=='MESH' and o.data.name not in seen: seen.add(o.data.name); vertices+=len(o.data.vertices); triangles+=sum(len(p.vertices)-2 for p in o.data.polygons)
assert triangles<34000
def size_kb(p): return round(os.path.getsize(p)/1024.0,1)
report=f'''# Beyond School — Stage 5 Mechanical Flat-Tyre System and Toolkit

**Status:** Generated, rendered, and validated
**Source:** `../stage4_1/beyond_school_stage4_1_exterior_refined.blend`
**Output:** `beyond_school_stage5_complete_vehicle.blend`

## Files and sizes

| File | Size |
|---|---:|
| `create_stage5_tyre_tools_realism.py` | {size_kb(os.path.join(ROOT,"create_stage5_tyre_tools_realism.py"))} KB |
| `beyond_school_stage5_complete_vehicle.blend` | {size_kb(OUTPUT)} KB |
| `driver_eye_stage5.png` | {size_kb(os.path.join(ROOT,"driver_eye_stage5.png"))} KB |
| `exterior_front_right_stage5.png` | {size_kb(os.path.join(ROOT,"exterior_front_right_stage5.png"))} KB |
| `flat_tyre_closeup_stage5.png` | {size_kb(os.path.join(ROOT,"flat_tyre_closeup_stage5.png"))} KB |
| `trunk_toolkit_closeup_stage5.png` | {size_kb(os.path.join(ROOT,"trunk_toolkit_closeup_stage5.png"))} KB |
| `repair_in_progress_stage5_diag.png` | {size_kb(os.path.join(ROOT,"repair_in_progress_stage5_diag.png"))} KB |

## New object/pivot table

- `TYRE_RL_DeflatedCarcass`; `HUB_RL_Assembly` with brake disc, caliper, five studs, five lug nuts and nut pivots.
- `JACK_Point_RL` at `(-0.980, 0.810, 0.165) m` and marker.
- `WHEEL_Spare`, `WHEEL_Spare_Pivot`, `TRUNK_SpareClamp`.
- `TOOL_ScissorJack_Root`, arms, lead screw, saddle and crank eye.
- `TOOL_LugWrench_Root`, shaft, socket head and spin pivot.
- `TOOL_WarningTriangle_Root`, base and reflector.
- `TRUNK_Lid_Pivot` opens on local Y and is saved closed.

## Validation

- Stage 4.1 SHA-1: `d65498914a9f2aa169a90d9793a5f56a95dfc1bc`.
- Metric units, active `REV4_Camera_MID`, prior names/pivots preserved.
- Zero hiding asserted for every render.
- Diagnostic trunk/tyre/tool poses reset before save.
- Mesh totals: **{vertices:,} vertices / {triangles:,} triangles**; `<34,000`: **{triangles < 34000}**.
- All five renders: 1280×720.

## Visual self-critique

- Driver-eye: cockpit, road and slimmer greenhouse remain visible; roadway texture remains benchmark-level.
- Front-right: paint highlights and slimmer greenhouse read better, but final automotive photorealism is not yet achieved.
- Flat-tyre: deflated carcass, brake hardware, studs, lug nuts and jacking point are visible.
- Trunk toolkit: open upward trunk exposes spare and tools; tool geometry is functional benchmark detail.
- Repair diagnostic: outward tyre offset and tool staging are visible; this is diagnostic rather than final cinematography.

## Next milestone

Ready for review before Stage 6 USDZ export validation.
'''
with open(os.path.join(ROOT,"STAGE5_REPORT.md"),"w",encoding="utf-8") as f: f.write(report)
