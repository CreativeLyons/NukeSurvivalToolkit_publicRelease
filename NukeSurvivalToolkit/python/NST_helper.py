import nuke
import nukescripts
import os

NST_FolderPath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# Defining a function to replace filepaths on tools importing files on creation

def filepathCreateNode(gizmoName):
    if '.nk' in gizmoName:
        nukescripts.clear_selection_recursive()
        nuke.nodePaste(gizmoName)
        fileNodes = nuke.selectedNodes()
    else:
        newGizmo = nuke.createNode(gizmoName)
        fileNodes = newGizmo.nodes()
    for i in fileNodes:
        if i.Class() in ("Read", "DeepRead", "ReadGeo", "ReadGeo2", "Camera2", "Axis2"):
            filepath = i.knob("file").getValue()
            if "<<<replace>>>" in filepath:
                newFilepath = filepath.replace("<<<replace>>>", NST_FolderPath)
                i.knob("file").setValue(newFilepath)
