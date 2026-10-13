import math
import os

import bpy
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(
    os.path.dirname(ROOT),
    "revision4",
    "beyond_school_cockpit_blockout_revision4.blend",
)
OUTPUT = os.path.join(ROOT, "beyond_school_cockpit_blockout_revision5.blend")

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


def bar_between(name, start, end, thickness, width, mat, parent):
    start = Vector(start)
    end = Vector(end)
    delta = end - start
    bpy.ops.mesh.primitive_cube_add(
        location=(start + end) * 0.5,
    )
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = (thickness, width, delta.length)
    obj.rotation_euler = delta.to_track_quat("Z", "X").to_euler()
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    world = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_world = world
    return obj


remove_prefix("REV5_")

rubber = material("REV5_Steering_Rubber", (0.035, 0.042, 0.045), 0.72)
metal = material("REV5_Steering_Metal", (0.20, 0.22, 0.24), 0.42)

root = bpy.data.objects["STEERING_ROOT"]
root.location = (0.42, -0.455, 1.08)
root.rotation_euler = (0.0, 0.0, 0.0)
root["pivot_role"] = "Centered steering-wheel rotation pivot"
root["pivot_position_m"] = "(0.420, -0.455, 1.080)"

# Revision 4's vertical-cylinder spokes were not connected to the hub/rim.
# Remove only those spoke objects and replace them with planar bars that span
# from the hub perimeter into the torus inner perimeter.
for name in ("REV4_SteeringSpoke_00", "REV4_SteeringSpoke_01", "REV4_SteeringSpoke_02"):
    obj = bpy.data.objects.get(name)
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)

center = Vector((0.42, -0.455, 1.08))
hub_radius = 0.070
rim_inner_radius = 0.152
for index, angle in enumerate((90.0, 210.0, 330.0)):
    radians = math.radians(angle)
    direction = Vector((0.0, math.sin(radians), math.cos(radians)))
    start = center + direction * hub_radius
    end = center + direction * rim_inner_radius
    spoke = bar_between(
        "REV5_SteeringSpoke_%02d" % index,
        start,
        end,
        0.052,
        0.034,
        metal,
        root,
    )
    spoke["assembly_role"] = "Hub-to-rim steering spoke"

hub = bpy.data.objects["STEERING_Hub"]
hub["assembly_role"] = "Steering wheel hub"
wheel = bpy.data.objects["STEERING_Wheel"]
wheel["assembly_role"] = "Continuous steering wheel rim"

# Keep the locked Revision 4 MID eye position and 24 mm lens. Lower the aim
# to place the road corridor in the windshield without moving the driver.
camera = bpy.data.objects["REV4_Camera_MID"]
camera.location = (-0.620, -0.455, 1.290)
camera.data.lens = 24
look_at(camera, (6.0, -1.30, -0.70))
camera["revision5_eye_height_m"] = 1.290
camera["revision5_aim_point"] = "(6.000, -1.300, -0.700)"
camera["revision5_locked_mid"] = True

eye = bpy.data.objects["MARKER_DriverEye"]
eye.location = camera.location

# Only the temporary upper dashboard masses are reduced, preserving the
# cluster, wheel, mirror, hazard and overall cockpit proportions.
for name, dz in (("DASH_Shell", -0.16), ("DASH_UpperPad", -0.14)):
    obj = bpy.data.objects.get(name)
    if obj:
        obj.location.z += dz

scene.camera = camera
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.filepath = os.path.join(ROOT, "driver_eye_revision5_mid.png")
bpy.ops.render.render(write_still=True)

overall_data = bpy.data.cameras.new("REV5_Camera_Overall")
overall = bpy.data.objects.new("REV5_Camera_Overall", overall_data)
scene.collection.objects.link(overall)
overall.location = (3.6, -7.2, 3.3)
overall_data.lens = 42
look_at(overall, (5.0, 0.0, 0.65))
scene.camera = overall
scene.render.filepath = os.path.join(ROOT, "cockpit_overall_revision5.png")
bpy.ops.render.render(write_still=True)

scene.camera = camera
scene["revision5"] = "Locked MID steering and forward composition correction"
scene["revision5_source"] = "Revision 4 preserved as input"
scene["revision5_camera"] = "REV4_Camera_MID"
scene["revision5_steering_hierarchy"] = (
    "STEERING_ROOT > STEERING_Wheel, STEERING_Hub, REV5_SteeringSpoke_00..02, STEERING_Column"
)
scene["revision5_remaining_limitations"] = "Temporary blockout geometry; no production asset integration"
bpy.ops.wm.save_as_mainfile(filepath=OUTPUT)
