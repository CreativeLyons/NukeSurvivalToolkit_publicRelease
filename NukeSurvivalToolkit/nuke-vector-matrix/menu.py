"""
Creates a menu and dynamically populate it with .gizmo, .so and .nk files
Supports icons by adding them either at the same level as the tool/subdir or in a /icons directory
All subdirectories are added to the nuke.pluginPath() (see init.py)
"""

import os
import re
import nuke
import matrix_utils
try:
    import scandir as walk_module
except ImportError:
    walk_module = os

CWD = os.path.dirname((os.path.abspath(__file__)))

#prefixNST = "NST_"

# Functions
def find_icon(name):
    path = os.path.join(CWD, 'icons')
    img = None
    for icon_ext in ['.jpg', '.png']:
        icon_path = os.path.join(path, name + icon_ext)
        if os.path.isfile(icon_path):
            img = icon_path

    return str(img) if img else None


def populate_menu_recursive(tool_path, menu):
    if not tool_path.endswith(os.sep):
        tool_path += os.sep

    for root, dirs, files in os.walk(tool_path):
        category = root.replace(tool_path, '').replace('\\', '/')
        # build the dynamic menus, ignoring empty dirs:
        for dir_name in natural_sort(dirs):
            if os.listdir(os.path.join(root, dir_name)):
                img = find_icon(dir_name)
                menu.addMenu(category + '/' + dir_name, icon=img)

        # if we have both dirs and files, add a separator
        if files and dirs:
            submenu = menu.addMenu(category)  # menu() and findItem() do not return a menu object.
            submenu.addSeparator()

        # Populate the menus
        for nuke_file in natural_sort(files):
            file_name, extension = os.path.splitext(nuke_file)
            if extension.lower() in ['.gizmo', '.so', '.nk']:
                img = find_icon(file_name.replace(prefixNST, ""))
                # Adding the menu command
                if extension.lower() in ['.nk']:
                    menu.addCommand(category + '/' + file_name.replace(prefixNST, "") + ' MT',
                                    'nuke.nodePaste( "{}" )'.format(os.path.join(root, nuke_file).replace('\\', '/')),
                                    icon=img)
                if extension.lower() in ['.gizmo', '.so']:
                    menu.addCommand(category + '/' + file_name,
                                    'nuke.createNode( "{}" )'.format(file_name),
                                    icon=img)
    return menu


def natural_sort(values, case_sensitive=False):
    """
    Returns a human readable list with integers accounted for in the sort.
    items = ['xyz.1001.exr', 'xyz.1000.exr', 'abc11.txt', 'xyz.0999.exr', 'abc10.txt', 'abc9.txt']
    natural_sort(items) = ['abc9.txt', 'abc10.txt', 'abc11.txt', 'xyz.0999.exr', 'xyz.1000.exr', 'xyz.1001.exr']
    :param values: string list
    :param case_sensitive: Bool. If True capitals precede lowercase, so ['a', 'b', 'C'] sorts to ['C', 'a', 'b']
    :return: list
    """
    def alpha_to_int(a, _case_sensitive=False):
        return int(a) if a.isdigit() else (a if _case_sensitive else a.lower())

    def natural_sort_key(_values):
        try:
            return tuple(alpha_to_int(c, case_sensitive) for c in re.split('(\d+)', _values) if c)
        except (TypeError, ValueError):
            return _values

    return sorted(values, key=natural_sort_key)


# Nodes Menu
toolbar = nuke.toolbar("Nodes")
toolbar_math_tools = toolbar.addMenu("NukeSurvivalToolkit/Transform/Math Tools MT", icon=find_icon("Math"), index=000)

nuke_dir = os.path.join(CWD, 'nuke')

populate_menu_recursive(nuke_dir, toolbar_math_tools)

# Utilities Menu
# By default in the main Nuke menu, change the next line to have the menu somewhere else.
#target_menu = nuke.menu('Nuke')
#transform_menu = target_menu.addMenu("Transform Utils", icon="transforms.png")
#transform_menu.addCommand("Convert Node Matrix", matrix_utils.run_convert_matrix)
#transform_menu.addCommand("Merge Transforms", matrix_utils.run_merge_transforms)