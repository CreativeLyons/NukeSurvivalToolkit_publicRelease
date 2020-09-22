'''
VectorTracker v1.0 by Jorrit Schulte

Add this to menu.py:
nuke.load('VectorTracker.py')
nuke.menu("Nodes").addCommand('user/VectorTracker', "nuke.createNode('VectorTracker.gizmo')")
'''

def allScriptNodes():
    #collect all nodes in the root node graph
    nodes = nuke.allNodes()
    groups = [node for node in nodes if node.Class() == 'Group' ]

    #first collect groups inside groups
    for group in groups:
        for i in group.nodes():
            if i.Class() == 'Group':
                groups.append(i)
    #then append nodes inside groups to the nodes list
    for group in groups:
        for node in group.nodes():
            nodes.append(node)
    #return all nodes on all levels
    return nodes

def J_VTT_Track(first, last, pb = True):
    node = nuke.thisNode()
    vectors = node.input(1)

    #bool to check track direction
    forward = last > first

    #get number of frames
    totalFrames = max(first, last) - min(first, last)

    #check vector type
    if vectors is not None:
        layers = list( set([channel.split('.')[0] for channel in vectors.channels()]) )
    else:
        layers = []

    if 'smartvector' in layers:
        if forward:
            u = 'smartvector.fn1vp0_u'
            v = 'smartvector.fn1vp0_v'
        else:
            u = 'smartvector.fp1vp0_u'
            v = 'smartvector.fp1vp0_v'
        run = True
    elif 'forward' in layers and forward:
        u = 'forward.u'
        v = 'forward.v'
        run = True
    elif 'backward' in layers and not forward:
        u = 'backward.u'
        v = 'backward.v'
        run = True
    else:
        run = False

    #check if there are vectors
    if run:
        #collect existing trackers
        trackers = [i.name() for i in node.allKnobs() if i.Class() == 'XY_Knob' and 'tracker' in i.name()]
        #remove inactive trackers
        trackers = [i for i in trackers if node['enable_' + i].value()]

        #lists where tracker position data get stored
        xpos = []
        ypos = []
        xsize = []
        ysize = []
        for tracker in trackers:
            #Append initial positions
            trackerVal = node[tracker].valueAt(first)
            xpos.append(trackerVal[0])
            ypos.append(trackerVal[1])
            #append sample area sizes
            xsize.append(node['sampleArea_'+tracker].value(0))
            ysize.append(node['sampleArea_'+tracker].value(1))

            #make tracker knobs keyable
            node[tracker].setAnimated()

        #set frame list
        if forward:
            rangeList = xrange(first, last+1)
        else:
            rangeList = reversed(xrange(last, first+1))

        #set up pogress window
        if pb:
            task = nuke.ProgressTask("VectorTracker")
            count = 0

        #cycle through frames
        for frame in rangeList:

            #stop tracking if process is cancelled
            if pb:
                if task.isCancelled():
                    break

            #update process window
            if frame != last and pb:
                count += 1
                task.setMessage("sampling frame " + str(frame) + ' (frame ' + str(count) +' of ' + str(totalFrames) + ')')
                task.setProgress(count*100/totalFrames)

            #execute for each tracker
            for i, tracker in enumerate(trackers):
                #get current position from list
                curx = xpos[i]
                cury = ypos[i]

                #set keyframe
                node[tracker].animations()[0].setKey(frame, curx)
                node[tracker].animations()[1].setKey(frame, cury)

                if frame != last:
                    #sample vectors
                    x = vectors.sample(u, curx+.5, cury+.5, xsize[i],ysize[i], frame)
                    y = vectors.sample(v, curx+.5, cury+.5, xsize[i],ysize[i], frame)

                    #set new position
                    xpos[i] = curx + x
                    ypos[i] = cury + y

            #jump to frame
            nuke.frame(frame)
        if pb:
            del task
    #message when there is no vector data
    else:
        nuke.message('No vectors found!')

def J_VTT_AddTracker():
    node = nuke.thisNode()

    trackerCount = int(node['count'].value() + 1)
    node['count'].setValue(trackerCount)

    name = 'tracker' + str(trackerCount)

    #enable knob
    enableKnob = nuke.nuke.Boolean_Knob('enable_' + name, '')
    enableKnob.setValue(True)
    enableKnob.setFlag(nuke.STARTLINE)
    enableKnob.setTooltip('Enable this tracker for tracking')
    node.addKnob( enableKnob )

    #position knob
    posKnob = nuke.nuke.XY_Knob(name, name)
    posKnob.clearFlag(nuke.STARTLINE)
    node.addKnob( posKnob )

    #area size knob
    areaKnob = nuke.nuke.WH_Knob('sampleArea_' + name, 'area')
    areaKnob.setValue(1)
    areaKnob.setRange(1,50)
    areaKnob.clearFlag(nuke.STARTLINE)
    areaKnob.clearFlag(0x00000004) #clear LOG_SLIDER flag
    areaKnob.setFlag(0x00000010) #set FORCE_RANGE flag
    areaKnob.setTooltip('Size of the area that will get sampled in the vector channels')
    node.addKnob( areaKnob )

    #remove knob
    removeKnob = nuke.PyScript_Knob('remove_' + name, '@ColorMult', "node = nuke.thisNode()\nname = '" + name + "'\n\nknobs = ['', 'sampleArea_', 'enable_', 'remove_' ]\n\nfor i in knobs:\n    try:\n        node.removeKnob(node.knobs()[i + name])\n    except:\n        pass")
    removeKnob.setTooltip('Remove this tracker')
    node.addKnob( removeKnob )

def J_VTT_Export():
    node = nuke.thisNode()

    #deselect nodes
    an = allScriptNodes()
    selnodes = [i for i in an if i['selected'].value()]
    for snode in selnodes:
        snode['selected'].setValue(False)
    #select VectorTracker node
    node['selected'].setValue(True)

    #find group name if node is in group
    fnn = node.fullName().split('.')
    groupName = 'root.'
    for i in range(len(fnn)-1):
        groupName += fnn[i] + '.'
    #get parent
    if groupName != 'root.':
        parent = nuke.toNode(groupName[:-1])
    else:
        parent = nuke.root()

    #create node in parent root
    with parent:
        #create tracker node
        trackerNode = nuke.nodes.Tracker4()
        trackerNode['xpos'].setValue(node['xpos'].value()+100)
        trackerNode['ypos'].setValue(node['ypos'].value()+50)
        trackerNode.showControlPanel()

        #define tracks container knob
        container = trackerNode['tracks']

        #collect existing trackers
        trackers = [i.name() for i in node.allKnobs() if i.Class() == 'XY_Knob' and 'tracker' in i.name()]

        #copy keyframes for each tracker
        for i, tracker in enumerate(trackers):
            #add tracker to container
            trackerNode['add_track'].execute()

            #remove auto made keys
            for inx in [0,2,3,4,5,9]:
                container.removeKey(i*31 + inx)
            container.setValue(False, i*31 + 6)

            #define some stuff
            trackerKnob = node[tracker].value()
            tracker = node[tracker]

            #set keys for x and y curves
            for curve in [0,1]:
                animcheck = tracker.animation(0+curve) is not None

                #set value if there is no animation
                if not animcheck:
                    container.setValue(trackerKnob[0+curve], i*31 + 2+curve)

                #if there are keyframes on original tracker knob
                if animcheck:
                    #set x y knobs animated
                    container.setAnimated(i*31 + 2+curve)

                    #find frame numbers of first and last keyframe
                    keys = tracker.animation(0+curve).keys()
                    first = int(keys[0].x)
                    last = int(keys[len(keys)-1].x)

                    #set value at each frame
                    framerange = xrange(first, last+1)
                    for frame in framerange:
                        #check if current frame is tracked before setting key
                        if tracker.isKeyAt(frame):
                            pos = tracker.getValueAt(frame)
                            #set key
                            container.setValueAt(pos[0+curve],frame,i*31+2+curve)

                    #remove key at frame 0 if not used
                    if 0 not in framerange:
                        container.removeKeyAt(0,i*31 + 2+curve)

        #reselect nodes
        trackerNode['selected'].setValue(False)
        for snode in selnodes:
            snode['selected'].setValue(True)
        #deselect VectorTracker node
        if node not in selnodes:
            node['selected'].setValue(False)

