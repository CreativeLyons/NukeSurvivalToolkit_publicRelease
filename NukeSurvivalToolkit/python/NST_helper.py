import nuke
import nukescripts
import os
from pathlib import Path

# Use Path.as_posix() to ensure forward slashes on all platforms (fixes Windows path issues)
NST_FolderPath = Path(__file__).parent.parent.as_posix()

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
