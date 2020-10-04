'''
@author: Tony Lyons (creativelyons@gmail.com)
# init.py with recursive path loading.
'''
import os
import nuke

# var that points to the folder that this init file lives in
NST_FolderPath = os.path.dirname(__file__)

whiteList = []

# add Folder name to list to prevent it from loading
blackList = []

for root, dirs, files in os.walk(NST_FolderPath):
    # remove blacklist items
    for i in blackList:
        if i in dirs:
            dirs.remove(i)
    # ignore any folder that states with these characters
    dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('_')]
    #create whiteList
    for dir in dirs:
        whiteList.append( os.path.join(root, dir) )

# add plugin paths
print ("""
#################################################################
#################################################################
#################################################################
Adding {} plugin Directories from {}:""".format( len(whiteList)-1, os.path.basename(NST_FolderPath) ) )
for item in sorted(whiteList):
    nuke.pluginAddPath(str(item))
    print(item)

