import bpy, os, math
from mathutils import Vector
src='/Volumes/DHRUV/Beyond_School/.asset-staging/vehicle-custom/beyond_school_cockpit_blockout.blend'
outdir='/Volumes/DHRUV/Beyond_School/.asset-staging/vehicle-custom/revision'
os.makedirs(outdir, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=src)
scene=bpy.context.scene
# Keep original geometry intact except measured blockout refinements.
# Lower the dashboard upper obstruction and instrument surround, not the camera alone.
for name, dz in [('DASH_Shell',-0.07),('DASH_UpperPad',-0.08),('DASH_InstrumentBinnacle',-0.06),('DASH_InstrumentCluster',-0.04)]:
    o=bpy.data.objects.get(name)
    if o: o.location.z += dz
# Lower wheel slightly and move it rearward with the seat relationship.
for name, dx, dz in [('STEERING_ROOT',-0.04,-0.035)]:
    o=bpy.data.objects.get(name)
    if o: o.location.x += dx; o.location.z += dz
# Make driver mirror slightly inward and higher for a natural visible sightline.
mir=bpy.data.objects.get('MIRROR_Driver')
if mir:
    mir.location.y += 0.08
    mir.location.z += 0.04
# Make hazard switch slightly higher and more central, preserving separate object.
h=bpy.data.objects.get('BTN_HazardSwitch')
if h: h.location.z += 0.035
hm=bpy.data.objects.get('MARKER_HazardSwitch')
if hm: hm.location.z += 0.035
# Revision metadata
scene['revision']='Milestone 00C.1 Revision - Driver Eye Composition'
scene['revision_changes']='Measured dashboard lowering, slight steering-wheel lowering/rearward adjustment, driver-mirror inward/upward adjustment, hazard switch raised; three camera variants.'

def look_at(obj, target): obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
def make_cam(name, loc, target, lens):
    d=bpy.data.cameras.new(name); c=bpy.data.objects.new(name,d); scene.collection.objects.link(c)
    c.location=loc; d.lens=lens; d.sensor_width=36; look_at(c,target); return c
variants=[
 ('A_balanced',(-0.62,-0.455,1.31),(2.8,-0.18,1.39),27),
 ('B_lower_road',(-0.56,-0.455,1.27),(3.0,-0.16,1.47),26),
 ('C_wide_context',(-0.72,-0.455,1.33),(3.2,-0.12,1.42),24),
]
for name,loc,target,lens in variants:
    c=make_cam('CAM_REV_'+name,loc,target,lens); c['variant']=name; c['eye_position']=str(loc); c['aim_point']=str(target)
    scene.camera=c; scene.render.filepath=os.path.join(outdir,'driver_eye_'+name+'.png'); bpy.ops.render.render(write_still=True)
# overall reference view
c=make_cam('CAM_REV_Overall',(2.9,-4.5,2.4),(0.3,0,1.0),42); scene.camera=c
scene.render.filepath=os.path.join(outdir,'cockpit_overall.png'); bpy.ops.render.render(write_still=True)
# save after all adjustments, with balanced camera active
scene.camera=bpy.data.objects['CAM_REV_A_balanced']
scene.render.filepath=os.path.join(outdir,'driver_eye_A_balanced.png')
blend=os.path.join(outdir,'beyond_school_cockpit_blockout_revision.blend')
bpy.ops.wm.save_as_mainfile(filepath=blend)
