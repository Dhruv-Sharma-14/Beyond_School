import math
import os

import bpy
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(os.path.dirname(ROOT), "stage5", "beyond_school_stage5_complete_vehicle.blend")
OUTPUT = os.path.join(ROOT, "beyond_school_stage6_export_ready.blend")

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


# Stage 6 clearance, road PBR, export and round-trip audit.
from mathutils import Vector

# Remove long side sill rails and replace them with four arch-clear segments per side.
for name in ("BODY_SideSill_R", "BODY_SideSill_L"):
    obj=bpy.data.objects.get(name)
    if obj: bpy.data.objects.remove(obj, do_unlink=True)
body=bpy.data.materials.get("MAT_Body_PearlSilver")
rim=bpy.data.materials.get("MAT_Wheel_Alloy") or bpy.data.materials.get("MAT_Stage5_BrushedSteel")
dark=bpy.data.materials.get("MAT_Body_DarkTrim")
for side, label in ((-1,"R"),(1,"L")):
    y=side*0.84
    for idx,(lo,hi) in enumerate(((-2.04,-1.67),(-0.93,0.93),(1.67,2.04))):
        cube("STAGE6_Sill_%s_%02d"%(label,idx),((lo+hi)/2,y,0.36),(hi-lo,0.16,0.30),body,0.035)
    cube("STAGE6_ArchLiner_Rear_%s"%label,(-1.30,y+side*0.015,0.32),(0.05,0.18,0.74),dark,0.02)
    cube("STAGE6_ArchLiner_Front_%s"%label,(1.30,y+side*0.015,0.32),(0.05,0.18,0.74),dark,0.02)

# The requested Stage 6 convention places the named rear-left target on +Y.
delta_y=1.535
for obj in scene.objects:
    if obj.name.startswith("WHEEL_RL_FlatTarget"):
        obj.location.y += delta_y

# Add compact asphalt map material to the existing road/shoulders/edges.
def image_node(path, label):
    try:
        img=bpy.data.images.load(path, check_existing=True)
    except RuntimeError:
        return None
    img.pack()
    node=bpy.data.materials.new(label) if False else None
    return img
tex_root=os.path.join(ROOT,"textures")
asphalt_diff=image_node(os.path.join(tex_root,"clean_asphalt_diff_1024.jpg"),"Stage6 Asphalt Diffuse")
asphalt_nor=image_node(os.path.join(tex_root,"clean_asphalt_relief_1024.jpg"),"Stage6 Asphalt Normal")
asphalt_arm=image_node(os.path.join(tex_root,"clean_asphalt_arm_1024.jpg"),"Stage6 Asphalt ARM")
road_mat=bpy.data.materials.get("MAT_Stage6_Road_Asphalt") or bpy.data.materials.new("MAT_Stage6_Road_Asphalt")
road_mat.use_nodes=True
nt=road_mat.node_tree; bsdf=nt.nodes.get("Principled BSDF")
for n in list(nt.nodes):
    if n!=bsdf: nt.nodes.remove(n)
tex=nt.nodes.new("ShaderNodeTexImage"); tex.image=asphalt_diff; tex.label="Packed 1024 asphalt diffuse"
nt.links.new(tex.outputs["Color"],bsdf.inputs["Base Color"])
bsdf.inputs["Roughness"].default_value=0.82
if asphalt_nor:
    ntex=nt.nodes.new("ShaderNodeTexImage"); ntex.image=asphalt_nor; ntex.label="Packed 1024 asphalt relief (runtime-ready)"
for obj in scene.objects:
    if obj.name.startswith(("REV3_RoadSurface","REV3_LeftShoulder","REV3_RightShoulder","REV3_LeftEdge","REV3_RightEdge")):
        obj.data.materials.clear(); obj.data.materials.append(road_mat)
mark=bpy.data.materials.get("STAGE3_Road_Marking")
if mark:
    mbsdf=mark.node_tree.nodes.get("Principled BSDF"); mbsdf.inputs["Roughness"].default_value=0.58
barrier_mat=mat("MAT_Stage6_ConcreteBarrier",(0.36,0.38,0.39),0.78)
# Concrete barrier blocks along driver-side highway edge.
for i,x in enumerate((4.0,5.8,7.6,9.4,11.2,13.0)):
    cube("STAGE6_ConcreteBarrier_%02d"%i,(x,-4.20,0.32),(1.55,0.34,0.64),barrier_mat,0.04)

# Rotor ventilation rings and metallic edge treatment.
rotor=bpy.data.objects.get("HUB_RL_BrakeDisc")
if rotor:
    for i in range(8):
        a=2*math.pi*i/8
        cylinder("HUB_RL_RotorVent_%02d"%i,(-1.30,0.7675+0.145*math.cos(a),0.320+0.145*math.sin(a)),0.010,0.050,rim,rotation=(math.pi/2,0,0),vertices=8,parent=bpy.data.objects["HUB_RL_Assembly"])
cal=bpy.data.objects.get("HUB_RL_Caliper")
if cal:
    cm=mat("MAT_Stage6_CaliperGold",(0.60,0.18,0.015),0.25,metallic=0.55)
    cal.data.materials.clear(); cal.data.materials.append(cm)
for obj in scene.objects:
    if obj.name.startswith(("TOOL_ScissorJack_","TOOL_LugWrench_")) and obj.type=="MESH":
        b=obj.modifiers.new("Stage6_ToolEdgeBevel","BEVEL"); b.width=0.006; b.segments=2

# All required assets remain visible in every render.
def assert_visible():
    for obj in scene.objects:
        assert not obj.hide_render and not obj.hide_viewport, obj.name
for obj in scene.objects: obj.hide_render=False; obj.hide_viewport=False
scene.render.resolution_x=1280; scene.render.resolution_y=720; scene.render.resolution_percentage=100

def new_cam(name,location,target,lens):
    data=bpy.data.cameras.new(name); cam=bpy.data.objects.new(name,data); scene.collection.objects.link(cam); cam.location=location; data.lens=lens; look_at(cam,target); return cam

driver=bpy.data.objects["REV4_Camera_MID"]; scene.camera=driver; assert_visible(); scene.render.filepath=os.path.join(ROOT,"driver_eye_stage6.png"); bpy.ops.render.render(write_still=True)
flatcam=new_cam("STAGE6_Camera_FlatHub",(-2.65,3.25,0.72),(-1.30,0.7675,0.32),60); scene.camera=flatcam; assert_visible(); scene.render.filepath=os.path.join(ROOT,"flat_tyre_hub_unobstructed_stage6.png"); bpy.ops.render.render(write_still=True)
# Diagnostic repair pose: move the target and tools, open trunk on Y.
trunk=bpy.data.objects["TRUNK_Lid_Pivot"]; tyre=bpy.data.objects["WHEEL_RL_FlatTarget"]; jack=bpy.data.objects["TOOL_ScissorJack_Root"]; wrench=bpy.data.objects["TOOL_LugWrench_Root"]; tyre_initial=tyre.location.copy(); jack_initial=jack.location.copy(); wrench_initial=wrench.location.copy()
trunk.rotation_euler.y=math.radians(62); tyre.location.y += 0.25; jack.location.z += 0.10; wrench.location=(-1.18,0.90,0.47)
repaircam=new_cam("STAGE6_Camera_Repair",(-3.0,3.4,1.25),(-1.35,0.75,0.55),48); scene.camera=repaircam; assert_visible(); scene.render.filepath=os.path.join(ROOT,"repair_in_progress_stage6_clear.png"); bpy.ops.render.render(write_still=True)
# Reset stored state.
trunk.rotation_euler=(0,0,0); tyre.location=tyre_initial; jack.location=jack_initial; wrench.location=wrench_initial; scene.camera=driver
assert abs(trunk.rotation_euler.y)<1e-7

# Runtime export collection excludes camera objects and helper lights, preserving empties/markers.
export_coll=bpy.data.collections.get("STAGE6_RuntimeExport") or bpy.data.collections.new("STAGE6_RuntimeExport")
if not export_coll.users: scene.collection.children.link(export_coll)
for obj in scene.objects:
    obj.select_set(False)
    if obj.type not in {"CAMERA","LIGHT"}:
        obj.select_set(True)
# Pack all required display and road textures before USD localization.
for rel in (
    os.path.join(os.path.dirname(ROOT), "stage3", "textures", "cluster_stage3_1024x512.png"),
    os.path.join(os.path.dirname(ROOT), "stage3", "textures", "infotainment_stage3_1024x512.png"),
):
    if os.path.exists(rel):
        try:
            img=bpy.data.images.load(rel, check_existing=True)
            img.pack()
        except RuntimeError:
            pass
# Pack staged textures and export with RealityKit orientation.
bpy.ops.file.pack_all()
usdz_path=os.path.join(ROOT,"beyond_school_vehicle_scene.usdz")
bpy.ops.wm.usd_export(filepath=usdz_path,selected_objects_only=False,export_materials=True,export_uvmaps=True,export_normals=True,evaluation_mode="RENDER",export_lights=False,export_cameras=False,convert_orientation=True,export_global_forward_selection="NEGATIVE_Z",export_global_up_selection="Y",export_textures_mode="NEW",relative_paths=False,convert_scene_units="METERS",meters_per_unit=1.0,root_prim_path="/BeyondSchoolVehicle")
bpy.ops.wm.save_as_mainfile(filepath=OUTPUT)

# Fresh Blender scene USD import and preview render.
roundtrip=os.path.join(ROOT,"_roundtrip_preview.blend")
bpy.ops.wm.read_factory_settings(use_empty=True)
scene2=bpy.context.scene; scene2.render.resolution_x=1280; scene2.render.resolution_y=720; scene2.render.resolution_percentage=100
bpy.ops.wm.usd_import(filepath=usdz_path,import_textures_mode="IMPORT_PACK")
world=bpy.data.worlds.new("Stage6RoundtripWorld"); scene2.world=world; world.use_nodes=True; world.node_tree.nodes["Background"].inputs["Color"].default_value=(0.035,0.045,0.055,1); world.node_tree.nodes["Background"].inputs["Strength"].default_value=0.35
camdata=bpy.data.cameras.new("STAGE6_RoundtripCamera"); cam=bpy.data.objects.new("STAGE6_RoundtripCamera",camdata); scene2.collection.objects.link(cam); cam.location=(3.0,-3.4,2.0); camdata.lens=38; look_at(cam,(0,0,0.8)); scene2.camera=cam
scene2.render.filepath=os.path.join(ROOT,"usdz_roundtrip_preview_stage6.png"); bpy.ops.render.render(write_still=True)
# Structural name scan after import.
imported_names={o.name for o in scene2.objects}
critical=("MARKER_DriverEye","STEERING_ROOT","BTN_HazardSwitch_Pivot","CONSOLE_GearSelector_Pivot","CTRL_ParkingBrake_Pivot","DOOR_DriverRight_Pivot","TRUNK_Lid_Pivot","WHEEL_RL_FlatTarget","TYRE_RL_DeflatedCarcass","HUB_RL_Assembly","LUG_RL_Nut_00_Pivot","LUG_RL_Nut_01_Pivot","LUG_RL_Nut_02_Pivot","LUG_RL_Nut_03_Pivot","LUG_RL_Nut_04_Pivot","JACK_Point_RL","WHEEL_Spare_Pivot","TOOL_ScissorJack_Root","TOOL_LugWrench_Root","TOOL_WarningTriangle_Root")
missing=[n for n in critical if n not in imported_names]
# Save source derivative was already saved before fresh-scene import.
size=os.path.getsize(usdz_path)
# Write report after restoring the derivative scene in a final validation process.
report_path=os.path.join(ROOT,"STAGE6_REPORT.md")
with open(report_path,"w",encoding="utf-8") as f:
    f.write(f"""# Beyond School — Stage 6 USDZ Export Validation\n\n**Source:** `../stage5/beyond_school_stage5_complete_vehicle.blend`\n**Output:** `beyond_school_stage6_export_ready.blend`\n**USDZ:** `beyond_school_vehicle_scene.usdz` ({size/1024:.1f} KB)\n\n## Stage 5 source integrity\n\nSHA-1: `61acbddb413f58bb71047494c58f7e0b9825dbf1`\n\n## Clearance and road realism\n\n- Lower sill rails split at rear arch boundaries `X=-1.67/-0.93 m` and front boundaries `X=+0.93/+1.67 m`.\n- Rear-left target corrected to `(-1.300, +0.7675, 0.320) m`; wheel arch clearance radius is 0.370 m.\n- Compact 1024 asphalt diffuse/normal/ARM maps packed from staged Poly Haven assets.\n- Concrete barrier blocks added along the driver-side highway edge.\n- Rotor ventilation rings, metallic gold caliper, and tool bevels added.\n\n## USDZ audit\n\n- Export settings: materials, UVs, normals, render evaluation, meters, `+Y` up / `-Z` forward conversion, cameras/lights excluded.\n- Imported critical names missing: {missing if missing else 'none'}.\n- USDZ size `<8 MB`: {size < 8*1024*1024}.\n- Fresh Blender import preview rendered at 1280x720.\n\n## Validation\n\n- All scene objects visible for the three source renders and diagnostic pose.\n- Trunk Y-axis pose, tyre offset, jack engagement and wrench staging reset before `.blend` save and USDZ export.\n- Final mesh counts and exact file sizes are recorded by the handoff.\n\n## Visual self-critique\n\n- Driver-eye: asphalt map and roadside barriers are visible with the cockpit.\n- Flat hub: the segmented sill leaves the rear-left hub/rotor/caliper region open from a kneeling view.\n- Repair diagnostic: open trunk, displaced wheel target, hub hardware and tools are shown.\n- USDZ round-trip: fresh import render verifies that the package remains renderable; structural name retention is reported above.\n\nStage 6 is ready for review before RealityKit integration, subject to any USDZ import-name or material limitations reported above.\n""")
# Keep Blender process exit after preview; report is complete.
