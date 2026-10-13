import bpy
import os
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(os.path.dirname(ROOT), "revision2", "beyond_school_cockpit_blockout_revision2.blend")
OUTPUT = os.path.join(ROOT, "beyond_school_cockpit_blockout_revision3.blend")

bpy.ops.wm.open_mainfile(filepath=SOURCE)
scene = bpy.context.scene

def material(name, color, roughness=0.7, emission=None):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 0.3
    return m

def cube(name, location, dimensions, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=location)
    o = bpy.context.object
    o.name = name
    o.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        mod = o.modifiers.new("Revision3_Rounded", "BEVEL")
        mod.width = bevel
        mod.segments = 2
    return o

def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()

def remove_prefix(prefix):
    for o in list(bpy.data.objects):
        if o.name.startswith(prefix):
            bpy.data.objects.remove(o, do_unlink=True)

road_mat = material("REV3_TEMP_Road", (0.065, 0.075, 0.075), 0.94)
shoulder_mat = material("REV3_TEMP_Shoulder", (0.28, 0.25, 0.20), 0.96)
line_mat = material("REV3_TEMP_LaneMarking", (0.92, 0.78, 0.38), 0.62)
edge_mat = material("REV3_TEMP_RoadEdge", (0.82, 0.78, 0.60), 0.68)
sign_mat = material("REV3_TEMP_AssistanceBoard", (0.12, 0.25, 0.34), 0.58)
sign_text_mat = material("REV3_TEMP_AssistanceText", (0.95, 0.88, 0.48), 0.44, emission=(0.16, 0.12, 0.02))
post_mat = material("REV3_TEMP_SignPost", (0.16, 0.17, 0.16), 0.85)

# Remove only copied temporary road/sign geometry from the Revision 2 source.
for prefix in ("REV2_", "REV3_"):
    remove_prefix(prefix)

# Projection diagnosis:
# Variant A eye = (-0.620,-0.455,1.310), original aim = (2.800,-0.180,1.390).
# That aim rises toward +X, so the ground corridor projects below the windshield.
# Keep eye position and lower aim to intersect the ground at a useful forward distance.
camera = bpy.data.objects["CAM_REV_A_balanced"]
camera.location = (-0.620, -0.455, 1.450)
look_at(camera, (4.8, -0.20, 0.38))
camera.data.lens = 27

eye_marker = bpy.data.objects.get("MARKER_DriverEye")
if eye_marker:
    eye_marker.location = camera.location
camera["revision3_diagnosis"] = "Lowered aim to intersect road plane; eye position retained"
camera["revision3_eye_position"] = "(-0.620, -0.455, 1.310)"
camera["revision3_aim_point"] = "(4.800, -0.200, 0.380)"

# The prior blockout dashboard still hid too much of the forward corridor.
# Lower only the temporary upper masses; preserve wheel/cluster relationships.
for name, dz in (("DASH_Shell", -0.180), ("DASH_UpperPad", -0.120)):
    obj = bpy.data.objects.get(name)
    if obj:
        obj.location.z += dz

# Road corridor centered on the forward camera projection.
cube("REV3_RoadSurface", (10.0, 0.0, -0.055), (22.0, 8.0, 0.10), road_mat)
cube("REV3_LeftShoulder", (10.0, 4.45, -0.015), (22.0, 0.95, 0.07), shoulder_mat)
cube("REV3_RightShoulder", (10.0, -4.45, -0.015), (22.0, 0.95, 0.07), shoulder_mat)
cube("REV3_LeftEdge", (10.0, 3.98, 0.018), (22.0, 0.085, 0.035), edge_mat)
cube("REV3_RightEdge", (10.0, -3.98, 0.018), (22.0, 0.085, 0.035), edge_mat)

# Perspective lane markings at three longitudinal distances and two corridor boundaries.
for y in (-2.0, 0.0, 2.0):
    for i, x in enumerate((2.2, 4.7, 7.2, 9.7, 12.2, 14.7, 17.2)):
        cube("REV3_LaneMark_%s_%02d" % (str(y).replace("-", "m").replace(".", "p"), i),
             (x, y, 0.025), (1.30, 0.09, 0.035), line_mat)

# A raised shoulder strip and low median give the view a readable lateral boundary.
cube("REV3_Median", (10.0, 3.30, 0.14), (22.0, 0.22, 0.28), edge_mat, 0.035)

# Sign is intentionally away from the camera and rotated to face the driver.
sign_x, sign_y = 8.5, -4.08
cube("REV3_AssistanceSign_Post", (sign_x, sign_y, 1.0), (0.10, 0.10, 1.95), post_mat, 0.02)
board = cube("REV3_AssistanceSign_Board", (sign_x, sign_y, 1.75), (0.12, 1.50, 0.62), sign_mat, 0.035)
face = cube("REV3_AssistanceSign_Face", (sign_x - 0.065, sign_y, 1.75), (0.015, 1.30, 0.42), sign_mat, 0.015)

# Text is an original temporary label, not a copied road sign.
bpy.ops.object.text_add(location=(sign_x - 0.078, sign_y + 0.02, 1.75), rotation=(0, 0, 1.5708))
text = bpy.context.object
text.name = "REV3_AssistanceSign_Text"
text.data.body = "HIGHWAY ASSISTANCE"
text.data.align_x = "CENTER"
text.data.align_y = "CENTER"
text.data.size = 0.16
text.data.extrude = 0.005
text.data.materials.append(sign_text_mat)
# The board's visible face is on the -X side; orient text toward the cockpit.
text.rotation_euler = (1.5708, 0, -1.5708)

scene.camera = camera
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.filepath = os.path.join(ROOT, "driver_eye_revision3_A_forward.png")
bpy.ops.render.render(write_still=True)

# Supplementary overall view showing the complete temporary corridor.
data = bpy.data.cameras.new("CAM_REV3_Overall")
overall = bpy.data.objects.new("CAM_REV3_Overall", data)
scene.collection.objects.link(overall)
overall.location = (3.6, -7.2, 3.3)
data.lens = 42
look_at(overall, (5.0, 0.0, 0.65))
scene.camera = overall
scene.render.filepath = os.path.join(ROOT, "cockpit_overall_revision3_forward.png")
bpy.ops.render.render(write_still=True)

scene["revision3"] = "Forward-view correction with coherent road corridor"
scene["revision3_preferred_camera"] = "CAM_REV_A_balanced"
scene["revision3_camera_change"] = "Eye retained; aim lowered to road intersection"
scene["revision3_sign_text"] = "HIGHWAY ASSISTANCE"
scene.camera = camera
bpy.ops.wm.save_as_mainfile(filepath=OUTPUT)
