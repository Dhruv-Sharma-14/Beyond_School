import bpy
import math
import os
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
BLEND_PATH = os.path.join(ROOT, "beyond_school_cockpit_blockout.blend")
RENDER_PATH = os.path.join(ROOT, "driver_eye_blockout.png")

bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, color, roughness=0.5, metallic=0.0, emission=None):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 2.0
    return m

MATS = {
    "dash": mat("MAT_Dashboard_SoftTouch", (0.055, 0.065, 0.075), 0.72),
    "dash_edge": mat("MAT_Dashboard_Edge", (0.13, 0.15, 0.16), 0.48),
    "seat": mat("MAT_Seat_Fabric", (0.18, 0.20, 0.22), 0.9),
    "seat_edge": mat("MAT_Seat_Bolster", (0.08, 0.09, 0.10), 0.82),
    "rubber": mat("MAT_Steering_Rubber", (0.025, 0.028, 0.03), 0.86),
    "glass": mat("MAT_Windshield_Temporary", (0.18, 0.34, 0.43), 0.18),
    "mirror": mat("MAT_Mirror_Glass", (0.08, 0.14, 0.17), 0.12, 0.25),
    "metal": mat("MAT_Satin_Metal", (0.32, 0.35, 0.36), 0.32, 0.7),
    "screen": mat("MAT_Cluster_Screen", (0.015, 0.04, 0.055), 0.24, 0.1, (0.02, 0.12, 0.16)),
    "hazard": mat("MAT_Hazard_Red", (0.5, 0.015, 0.01), 0.42, 0.0, (0.3, 0.0, 0.0)),
    "road": mat("MAT_Temporary_Road", (0.12, 0.13, 0.12), 0.95),
    "marking": mat("MAT_Road_Marking", (0.8, 0.72, 0.46), 0.65),
    "sky": mat("MAT_Horizon", (0.28, 0.52, 0.78), 0.9),
}

def assign(obj, material):
    obj.data.materials.append(material)
    return obj

def cube(name, loc, scale, material, bevel=0.0, parent=None):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = (scale[0] / 2, scale[1] / 2, scale[2] / 2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(o, material)
    if bevel:
        mod = o.modifiers.new("Blockout_Rounded_Edges", "BEVEL")
        mod.width = bevel
        mod.segments = 3
    if parent:
        o.parent = parent
        o.matrix_parent_inverse = parent.matrix_world.inverted()
    return o

def cyl(name, loc, radius, depth, material, rotation=(0, 0, 0), parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth, location=loc, rotation=rotation)
    o = bpy.context.object
    o.name = name
    assign(o, material)
    if parent:
        o.parent = parent
        o.matrix_parent_inverse = parent.matrix_world.inverted()
    return o

def sphere(name, loc, scale, material, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(o, material)
    if parent:
        o.parent = parent
        o.matrix_parent_inverse = parent.matrix_world.inverted()
    return o

def torus(name, loc, major, minor, material, rotation=(0, 0, 0), parent=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, major_segments=48, minor_segments=12, location=loc, rotation=rotation)
    o = bpy.context.object
    o.name = name
    assign(o, material)
    if parent:
        o.parent = parent
        o.matrix_parent_inverse = parent.matrix_world.inverted()
    return o

def empty(name, loc, parent=None):
    o = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(o)
    o.location = loc
    if parent:
        o.parent = parent
        o.matrix_parent_inverse = parent.matrix_world.inverted()
    return o

def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()

def collection(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c

def move_to(obj, c):
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    c.objects.link(obj)

scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1.0
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = RENDER_PATH
scene.render.film_transparent = False
scene.world = bpy.data.worlds.new("World_Daylight")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.08, 0.14, 0.22, 1.0)
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.35

root = empty("VEHICLE_ROOT", (0, 0, 0))
root["coordinate_convention"] = "+X forward, -X rearward, -Y driver, +Y passenger, +Z up"
root["design_status"] = "Stage 1 temporary cockpit blockout"

groups = {n: collection(n) for n in [
    "COCKPIT_BLOCKOUT", "DASHBOARD", "SEATS", "STEERING", "GLASS_MIRRORS",
    "INTERACTION_MARKERS", "ROAD_HORIZON", "LIGHTING"
]}

floor = cube("CABIN_Floor", (-0.10, 0, 0.18), (2.65, 1.52, 0.12), MATS["dash"], 0.04, root)
tunnel = cube("CABIN_TransmissionTunnel", (-0.05, 0.10, 0.31), (1.72, 0.30, 0.27), MATS["dash_edge"], 0.06, root)
dash = cube("DASH_Shell", (0.78, 0, 1.01), (0.52, 1.68, 0.25), MATS["dash"], 0.08, root)
dash_top = cube("DASH_UpperPad", (0.54, 0, 1.18), (0.72, 1.66, 0.12), MATS["dash"], 0.05, root)
dash["design_note"] = "Original unbranded dashboard mass; final surfacing deferred"

for y, label in [(-0.43, "Driver"), (0.43, "Passenger")]:
    seat = empty("SEAT_" + label, (-0.48, y, 0.0), root)
    cube("SEAT_%s_Cushion" % label, (-0.42, y, 0.67), (0.78, 0.47, 0.22), MATS["seat"], 0.10, seat)
    back = cube("SEAT_%s_Backrest" % label, (-0.72, y, 1.02), (0.23, 0.47, 0.76), MATS["seat"], 0.10, seat)
    back.rotation_euler[1] = math.radians(-10)
    cube("SEAT_%s_Headrest" % label, (-0.83, y, 1.47), (0.18, 0.34, 0.22), MATS["seat_edge"], 0.06, seat)
    cube("SEAT_%s_Bolster_Outer" % label, (-0.40, y + (-0.19 if y < 0 else 0.19), 0.83), (0.62, 0.08, 0.30), MATS["seat_edge"], 0.04, seat)

steering_root = empty("STEERING_ROOT", (0.42, -0.455, 1.04), root)
column = cyl("STEERING_Column", (0.42, -0.455, 1.10), 0.055, 0.38, MATS["rubber"], rotation=(0, math.radians(90), 0), parent=steering_root)
wheel = torus("STEERING_Wheel", (0.42, -0.455, 1.18), 0.185, 0.032, MATS["rubber"], rotation=(0, math.radians(90), 0), parent=steering_root)
hub = cyl("STEERING_Hub", (0.42, -0.455, 1.18), 0.075, 0.055, MATS["metal"], rotation=(0, math.radians(90), 0), parent=steering_root)
steering_root["interactive"] = True

binnacle = cube("DASH_InstrumentBinnacle", (0.55, -0.455, 1.31), (0.23, 0.43, 0.17), MATS["dash_edge"], 0.035, root)
cluster = cube("DASH_InstrumentCluster", (0.43, -0.455, 1.305), (0.035, 0.30, 0.105), MATS["screen"], 0.012, root)
cluster["display_placeholder"] = "Temporary blockout display; final graphics deferred"

stack = cube("CONSOLE_CentreStack", (0.67, 0.0, 1.05), (0.28, 0.48, 0.44), MATS["dash_edge"], 0.05, root)
screen = cube("CONSOLE_InfotainmentScreen", (0.54, 0.0, 1.26), (0.035, 0.34, 0.18), MATS["screen"], 0.01, root)
hazard = cube("BTN_HazardSwitch", (0.48, -0.005, 1.235), (0.06, 0.12, 0.06), MATS["hazard"], 0.012, root)
hazard["interactive"] = True
hazard["function"] = "Hazard light toggle"
hazard_icon = cube("BTN_HazardSwitch_Icon", (0.515, -0.005, 1.235), (0.006, 0.05, 0.025), MATS["screen"], 0.002, hazard)
gear = cube("CONSOLE_GearSelector", (0.22, 0.10, 0.48), (0.16, 0.18, 0.18), MATS["metal"], 0.04, root)

for side, y in [("Left", 0.0), ("Right", -1.0)]:
    pass
for side, y in [("Driver", -0.92), ("Passenger", 0.92)]:
    mirror = empty("MIRROR_" + side, (0.62, y, 1.19), root)
    cube("MIRROR_%s_Housing" % side, (0.62, y, 1.19), (0.22, 0.12, 0.12), MATS["dash_edge"], 0.035, mirror)
    cube("MIRROR_%s_Glass" % side, (0.63, y + (0.065 if y > 0 else -0.065), 1.19), (0.025, 0.095, 0.075), MATS["mirror"], 0.012, mirror)
    mirror["adjustable"] = True

windshield = empty("GLASS_WindshieldOpening", (1.08, 0, 1.44), root)
windshield["blockout_note"] = "Opening only at Stage 1; final laminated glass deferred"
for y, name in [(-0.78, "A_Pillar_Driver"), (0.78, "A_Pillar_Passenger")]:
    cube(name, (0.93, y, 1.48), (0.18, 0.16, 1.12), MATS["dash_edge"], 0.035, root)
roof = cube("CABIN_Roof_Header", (0.52, 0, 1.96), (0.85, 1.64, 0.16), MATS["dash_edge"], 0.05, root)

eye = empty("MARKER_DriverEye", (-0.35, -0.455, 1.285))
eye["purpose"] = "Primary seated driver's-eye composition reference"
eye["forward_axis"] = "+X"
hazard_marker = empty("MARKER_HazardSwitch", (0.45, -0.01, 1.29))
mirror_marker = empty("MARKER_Mirror_Driver", (0.64, -0.92, 1.23))
mirror_marker["purpose"] = "Driver-side mirror sightline target"
for m in [eye, hazard_marker, mirror_marker]:
    m.parent = root

road = cube("ROAD_HorizonPlane", (7.0, 0, -0.03), (14.0, 18.0, 0.06), MATS["road"], 0.0)
road_mark = cube("ROAD_CentreMarking", (7.0, 0, 0.005), (14.0, 0.06, 0.01), MATS["marking"], 0.0)
horizon = cube("ROAD_HorizonBackdrop", (11.0, 0, 3.0), (0.10, 20.0, 6.0), MATS["sky"], 0.0)

cam_data = bpy.data.cameras.new("CAM_DriverEye")
camera = bpy.data.objects.new("CAM_DriverEye", cam_data)
scene.collection.objects.link(camera)
camera.location = eye.location.copy()
camera.data.lens = 24
camera.data.sensor_width = 36
look_at(camera, (2.6, -0.25, 1.18))
camera["reference_marker"] = "MARKER_DriverEye"
scene.camera = camera

bpy.ops.object.light_add(type="AREA", location=(0.4, -1.8, 3.2))
key = bpy.context.object
key.name = "LIGHT_Daylight_Key"
key.data.energy = 850
key.data.shape = "RECTANGLE"
key.data.size = 4.0
look_at(key, (0.8, 0, 0.8))
bpy.ops.object.light_add(type="AREA", location=(1.8, 1.5, 2.2))
fill = bpy.context.object
fill.name = "LIGHT_Daylight_Fill"
fill.data.energy = 450
fill.data.size = 3.0
look_at(fill, (0.8, 0, 1.0))

scene["stage"] = "Milestone 00C.1 Stage 1 cockpit blockout"
scene["dimensions_m"] = "4.430 length x 1.765 body width x 1.485 height target"
scene["driver_eye_m"] = "-0.350, -0.455, 1.285 (adjusted rearward from initial blueprint target for seated composition)"
scene["quality_status"] = "Temporary proportion and composition blockout; not final photorealistic asset"

bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
scene.render.filepath = RENDER_PATH
bpy.ops.render.render(write_still=True)
