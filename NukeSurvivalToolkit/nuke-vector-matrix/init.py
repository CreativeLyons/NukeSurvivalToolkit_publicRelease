"""
recursively adding all subfolders to plugin path
"""

import os
import nuke
try:
    import scandir as walk_module
except ImportError:
    import os as walk_module


CWD = os.path.dirname((os.path.abspath(__file__)))

# add Nuke Directory Recursively
nuke_dir = os.path.join(CWD, 'nuke')

for root, dirs, files in walk_module.walk(nuke_dir):
    nuke.pluginAddPath(root)
