import math
import os

import bpy
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(
    os.path.dirname(ROOT),
    "revision3",
    "beyond_school_cockpit_blockout_revision3.blend",
)
OUTPUT = os.path.join(ROOT, "beyond_school_cockpit_blockout_revision4.blend")

bpy.ops.wm.open_mainfile(filepath=SOURCE)
scene = bpy.context.scene


def material(name, color, roughness=0.7):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def remove_prefix(prefix):
    for obj in list(bpy.data.objects):
        if obj.name.startswith(prefix):
            bpy.data.objects.remove(obj, do_unlink=True)


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def cylinder_between(name, start, end, radius, mat, parent=None):
    start = Vector(start)
    end = Vector(end)
    delta = end - start
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=24,
        radius=radius,
        depth=delta.length,
        location=(start + end) * 0.5,
    )
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = delta.to_track_quat("Z", "Y").to_euler()
    obj.data.materials.append(mat)
    if parent:
        world = obj.matrix_world.copy()
        obj.parent = parent
        obj.matrix_world = world
    return obj


def create_camera(name, location, target, lens=27):
    data = bpy.data.cameras.new(name)
    camera = bpy.data.objects.new(name, data)
    scene.collection.objects.link(camera)
    camera.location = location
    data.lens = lens
    data.sensor_width = 36
    look_at(camera, target)
    return camera


remove_prefix("REV4_")

rubber = material("REV4_Steering_Rubber", (0.035, 0.042, 0.045), 0.72)
metal = material("REV4_Steering_Metal", (0.20, 0.22, 0.24), 0.42)

# Center the existing steering root on the wheel hub so it is a usable future
# rotation pivot, while preserving the existing wheel and hub world transforms.
root = bpy.data.objects["STEERING_ROOT"]
preserved = {}
for name in ("STEERING_Wheel", "STEERING_Hub"):
    obj = bpy.data.objects.get(name)
    if obj:
        preserved[name] = obj.matrix_world.copy()
root.location = (0.42, -0.455, 1.08)
root.rotation_euler = (0.0, 0.0, 0.0)
for name, matrix in preserved.items():
    obj = bpy.data.objects[name]
    matrix.translation.z -= 0.10
    matrix.translation.x = 0.42
    matrix.translation.y = -0.455
    matrix.translation.z = 1.08
    obj.matrix_world = matrix
    if name == "STEERING_Wheel":
        obj.scale *= 0.86
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        obj.select_set(False)
        matrix = obj.matrix_world.copy()
        matrix.translation = Vector((0.42, -0.455, 1.08))
        obj.matrix_world = matrix

for name in ("STEERING_Column",):
    obj = bpy.data.objects.get(name)
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)

column = cylinder_between(
    "STEERING_Column",
    (0.42, -0.455, 1.08),
    (0.67, -0.455, 1.02),
    0.055,
    rubber,
    root,
)
column["interaction_axis"] = "STEERING_ROOT local Z rotation"
column["dashboard_connection"] = "Forward (+X) connection to dashboard"

# Explicit spokes make the steering wheel a complete, inspectable assembly.
for index, angle in enumerate((90.0, 210.0, 330.0)):
    radians = math.radians(angle)
    start = Vector((0.42, -0.455, 1.08))
    end = start + Vector(
        (0.0, math.sin(radians) * 0.150, math.cos(radians) * 0.150)
    )
    spoke = cylinder_between(
        "REV4_SteeringSpoke_%02d" % index,
        start,
        end,
        0.022,
        metal,
        root,
    )
    spoke["interaction_part"] = "Steering wheel spoke"

root["pivot_role"] = "Centered steering-wheel rotation pivot"
root["pivot_position_m"] = "(0.420, -0.455, 1.080)"

for name in ("DASH_InstrumentBinnacle", "DASH_InstrumentCluster"):
    obj = bpy.data.objects.get(name)
    if obj:
        obj.location.z -= 0.10

for name, dz in (("DASH_Shell", -0.12), ("DASH_UpperPad", -0.08)):
    obj = bpy.data.objects.get(name)
    if obj:
        obj.location.z += dz

# Preserve the Revision 3 road geometry and test only approved seated eye
# heights. Aim points are lowered slightly for the lower variants to retain
# the road corridor without lifting the driver's eye.
variants = (
    ("LOW", 1.250, (4.8, -0.20, 0.02)),
    ("MID", 1.290, (4.8, -0.20, 0.12)),
    ("HIGH", 1.330, (4.8, -0.20, 0.22)),
)
for label, height, target in variants:
    camera = create_camera(
        "REV4_Camera_%s" % label,
        (-0.620, -0.455, height),
        target,
        24,
    )
    camera["revision4_eye_height_m"] = height
    camera["revision4_target"] = "(%.3f, %.3f, %.3f)" % target
    camera["revision4_variant"] = label
    eye = bpy.data.objects.get("MARKER_DriverEye")
    if eye:
        eye.location = camera.location
    scene.camera = camera
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.filepath = os.path.join(
        ROOT, "driver_eye_revision4_%s.png" % label.lower()
    )
    bpy.ops.render.render(write_still=True)

# Restore the preferred mid-height marker and active camera after rendering.
preferred = bpy.data.objects["REV4_Camera_MID"]
scene.camera = preferred
eye = bpy.data.objects.get("MARKER_DriverEye")
if eye:
    eye.location = preferred.location

overall = create_camera(
    "REV4_Camera_Overall",
    (3.6, -7.2, 3.3),
    (5.0, 0.0, 0.65),
    42,
)
scene.camera = overall
scene.render.filepath = os.path.join(ROOT, "cockpit_overall_revision4.png")
bpy.ops.render.render(write_still=True)

scene.camera = preferred
scene["revision4"] = "Driver ergonomics and steering assembly correction"
scene["revision4_source"] = "Revision 3 preserved as input"
scene["revision4_eye_variants"] = "LOW 1.250 m; MID 1.290 m; HIGH 1.330 m"
scene["revision4_recommended_variant"] = "MID"
scene["revision4_steering_pivot"] = "(0.420, -0.455, 1.080)"
scene["revision4_steering_column"] = "(0.420,-0.455,1.080) to (0.670,-0.455,1.020)"
bpy.ops.wm.save_as_mainfile(filepath=OUTPUT)
