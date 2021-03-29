import nuke
import nukescripts

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
        if i.Class() == "Read" or i.Class() == "DeepRead" or i.Class() == "ReadGeo" or i.Class() == "ReadGeo2" or i.Class() == "Camera2"  or  i.Class() == "Axis2":
            filepath = i.knob("file").getValue()
            if "<<<replace>>>" in filepath:
                newFilepath = filepath.replace("<<<replace>>>", NST_FolderPath)
                i.knob("file").setValue(newFilepath)

