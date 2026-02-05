# NukeSurvivalToolkit Development Notes

This document captures key learnings, architecture decisions, and development knowledge for AI agents and developers working on this project.

## Architecture Overview

```
NukeSurvivalToolkit/
├── menu.py            # Main entry point - creates toolbar, loads all tools
├── init.py            # Minimal (plugin path setup happens in menu.py)
├── gizmos/            # 290+ .gizmo files (prefixed NST_)
├── python/            # Supporting Python modules
├── nk_files/          # .nk script templates and presets
├── icons/             # Menu and tool icons (.png)
└── images/            # Demo images referenced by gizmos
```

**Loading Flow:**
1. User adds `nuke.pluginAddPath("path/to/NukeSurvivalToolkit")` to their `init.py`
2. Nuke auto-loads `menu.py` on startup
3. `menu.py` registers plugin paths, imports helpers, creates the toolbar menu structure

## Menu System

### Entry Point: `menu.py`

The menu system uses `nuke.menu('Nodes')` to create a toolbar with submenus:

```python
toolbar = nuke.menu('Nodes')
NST_menu = toolbar.addMenu('NukeSurvivalToolkit', icon="SurvivalToolkit.png")
```

### Helper Functions

Two utility functions simplify path construction:

```python
def nk_path(filename, prefix=False):
    """Return full path to an .nk file in nk_files folder."""
    name = f"{prefixNST}{filename}" if prefix else filename
    return f"{NST_FolderPath}/nk_files/{name}"

def icon_path(filename):
    """Return full path to an icon file."""
    return f"{NST_FolderPath}/icons/{filename}"
```

Usage patterns:
```python
# With prefix (NST_AdvancedKeyingTemplate.nk)
nk_path("AdvancedKeyingTemplate.nk", prefix=True)

# Without prefix (deepThickness.nk)
nk_path("deepThickness.nk")
```

### Tool Creation Methods

There are three ways tools are added to menus:

1. **Direct gizmo creation** (most common):
   ```python
   menu.addCommand('ToolName', f"nuke.createNode('{prefixNST}ToolName')", icon="icon.png")
   ```

2. **Node paste from .nk file** (for templates/multi-node setups):
   ```python
   menu.addCommand('Template', f'nuke.nodePaste("{nk_path("Template.nk")}")')
   ```

3. **Helper function** (for tools needing file path replacement):
   ```python
   menu.addCommand('AutoFlare', f"NST_helper.filepathCreateNode('{prefixNST}AutoFlare2')")
   ```

## Gizmo Naming Convention

**All toolkit gizmos are prefixed with `NST_`** to avoid conflicts with user tools or other plugins.

```
NST_DummyCam.gizmo
NST_LabelFromRead.gizmo
NST_ID_Extractor.gizmo
```

The prefix is stored as a global in `menu.py`:
```python
global prefixNST
prefixNST = "NST_"
```

## Cross-Platform Path Handling

### The Windows Backslash Problem

Windows uses backslashes (`\`) in paths, which causes issues:
- `\n` in a path like `C:\nk_files\` is interpreted as a newline
- `nuke.nodePaste()` fails with malformed paths
- File knobs display incorrectly

**Solution:** Always use `Path.as_posix()` to force forward slashes:

```python
from pathlib import Path

# CORRECT - works on all platforms
NST_FolderPath = Path(__file__).parent.as_posix()

# WRONG - breaks on Windows
NST_FolderPath = os.path.dirname(__file__)
```

### Help Documentation URL

For opening local files in a browser, use `Path.as_uri()` to handle drive letters correctly:

```python
# Creates proper file:/// URL on all platforms
NST_helpDocPath = Path(f"{NST_FolderPath}/{NST_helpDoc}").as_uri()
```

## Dynamic File Path Replacement

Some gizmos contain Read/Camera nodes that reference image files in the toolkit. These use a placeholder pattern:

```python
# In gizmo: file path contains "<<<replace>>>"
# NST_helper.filepathCreateNode() swaps it with actual path

def filepathCreateNode(gizmoName):
    # ...create node...
    for i in fileNodes:
        if i.Class() in ("Read", "DeepRead", "ReadGeo", "ReadGeo2", "Camera2", "Axis2"):
            filepath = i.knob("file").getValue()
            if "<<<replace>>>" in filepath:
                newFilepath = filepath.replace("<<<replace>>>", NST_FolderPath)
                i.knob("file").setValue(newFilepath)
```

**Node classes that support file replacement:** Read, DeepRead, ReadGeo, ReadGeo2, Camera2, Axis2

## Python Module Loading

### Safe Import Pattern

When loading optional Python modules, use specific exception handling:

```python
# CORRECT - catches specific errors
try:
    import ColorGradientUi
    drawMenu.addCommand("GradientEditor", ...)
except ImportError as e:
    print(f"Could not load ColorGradientUi: {e}")
    pass

# ALSO CORRECT - for nuke.load()
try:
    nuke.load(f'{prefixNST}VectorTracker.py')
    menu.addCommand('VectorTracker', ...)
except RuntimeError as e:
    print(f"Could not load VectorTracker.py: {e}")
    pass
```

### Module Dependencies

| Module | Purpose | Dependencies |
|--------|---------|--------------|
| `ColorGradientUi.py` | Gradient editor widget | PySide6, ConfigParser |
| `NST_helper.py` | Path replacement utility | nuke, nukescripts, pathlib |
| `NST_ID_Extractor.py` | ID channel extraction | nuke, nukescripts |
| `NST_VectorTracker.py` | Vector-based tracking | nuke |
| `NST_cardToTrack.py` | 3D card to 2D track | nuke, math, threading |
| `NST_stickit.py` | Camera tracker warping | nuke, nuke.splinewarp, math |

## Nuke Version Compatibility

### Camera Class Changes (Nuke 13+)

Nuke 13 introduced `Camera3` class. Code must check for all camera types:

```tcl
# In DummyCam.gizmo TCL expression
if {[class $x]=="Camera3"||[class $x]=="Camera2"||[class $x]=="Camera"} {
    # handle camera...
}
```

### PySide Migration (Nuke 16+)

Nuke 16+ uses PySide6 instead of PySide2. The `ColorGradientUi.py` was updated:

```python
# Old (PySide2)
from PySide2 import QtGui, QtCore, QtWidgets

# New (PySide6)
from PySide6 import QtGui, QtCore, QtWidgets
from PySide6.QtWidgets import QWidget, QLabel, ...
from PySide6.QtGui import QColor, QPainter, ...
```

**Key change:** In PySide6, some classes moved from `QtWidgets` to `QtGui` (e.g., `QAction`).

## Gizmo Structure Patterns

### Basic Group Gizmo Structure

```nk
Group {
 name ToolName
 tile_color 0x3d3d3dff
 addUserKnob {20 TabName}
 addUserKnob {7 param l "Label" R 0 1}
}
 Input {
  inputs 0
  name Input1
 }
 # ... internal nodes ...
 Output {
  name Output1
 }
end_group
```

### Stack Operations

Use `set` and `push` for branching node graphs:

```nk
set N36754800 [stack 0]   # Save current position
# ... do something ...
push $N36754800           # Restore to saved position
# ... branch from there ...
```

### Expression Linking

Link internal nodes to parent Group knobs:

```nk
# Inside group - references parent knob
red {{parent.parent.LightSwitchPuppet.exp1}}

# Or with TCL value expression
label "[value parent.finalFilePath]"
```

## Callback Patterns

### knobChanged

Responds to any knob value change in the node:

```python
knobChanged "n = nuke.thisNode()\nk = nuke.thisKnob()\n\nif k.name() == \"mute1\":\n    if k.getValue() == 1:\n        n[\"tile_color\"].setValue(4278190335)"
```

### onCreate

Runs once when node is created (also on script load):

```python
onCreate "n = nuke.thisNode()\nfor k in [\"projection_mode\",\"focal\",...]:\n    n[k].setFlag(0x0000000010000000)"
```

**Flag `0x0000000010000000`:** `nuke.NO_UNDO` - prevents knob changes from creating undo events.

## TCL Expression Techniques

### DummyCam's Camera Traversal

The DummyCam gizmo uses TCL to find an upstream camera through any number of group levels:

```tcl
# Traverse up through inputs and groups to find camera
set x [node $starting_point]
while {$finished != 1} {
    while {[class $x] != "Camera3" && [class $x] != "Camera2" ...} {
        set x [node $x.input0]
    }
    # If found Input node, jump to parent group's corresponding input
    if {[class $x]=="Input"} {
        set inp "$x.parent.input"
        set inputNum [value $x.number]
        # ...
    }
}
```

### Frame-Aware Expressions

Get values at the correct frame, accounting for TimeOffset nodes:

```tcl
[expression [value the_cam]focal([value the_frame])]
```

Where `the_frame` evaluates to the camera's frame knob (handles retiming).

## Configuration Options

`menu.py` includes user-configurable variables:

```python
# Set to True to load the Expression Nodes AG submenu under Draw
LOAD_EXPRESSION_MENU = False
```

**Note:** Disabled by default to reduce menu clutter for users who don't need expression node presets.

## Integration with External Tools

### Stamps Integration

Several tools attempt to integrate with Adrian Pueyo's Stamps tool:

```python
try:
    import stamps
    stamps.anchor(title=channelName, tags="ID", input_node="", node_type="2D")
except:
    pass  # Stamps not installed, skip silently
```

**Tools with Stamps support:** ID_Extractor

## File Reference

| File | Purpose |
|------|---------|
| `menu.py` | Main menu creation and tool registration |
| `init.py` | Minimal stub (most work in menu.py) |
| `NST_helper.py` | `filepathCreateNode()` for dynamic paths |
| `ColorGradientUi.py` | PySide6 gradient editor widget |
| `NST_ID_Extractor.py` | RGB channel extraction with Stamps |
| `NST_VectorTracker.py` | Vector/motion vector based tracking |
| `NST_cardToTrack.py` | CardToTrack 3D→2D conversion |
| `NST_stickit.py` | SplineWarp from CameraTracker |
| `GradientPresets.cfg` | Stored gradient presets (ConfigParser) |

## Testing

1. Add toolkit path to `~/.nuke/init.py`:
   ```python
   nuke.pluginAddPath("/path/to/NukeSurvivalToolkit")
   ```

2. Restart Nuke

3. Look for red multi-tool icon in toolbar

4. Test individual tools by creating them from the menu

## Known Quirks

### Qt Color Order Bug

In `ColorGradientUi.py`, there's a noted color channel swap:
```python
# MUST BE A NUKE BUG THAT ITS GREEN BLUE ALPHA RED!!!
return QColor.fromRgbF(_green, _blue, _alpha, _red).rgba()
```

### Empty init.py

The `init.py` is essentially empty. All initialization happens in `menu.py`. This is intentional - keeps all code in one place.

### The `prefixNST` Global

Using `global prefixNST` is a legacy pattern. It works but a constant or module-level variable would be cleaner.

## Contributing

When adding new tools:

1. Name the gizmo file `NST_ToolName.gizmo`
2. Add menu entry in appropriate section of `menu.py`
3. Use existing icon or add new one to `icons/`
4. If tool needs images, add to `images/` and use `<<<replace>>>` pattern
5. Update CHANGELOG.md with addition
