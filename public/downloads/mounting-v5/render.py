"""Static views of the actual exported STEP geometry (no illustrative substitutes)."""
from pathlib import Path
import cadquery as cq
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
R=Path(__file__).resolve().parent
names=['WAIT_full_top_plate','WAIT_lower_light_tray','PRINT_joystick_adapter','PRINT_FIRST_upper_joint_sample','PRINT_FIRST_lower_joint_sample','PRINT_FIRST_joystick_corner']
shapes={n:cq.importers.importStep(str(R/'files'/f'{n}.step')) for n in names}
ref=cq.importers.importStep(str(R/'references/joystick-reference.step')).rotate((0,0,0),(1,0,0),90).rotate((0,0,0),(0,0,1),90).translate((-9.25,-9.25,0)).rotate((0,0,0),(0,0,1),180).translate((29,30.5,26.6))
def draw(ax,items):
 faces=[];colors=[]
 for shape,color in items:
  rgb=np.array(matplotlib.colors.to_rgb(color))
  for solid in shape.solids().vals():
   vs,ts=solid.tessellate(.08);vs=np.array([v.toTuple() for v in vs])
   for tri in ts:
    face=vs[list(tri)];faces.append(face)
    n=np.cross(face[1]-face[0],face[2]-face[0]);n=n/max(np.linalg.norm(n),1e-12)
    colors.append(rgb*(.52+.34*abs(n[2])+.14*abs(n[0])))
 ax.add_collection3d(Poly3DCollection(faces,facecolors=colors,edgecolors=(0,0,0,0),linewidth=0))
 ax.set_axis_off()
fig=plt.figure(figsize=(16,10),facecolor='#f6f8fa')
configs=[
 ('1. Flat front; tray fasteners underneath',[(shapes['WAIT_full_top_plate'].translate((0,0,20)),'#c6dbe8'),(shapes['WAIT_lower_light_tray'],'#5b6e7e'),(shapes['PRINT_joystick_adapter'].translate((0,0,32)),'#eaa156')],(-52,52),(-50,52),(7,70),38,-60),
 ('2. Underside: four bosses hold the inserts',[(shapes['WAIT_full_top_plate'],'#c6dbe8')],(-52,52),(-50,52),(10,28),-40,-60),
 ('3. Separate adapter: solid pegs underneath',[(shapes['PRINT_FIRST_joystick_corner'],'#c6dbe8'),(shapes['PRINT_joystick_adapter'].translate((0,0,8)),'#eaa156'),(ref.translate((0,0,15)),'#44484c')],(16,49),(16,49),(20,50),20,-80),
 ('4. Print the small joint samples first',[(shapes['PRINT_FIRST_upper_joint_sample'].translate((0,0,10)),'#c6dbe8'),(shapes['PRINT_FIRST_lower_joint_sample'],'#5b6e7e')],(-27,27),(16,50),(7,38),32,-60),
]
for i,(title,items,x,y,z,e,a) in enumerate(configs):
 ax=fig.add_subplot(2,2,i+1,projection='3d',facecolor='#f6f8fa');draw(ax,items)
 ax.set(xlim=x,ylim=y,zlim=z);ax.set_box_aspect((x[1]-x[0],y[1]-y[0],z[1]-z[0]));ax.view_init(elev=e,azim=a);ax.set_title(title,fontsize=13,pad=0)
fig.suptitle('Codex Micro · Mounting v5',fontsize=22,y=.98)
fig.text(.5,.02,'Actual CAD geometry · Four corner case screws remain on the front · Physical fit testing required',ha='center',fontsize=11)
fig.subplots_adjust(top=.91,bottom=.05,left=.02,right=.98,hspace=.08,wspace=.05)
fig.savefig(R/'preview.png',dpi=140);plt.close(fig)
