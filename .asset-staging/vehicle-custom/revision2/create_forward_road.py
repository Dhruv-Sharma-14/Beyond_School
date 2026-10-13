import bpy
import os
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(os.path.dirname(ROOT), "revision", "beyond_school_cockpit_blockout_revision.blend")
OUTPUT = os.path.join(ROOT, "beyond_school_cockpit_blockout_revision2.blend")

bpy.ops.wm.open_mainfile(filepath=SOURCE)
scene = bpy.context.scene

def material(name, color, roughness=0.7):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    return m

def cube(name, location, dimensions, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=location)
    o = bpy.context.object
    o.name = name
    o.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        mod = o.modifiers.new("Temporary_Rounded_Edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
    return o

def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()

road_mat = material("REV2_TEMP_Road", (0.075, 0.085, 0.085), 0.92)
shoulder_mat = material("REV2_TEMP_Shoulder", (0.30, 0.28, 0.24), 0.95)
line_mat = material("REV2_TEMP_LaneMarking", (0.88, 0.78, 0.47), 0.62)
edge_mat = material("REV2_TEMP_RoadEdge", (0.72, 0.68, 0.54), 0.70)
sign_mat = material("REV2_TEMP_AssistanceSign", (0.90, 0.18, 0.04), 0.58)
sign_white = material("REV2_TEMP_SignFace", (0.92, 0.92, 0.82), 0.55)
post_mat = material("REV2_TEMP_SignPost", (0.18, 0.19, 0.18), 0.82)

# Remove only the prior placeholder road and horizon from the copied revision.
for name in ["ROAD_HorizonPlane", "ROAD_CentreMarking", "ROAD_HorizonBackdrop"]:
    o = bpy.data.objects.get(name)
    if o:
        bpy.data.objects.remove(o, do_unlink=True)

# A visibly three-dimensional temporary divided-road slice, extending well beyond the windshield.
cube("REV2_RoadSurface", (10.5, 0.0, -0.055), (22.0, 8.0, 0.10), road_mat)
cube("REV2_LeftShoulder", (10.5, 4.55, -0.035), (22.0, 1.0, 0.06), shoulder_mat)
cube("REV2_RightShoulder", (10.5, -4.55, -0.035), (22.0, 1.0, 0.06), shoulder_mat)
cube("REV2_LeftRoadEdge", (10.5, 4.02, 0.005), (22.0, 0.08, 0.025), edge_mat)
cube("REV2_RightRoadEdge", (10.5, -4.02, 0.005), (22.0, 0.08, 0.025), edge_mat)

# Lane dividers and centre/median guidance lines.
for y in [-2.0, 0.0, 2.0]:
    for i in range(8):
        cube("REV2_LaneMark_%s_%02d" % (str(y).replace("-", "m").replace(".", "p"), i),
             (2.0 + i * 2.4, y, 0.012), (1.25, 0.065, 0.025), line_mat)
# A driver-side sightline marking kept within the windshield view for composition review.
for i in range(8):
    cube("REV2_DriverSightlineMark_%02d" % i,
         (1.6 + i * 2.4, -0.85, 0.018), (1.45, 0.09, 0.03), line_mat)
# Secondary shoulder-adjacent dashes placed high in the driver's visible road wedge.
for i in range(6):
    cube("REV2_VisibleRoadMark_%02d" % i,
         (3.0 + i * 2.5, -3.05, 0.022), (1.65, 0.12, 0.035), line_mat)
for i, x in enumerate((5.5, 8.0)):
    cube("REV2_VisibleRoadMark_Near_%02d" % i,
         (x, -3.65, 0.026), (1.55, 0.14, 0.04), line_mat)

# A low median silhouette beyond the visible lane, helping communicate road depth.
cube("REV2_MedianBase", (10.5, 3.35, 0.16), (22.0, 0.22, 0.32), edge_mat, 0.04)

# Simple roadside assistance sign silhouette on the driver-side shoulder.
sign_x = 7.2
sign_y = -4.18
cube("REV2_AssistanceSign_Post", (sign_x, sign_y, 1.02), (0.10, 0.10, 2.0), post_mat, 0.02)
cube("REV2_AssistanceSign_Board", (sign_x, sign_y, 1.85), (0.12, 1.10, 0.72), sign_mat, 0.04)
cube("REV2_AssistanceSign_Face", (sign_x - 0.065, sign_y, 1.85), (0.015, 0.82, 0.50), sign_white, 0.02)
cube("REV2_AssistanceSign_CrossV", (sign_x - 0.078, sign_y, 1.85), (0.02, 0.12, 0.34), sign_mat, 0.01)
cube("REV2_AssistanceSign_CrossH", (sign_x - 0.079, sign_y, 1.85), (0.02, 0.34, 0.12), sign_mat, 0.01)

# Use the approved Variant A camera as the preferred camera and retain B for comparison.
scene.camera = bpy.data.objects["CAM_REV_A_balanced"]
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.filepath = os.path.join(ROOT, "driver_eye_revision2_A_road.png")
bpy.ops.render.render(write_still=True)

# Supplementary overall view.
camera_data = bpy.data.cameras.new("CAM_REV2_Overall")
overall = bpy.data.objects.new("CAM_REV2_Overall", camera_data)
scene.collection.objects.link(overall)
overall.location = (3.9, -6.8, 2.7)
camera_data.lens =  forty_two = 42
look_at(overall, (2.0, 0.0, 0.85))
scene.camera = overall
scene.render.filepath = os.path.join(ROOT, "cockpit_overall_revision2_road.png")
bpy.ops.render.render(write_still=True)

scene["revision2"] = "Forward road visibility composition test"
scene["revision2_preferred_camera"] = "CAM_REV_A_balanced"
scene["revision2_road_geometry"] = "Temporary 3D road, lane markings, shoulders, edges, median and assistance sign"
scene.camera = bpy.data.objects["CAM_REV_A_balanced"]
bpy.ops.wm.save_as_mainfile(filepath=OUTPUT)
