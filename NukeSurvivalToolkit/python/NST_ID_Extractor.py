import nuke
import nukescripts

def set():
	n = nuke.thisNode()
	redName = n.knob('Red').value()
	greenName = n.knob('Green').value()
	blueName = n.knob('Blue').value()
	newName_list = [redName,greenName,blueName]

	for node in n.dependent():
	    if node.Class() == 'Shuffle':
	        for newName in newName_list:
	            if newName != "":
	                matte = newName_list.index(newName) + 1
	                if node.knob('red').getValue() == matte and node.knob('green').getValue() == matte and node.knob('blue').getValue() == matte and node.knob('alpha').getValue() == matte:
	                    shuffle = nuke.toNode(node.name())
	                    shuffle.setName(newName)
	                    nextDep = node.dependent()
	                    
	                    for anchor in nextDep:
	                        if anchor.Class() == 'NoOp':
	                            if anchor.input(0).Class() == "Shuffle":
	                                if 'title' in anchor.knobs():
	                                    anchorTitle = anchor.knob('title')
	                                    if anchorTitle.value() != newName:
	                                        anchorTitle.setValue(newName)


def extractRed():
	n = nuke.thisNode()
	nxpos = n.xpos()
	nypos = n.ypos()
	channelName = n['Red'].value()
	channelNameNoSpace = channelName.replace(" ", "_")

	if channelName != '':
	    n.end()
	    n.setSelected(True)
	    
	    dependents = n.dependent()
	    shuffles = []
	    for node in dependents:
	        if node.Class() == "Shuffle":
	            shuffles.append(node)
	            
	    shuffleNames = []
	    for shuffle in shuffles:
	        shuffleNames.append(shuffle.name())

	    if channelNameNoSpace not in shuffleNames:
	        s = nuke.nodes.Shuffle(name=channelNameNoSpace)
	        s.setXYpos(int(nxpos-100),int(nypos+110))
	        s.autoplace()
	        s.setInput(0,n)##################
	        matte = 1
	        s['tile_color'].setValue(2466250752)
	        s['red'].setValue(matte)
	        s['green'].setValue(matte)
	        s['blue'].setValue(matte)
	        s['alpha'].setValue(matte)
	        s['note_font_size'].setValue(12)
	        s['note_font_color'].setValue(4294967040)
	        
	        try:
	            import stamps
	            n.setSelected(False)
	            s.setSelected(True)
	            
	            stamps.anchor(title = channelName, tags = "ID", input_node = "", node_type = "2D")
	            
	        except:
	            pass
	     
	nukescripts.clear_selection_recursive()
	n.setSelected(True)

def extractGreen():
	n = nuke.thisNode()
	nxpos = n.xpos()
	nypos = n.ypos()
	channelName = n['Green'].value()
	channelNameNoSpace = channelName.replace(" ", "_")

	if channelName != '':
	    n.end()
	    n.setSelected(True)
	    
	    dependents = n.dependent()
	    shuffles = []
	    for node in dependents:
	        if node.Class() == "Shuffle":
	            shuffles.append(node)
	            
	    shuffleNames = []
	    for shuffle in shuffles:
	        shuffleNames.append(shuffle.name())

	    if channelNameNoSpace not in shuffleNames:
	        s = nuke.nodes.Shuffle(name=channelNameNoSpace)
	        s.setXYpos(int(nxpos),int(nypos+110))
	        s.autoplace()
	        s.setInput(0,n)##################
	        matte = 2
	        s['tile_color'].setValue(1063467008)
	        s['red'].setValue(matte)
	        s['green'].setValue(matte)
	        s['blue'].setValue(matte)
	        s['alpha'].setValue(matte)
	        s['note_font_size'].setValue(12)
	        s['note_font_color'].setValue(4294967040)
	        
	        try:
	            import stamps
	            n.setSelected(False)
	            s.setSelected(True)
	            
	            stamps.anchor(title = channelName, tags = "ID", input_node = "", node_type = "2D")
	            
	        except:
	            pass
	     
	nukescripts.clear_selection_recursive()
	n.setSelected(True)

def extractBlue():
	n = nuke.thisNode()
	nxpos = n.xpos()
	nypos = n.ypos()
	channelName = n['Blue'].value()
	channelNameNoSpace = channelName.replace(" ", "_")

	if channelName != '':
	    n.end()
	    n.setSelected(True)
	    
	    dependents = n.dependent()
	    shuffles = []
	    for node in dependents:
	        if node.Class() == "Shuffle":
	            shuffles.append(node)
	            
	    shuffleNames = []
	    for shuffle in shuffles:
	        shuffleNames.append(shuffle.name())

	    if channelNameNoSpace not in shuffleNames:
	        s = nuke.nodes.Shuffle(name=channelNameNoSpace)
	        s.setXYpos(int(nxpos+100),int(nypos+110))
	        s.autoplace()
	        s.setInput(0,n)##################
	        matte = 3
	        s['tile_color'].setValue(1027575296)
	        s['red'].setValue(matte)
	        s['green'].setValue(matte)
	        s['blue'].setValue(matte)
	        s['alpha'].setValue(matte)
	        s['note_font_size'].setValue(12)
	        s['note_font_color'].setValue(4294967040)
	        
	        try:
	            import stamps
	            n.setSelected(False)
	            s.setSelected(True)
	            
	            stamps.anchor(title = channelName, tags = "ID", input_node = "", node_type = "2D")
	            
	        except:
	            pass

	nukescripts.clear_selection_recursive()
	n.setSelected(True)

def extractAll():
	n = nuke.thisNode()
	red = n.knob('Red')
	redName = red.value()
	green = n.knob('Green')
	greenName = green.value()
	blue = n.knob('Blue')
	blueName = blue.value()

	if redName != "" and greenName != "" and blueName != "":
	    dependents = n.dependent()
	    shuffles = []
	    for node in dependents:
	        if node.Class() == "Shuffle":
	            shuffles.append(node)
	            
	    shuffleNames = []
	    for shuffle in shuffles:
	        shuffleNames.append(shuffle.name())
	    
	    if redName != "":
	        if redName.replace(" ", "_") not in shuffleNames:
	            n.knob("extractRed").execute()
	    if greenName != "":
	        if greenName.replace(" ", "_") not in shuffleNames:
	            n.knob("extractGreen").execute()
	    if blue.value() != "":
	        if blueName.replace(" ", "_") not in shuffleNames:
	            n.knob("extractBlue").execute()
	    
	    nukescripts.clear_selection_recursive()
	    n.setSelected(True)

def reset():
	n = nuke.thisNode()
	n.knob('Red').setValue('')
	n.knob('Green').setValue('')
	n.knob('Blue').setValue('')
