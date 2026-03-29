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

**Documentation menu:** Online/offline/PDF targets and opening offline HTML (preferring a local `http://127.0.0.1` server so MkDocs Material search works) are implemented in `NST_helper`—see that module and `CHANGELOG.md`.

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

`NST_helper.py` also defines `NST_FolderPath` at import time from its own location (toolkit root is the parent of `python/`). `menu.py` still assigns `NST_helper.NST_FolderPath` after import; both point at the same toolkit folder.

### Documentation URLs (`NST_helper`)

Documentation is opened from `NST_helper` (see `openNSTDocumentationDefault`, `openNSTDocumentationOffline`, `openNSTDocumentationPDF`).

- **Online wiki:** `webbrowser.open(NST_DOCS_ONLINE_URL)` with a prior HTTPS reachability check (`is_online_wiki_reachable`).
- **Offline HTML:** Prefer `http://127.0.0.1:<port>/` via a small local static server so MkDocs Material search works; if that fails, fall back to `offline_index.as_uri()` (`file://`).
- **PDF in toolkit root:** Resolve with `find_pdf_doc()` (`NST_DOCS_PDF_NAME` under `_toolkit_root()`), then open with `Path.as_uri()` so Windows drive letters become valid `file:///…` URLs:

```python
pdf_doc = find_pdf_doc()
if pdf_doc:
    webbrowser.open(pdf_doc.as_uri())
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

**Example (Read node `file` knob):**

| | Path |
|---|------|
| **Before** (placeholder in gizmo) | `<<<replace>>>/images/my_demo.exr` |
| **After** (at runtime) | `NST_FolderPath` + `/images/my_demo.exr` — e.g. `/…/NukeSurvivalToolkit/images/my_demo.exr` |

Put assets under `images/` next to `gizmos/`, `python/`, etc., and keep the path after `<<<replace>>>` relative to the toolkit root.

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
| `NST_helper.py` | Path replacement utility; documentation submenu (online/offline/PDF); local HTTP for offline HTML | nuke, nukescripts, pathlib, stdlib (http, threading) |
| `NST_ID_Extractor.py` | ID channel extraction | nuke, nukescripts |
| `NST_VectorTracker.py` | Vector-based tracking | nuke |
| `NST_cardToTrack.py` | CardToTrack v7 — 3D card to 2D track | nuke, math, threading |
| `NST_cardToTrack_v9.py` | CardToTrack v9 — used by NST_CardToTrack2, NST_CProject2, NST_TProject2 | nuke, math, re, time |
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

## Gizmo Etiquette

### Save as Group, not Gizmo

When you save a tool to disk, use a **Group** as the root node, not a **Gizmo**. NST ships tools as Groups so scripts remain valid if NST is not installed (for example on a render farm) or if the toolkit is removed. Internal nodes, expressions, and the Group structure still load; a Gizmo definition would not.

### Clean the header when pasting from Nuke

Copying a node from Nuke into a text editor often includes paste/stack boilerplate before the node block. Strip that so **`Group {` is the first line** of the tool, and verify the **`name`** matches the tool.

**Remove these lines** (everything above `Group {`):

```nk
set cut_paste_input [stack 0]
version 16.0 v8
push $cut_paste_input
```

(Version numbers will differ; remove the `set`, `version`, and `push` block in full.)

**Remove graph position** so the node does not snap to a fixed spot when the script is merged or opened elsewhere. Delete the `xpos` and `ypos` lines near the top of the Group, **before** the first `addUserKnob`:

```nk
 xpos 136
 ypos -78
```

**Example — raw paste (abbreviated):**

```nk
---

set cut_paste_input [stack 0]
version 16.0 v8
push $cut_paste_input
Group {
 name GradMagic
 tile_color 0x621d5aff
 gl_color 0xbffffff
 note_font "Verdana Bold"
 note_font_color 0x73e6e2ff
 selected true
 xpos 136
 ypos -78
 addUserKnob {20 GradMagic}
```

**Example — cleaned header:**

```nk
Group {
 name GradMagic
 tile_color 0x621d5aff
 gl_color 0xbffffff
 note_font "Verdana Bold"
 note_font_color 0x73e6e2ff
 selected true
 addUserKnob {20 GradMagic}
```

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
except ImportError:
    pass  # Stamps not installed, skip silently
```

**Tools with Stamps support:** ID_Extractor

## File Reference

| File | Purpose |
|------|---------|
| `menu.py` | Main menu creation and tool registration |
| `init.py` | Minimal stub (most work in menu.py) |
| `NST_helper.py` | `filepathCreateNode()` for dynamic paths; documentation menu (online/offline/PDF); local HTTP server for offline wiki when opening bundled HTML |
| `ColorGradientUi.py` | PySide6 gradient editor widget |
| `NST_ID_Extractor.py` | RGB channel extraction with Stamps |
| `NST_VectorTracker.py` | Vector/motion vector based tracking |
| `NST_cardToTrack.py` | CardToTrack v7 3D→2D conversion |
| `NST_cardToTrack_v9.py` | CardToTrack v9 3D→2D conversion; used by NST_CardToTrack2, NST_CProject2, NST_TProject2 gizmos |
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

## Contributing

When adding new tools:

1. Name the gizmo file `NST_ToolName.gizmo`
2. Add menu entry in appropriate section of `menu.py`
3. Use existing icon or add new one to `icons/`
4. If tools or tool demos need images to read in, add them to `images/` and use the `<<<replace>>>` placeholder in the Read (or other file) node's file path so `NST_helper.filepathCreateNode()` can substitute the toolkit root.
5. Update CHANGELOG.md with addition
