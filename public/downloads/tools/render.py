"""Render actual CAD preview mesh with a depth-buffered offline VTK renderer."""
from pathlib import Path
import trimesh,numpy as np,vtk
from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray
ROOT=Path(__file__).resolve().parents[1]
scene=trimesh.load(ROOT/'cad/preview.glb',force='scene')
ren=vtk.vtkRenderer();ren.SetBackground(.933,.937,.922)
for node in scene.graph.nodes_geometry:
    mat,g=scene.graph[node];m=scene.geometry[g].copy();m.apply_transform(mat)
    points=vtk.vtkPoints();points.SetData(numpy_to_vtk(m.vertices,deep=True))
    cells=vtk.vtkCellArray();faces=np.hstack((np.full((len(m.faces),1),3),m.faces)).astype(np.int64).ravel();cells.SetCells(len(m.faces),numpy_to_vtkIdTypeArray(faces,deep=True))
    poly=vtk.vtkPolyData();poly.SetPoints(points);poly.SetPolys(cells)
    normals=vtk.vtkPolyDataNormals();normals.SetInputData(poly);normals.ConsistencyOn();normals.AutoOrientNormalsOn();normals.SetFeatureAngle(35);normals.Update()
    mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normals.GetOutputPort());mapper.ScalarVisibilityOff()
    actor=vtk.vtkActor();actor.SetMapper(mapper);p=actor.GetProperty();p.SetColor(*(m.visual.face_colors[0,:3]/255));p.SetAmbient(.28);p.SetDiffuse(.72);p.SetSpecular(.08);p.SetSpecularPower(20);ren.AddActor(actor)
cam=ren.GetActiveCamera();cam.SetPosition(170,-250,300);cam.SetFocalPoint(0,0,13);cam.SetViewUp(0,0,1);cam.ParallelProjectionOn();cam.SetParallelScale(85)
for y,text,size in [(1250,'DIY MICRO / REV A',26),(1210,'CAD reconstruction | 110 x 110 mm | Fit testing required',19),(55,'Prototype geometry. Not a verified OEM replacement enclosure.',18)]:
    label=vtk.vtkTextActor();label.SetInput(text);label.SetPosition(80,y);t=label.GetTextProperty();t.SetFontSize(size);t.SetColor(.16,.22,.19);ren.AddActor2D(label)
window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1);window.SetSize(1800,1350);window.AddRenderer(ren);window.Render()
w=vtk.vtkWindowToImageFilter();w.SetInput(window);w.Update();out=vtk.vtkPNGWriter();out.SetFileName(str(ROOT/'docs/cad-preview.png'));out.SetInputConnection(w.GetOutputPort());out.Write();window.Finalize()
print('Rendered CAD preview using VTK')
