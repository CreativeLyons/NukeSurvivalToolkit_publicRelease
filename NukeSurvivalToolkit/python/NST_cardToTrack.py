import nuke

def setRefFrame():
    n = nuke.thisGroup()
    n.begin()
    nuke.toNode("Switch1")['disable'].setValue(0)
    nuke.toNode("ScanlineRender1")['disable'].setValue(0)
    nuke.toNode("StabFrameHold")['first_frame'].setValue(n['refFrame'].value())

    if n['S'].value() == 1:
        n['Stabilize'].execute()
        n = a.input(1) 
    ss = n.input(1)
    n.end()       
    topnode_name = nuke.tcl("full_name [topnode %s]" % ss.name()) 
    cam = nuke.toNode(topnode_name)
    cam['near'].clearAnimated()
    cam['far'].clearAnimated()
    cam['near'].setValue(0.01)
    cam['far'].setValue(10000)

    ss=n['scene'].value()
    n.begin()

    nuke.toNode("NoOp1")['pick'].execute()
    n['refFrame'].setValue(nuke.frame())
    nuke.toNode("Switch")['which'].setValue(0)

    r=nuke.toNode("Perspective")
    r.setSelected(False)
    r.hideControlPanel()
    r['rotate'].setValue(0)
    r['translate'].setValue(0)
    r['scaling'].setValue(1)
    r['uniform_scale'].setValue(ss)
    n.end()
        
    if n['extraHelper'].value() in [0,1,2]:
        n['findZ'].clearFlag(1)
        n['happyGroup'].setFlag(1)
        n['goGroup'].setFlag(1)
    if n['extraHelper'].value() in [1,2,5]:
        n['Adjust'].execute()

def stabilize():
    node = nuke.thisGroup() 
    t = node['S']
    h = node['HighPass']

    if t.value() == 0:
       nuke.thisKnob().setLabel('<font color="Red"><b>Stabilized')
       t.setValue(1)
       nuke.toNode("StabFrameHold")['disable'].setValue(0)
       nuke.toNode("StabFrameHold")['first_frame'].setValue(node['refFrame'].value())
       nuke.toNode("StabRef")['first_frame'].setValue(node['refFrame'].value())
       nuke.toNode("StabSwitch")['disable'].setValue(0)
    else:
       nuke.thisKnob().setLabel('Stabilize')
       t.setValue(0)
       h.setValue(0)
       nuke.toNode("StabFrameHold")['disable'].setValue(1)
       nuke.toNode("StabSwitch")['disable'].setValue(1)

def consolidateAnimatedNodeTransforms():
    # This is based on Ivan B's consolidateNodeTransforms().
    # Added support for animated Axis/Camera nodes. Also, if it's
    # a Camera being concatenated, then projection settings get copied.
    # -Ean C 24/Feb/2011
    import math
    import nuke
    axisNode = nuke.toNode('Z_finder')
    m = nuke.math.Matrix4()

    nuke.toNode("Switch")['which'].setValue(1)
    n = nuke.toNode('Perspective')
    n['scaling'].setExpression('curve')
    n['rotate'].setExpression('curve')
    n['translate'].setExpression('curve')

    first_frame_v = nuke.root()['first_frame'].value()
    last_frame_v = nuke.root()['last_frame'].value()
    scale_anim = n['scaling'].animations()
    rotate_anim = n['rotate'].animations()
    translate_anim = n['translate'].animations()

    for i in range(int(first_frame_v), int(last_frame_v+1)):
        k = axisNode['world_matrix']
        k_time_aware = axisNode['world_matrix'].getValueAt(i)
        for y in range(k.height()):
            for x in range(k.width()):
                m[x+(y*k.width())] = k_time_aware[y + k.width()*x]
            transM =nuke.math.Matrix4(m)
            transM.translationOnly()
            rotM = nuke.math.Matrix4(m)
            rotM.rotationOnly()
            scaleM = nuke.math.Matrix4(m)
            scaleM.scaleOnly()
            scale = (scaleM.xAxis().x, scaleM.yAxis().y, scaleM.zAxis().z)
            rot = rotM.rotationsZXY()
            rotDegrees = ( math.degrees(rot[0]), math.degrees(rot[1]), math.degrees(rot[2]) )
            trans = (transM[12], transM[13], transM[14])

            for s in range(3):
                scale_anim[s].setKey(i, scale[s])
                rotate_anim[s].setKey(i, rotDegrees[s])
                translate_anim[s].setKey(i, trans[s])
    n['translate'].clearAnimated()
    n['rotate'].clearAnimated()
    n['scaling'].clearAnimated()
    n['uniform_scale'].setValue(nuke.toNode("Card1")['uniform_scale'].value())
    #nuke.show((n), True)
    n.setSelected(True)
    r=nuke.toNode("look_at_Axis")
    r.setSelected(False)
    r.hideControlPanel()            

def happy():
    consolidateAnimatedNodeTransforms()
    a=nuke.thisNode()
    if a['S'].value() == 1:
        a['Stabilize'].execute()

    n=a
    if n['extraHelper'].value() in [0,1,2,5]:
        n['findZ'].setFlag(1)
        n['happyGroup'].clearFlag(1)
        n['goGroup'].clearFlag(1)

def go():
    import nuke
    axisCase = 0
    a=nuke.thisNode()
    C2Tgroup = nuke.thisNode()

    #check if camera has animation and if yes collect first and last frame of it
    with nuke.Root():
        try:
            n = a.input(1)
            topnode_name = nuke.tcl("full_name [topnode %s]" % n.name()) 
            topnode = nuke.toNode(topnode_name)
            n = topnode
            f,l=[],[]
            print (topnode.name())
            tr = n['translate'].getKeyList()
            first_frame_v = min(tr)
            last_frame_v = max(tr)
        except:
            first_frame_v = int(nuke.toNode('root')['first_frame'].value())
            last_frame_v = int(nuke.toNode('root')['last_frame'].value())


        if a['S'].value() == 1:   
            a['Stabilize'].execute()



    a.begin()
    x=int(a['xpos'].value())
    y=int(a['ypos'].value())
    p = nuke.toNode("Perspective")
    t=p['translate'].value()
    r=p['rotate'].value()
    s=p['scaling'].value()
    us=p['uniform_scale'].value()
    nuke.toNode("Switch")['which'].setValue(1)
    a.end()


    for node in nuke.allNodes():
        node.setSelected(False)
    try:    
        a.input(1).setSelected(True)
    except:
        nuke.message("please connect your Camera")
    try:
        a.input(0).setSelected(True)
    except:
        nuke.message("please connect your footage to BG input")

    #Card case
    if a['extraHelper'].value()==3:
        crd = a.input(2)
        crd.setSelected(True)
        crd.setXYpos(x,y+50)
        axisCase = 2
        
    #Axises case
    elif a['extraHelper'].value()==4:
        axisCase = 1
        
        import math
        import nuke
        
        axisNode = a.input(2)
        nuke.thisGroup().end()
        m = nuke.math.Matrix4()
        n = nuke.nodes.Card2()
        n['scaling'].setExpression('curve')
        n['rotate'].setExpression('curve')
        n['translate'].setExpression('curve')
        n['name'].setValue("consolidate of "+axisNode.name())
        n['xpos'].setValue(int(x))
        n['ypos'].setValue(int(y+50))
        scale_anim = n['scaling'].animations()
        rotate_anim = n['rotate'].animations()
        translate_anim = n['translate'].animations()
        
        for i in range(int(first_frame_v), int(last_frame_v+1)):
            k = axisNode['world_matrix']
            k_time_aware = axisNode['world_matrix'].getValueAt(i)
            for y in range(k.height()):
                for x in range(k.width()):
                    m[x+(y*k.width())] = k_time_aware[y + k.width()*x]
        
                transM =nuke.math.Matrix4(m)
                transM.translationOnly()
                rotM = nuke.math.Matrix4(m)
                rotM.rotationOnly()
                scaleM = nuke.math.Matrix4(m)
                scaleM.scaleOnly()
                scale = (scaleM.xAxis().x, scaleM.yAxis().y, scaleM.zAxis().z)
                rot = rotM.rotationsZXY()
                rotDegrees = ( math.degrees(rot[0]), math.degrees(rot[1]), math.degrees(rot[2]) )
                trans = (transM[12], transM[13], transM[14])
                for s in range(3):
                    scale_anim[s].setKey(i, scale[s])
                    rotate_anim[s].setKey(i, rotDegrees[s])
                    translate_anim[s].setKey(i, trans[s])
        a.input(1).setSelected(True)
        a.input(0).setSelected(True) 
        n.setSelected(True)
        a.setInput(2,n)
                
    #Deep input case         
    else:
        n = nuke.nodes.Card2()
        n.setXYpos(x,y+100)
        n['translate'].setValue(t)
        n['rotate'].setValue(r)
        n['scaling'].setValue(s)
        n['uniform_scale'].setValue(us)
        n.setSelected(True)

    with nuke.Root():
        try:
            import thread, threading, time, nuke, math, nukescripts
        except:
            import _thread, threading, time, nuke, math, nukescripts
        def execRC(first,last):
            runMe = True
            while runMe == True:
                nuke.execute('r1',first,last)  
                nuke.execute('r2',first,last) 
                nuke.execute('r3',first,last) 
                nuke.execute('r4',first,last) 
                stop_event.set()
                runMe = False
                break

        def getCamera():
            n = a.input(1) 
            topnode_name = nuke.tcl("full_name [topnode %s]" % n.name()) 
            topnode = nuke.toNode(topnode_name)
            cam = topnode
            return cam

        def BGdetect():
            for n in nuke.selectedNodes():
                if 'xform_order' not in n.knobs():
                    Name = n.name()
                    Width = n.width()
                    Height = n.height()
                    Aspect = n.pixelAspect()
                    form = str(Width)+" "+str(Height)+" "+str(Aspect)
                    bg = nuke.nodes.Constant(postage_stamp = False)
                    bg['format'].setValue(nuke.addFormat(form))
                    return bg

        def C2T(dialog):


            #card
            card = None
            for n in nuke.selectedNodes():
                if "Card" in n.Class() or "Axis" in n.Class():
                    card = n
                    break
            if card == None:
                nuke.message('no card selected?')
                return

            # initialize tool values for auto-creation
            label = card['label'].value()
            ref = int(nuke.frame())
            first = first_frame_v
            last = last_frame_v
            bg = BGdetect() 
            cam = getCamera()
            rootAspect = nuke.Root()['format'].value().pixelAspect()
            x = card.xpos() 
            y = card.ypos()
            
            bg.setXYpos(x,y+50)
            
            if dialog == True:
                #panel
                panel = nuke.Panel("C2T")
                panel.addSingleLineInput("label:", card['label'].value())
                panel.addSingleLineInput("firstFrame:", str(first))
                panel.addSingleLineInput("lastFrame:", str(last))
                panel.addSingleLineInput("ref frame:", str(ref))
                if panel.show():
                    first = int(panel.value("firstFrame:"))
                    last = int(panel.value("lastFrame:"))
                    ref = int(panel.value("ref frame:"))
                    if ref>last or ref<first:
                        ref = first
                    label = panel.value("label:")

                else:
                    nuke.message('canceled')
                    nuke.delete(bg) # clean the mess up
                    return
            else:
                print ('no dialog, use auto-created input values')
            

            # create master axis and corner slaves
            
            aM = nuke.nodes.Axis2(name = 'aM', xform_order = 3, xpos = x, ypos = y+50)
            uscale = card['uniform_scale'].value()
            scalex = card['scaling'].value(0)
            scaley = card['scaling'].value(1)
            
            if card['translate'].isAnimated() is True:
                aM['translate'].copyAnimations(card['translate'].animations())
            else:
                aM['translate'].setValue(card['translate'].value())
            
            if card['rotate'].isAnimated() is True:
                aM['rotate'].copyAnimations(card['rotate'].animations())
            else:
                aM['rotate'].setValue(card['rotate'].value())
                
                
            # slaves
            a1 = nuke.nodes.Axis2(name = 'a1', xform_order = 1, xpos = x, ypos = y+50)
            a2 = nuke.nodes.Axis2(name = 'a2', xform_order = 1, xpos = x, ypos = y+50)
            a3 = nuke.nodes.Axis2(name = 'a3', xform_order = 1, xpos = x, ypos = y+50)
            a4 = nuke.nodes.Axis2(name = 'a4', xform_order = 1, xpos = x, ypos = y+50)
            
            a1['translate'].setValue([-0.5*uscale*scalex,rootAspect*-0.5*uscale*scaley,0])
            a2['translate'].setValue([0.5*uscale*scalex,rootAspect*-0.5*uscale*scaley,0])
            a3['translate'].setValue([0.5*uscale*scalex,rootAspect*0.5*uscale*scaley,0])
            a4['translate'].setValue([-0.5*uscale*scalex,rootAspect*0.5*uscale*scaley,0])
            
            aL = [a1,a2,a3,a4]
            
            for a in aL:
                a.setInput(0,aM)

            # reconcile
            r1 = nuke.nodes.Reconcile3D(name = 'r1', xpos = x, ypos = y+50)
            r2 = nuke.nodes.Reconcile3D(name = 'r2', xpos = x, ypos = y+50)
            r3 = nuke.nodes.Reconcile3D(name = 'r3', xpos = x, ypos = y+50)
            r4 = nuke.nodes.Reconcile3D(name = 'r4', xpos = x, ypos = y+50)
            
            rL = [r1,r2,r3,r4]
            
            for r in rL:
                r.setInput(2,aL[rL.index(r)])
                r.setInput(1,cam)
                r.setInput(0,bg)
                
            # run with threading
            global stop_event 
            stop_event = threading.Event()
            threading.Thread(target=execRC, kwargs=dict(first=first,last=last)).start() 
            while not stop_event.is_set():
                time.sleep(0.1)

            problem = 0


            import math
            timeline = ["beginning","end"]#######looping to fix stuff before and after ref frame
            for side in timeline:##########################################################################################################: Fixing the curve###############################
                if side == "beginning":
                    firstT = first
                    lastT = ref
                if side == "end":
                    firstT = ref
                    lastT = last

                for one in rL:########fixing stuff
                    curveXUp = 0
                    curveXDown = 0
                    curveYUp = 0
                    curveYDown = 0
                    fuckedFrames = []
                    k = one["output"]
                    valsx = [];valSortx =[]
                    valsy = [];valSorty =[]
                    for i in range(firstT,lastT+1):
                        valsx.append(k.valueAt(i,0))
                        valSortx.append(k.valueAt(i,0))
                        valsy.append(k.valueAt(i,1))
                        valSorty.append(k.valueAt(i,1))
                    valSortx.sort()
                    valSorty.sort()
                    minX = valSortx[0]
                    maxX = valSortx[-1]
                    minY = valSorty[0]
                    maxY = valSorty[-1]
                    if math.fabs(valsx.index(maxX)-valsx.index(minX)) == 1:
                        problem = 1
            if problem == 1:
                if nuke.ask("Perspective problem detected! would you like to fix it? \n your card did pass the Camera center, this causes the track to break, i will try to fix the problem. if my fix will not succeed you should use a bit smaller card so corners of the card will not cross the camera so fast."):
                    problem = 0
                    import math
                    timeline = ["beginning","end"]#######looping to fix stuff before and after ref frame
                    lastB = last
                    firstB = first
                    for side in timeline:##########################################################################################################: Fixing the curve###############################
                        if side == "beginning":
                            last = ref
                        if side == "end":
                            first = ref
                            last = lastB

                        for one in rL:########fixing stuff
                            curveXUp = 0
                            curveXDown = 0
                            curveYUp = 0
                            curveYDown = 0
                            fuckedFrames = []
                            k = one["output"]
                            valsx = [];valSortx =[]
                            valsy = [];valSorty =[]
                            for i in range(first,last+1):
                                valsx.append(k.valueAt(i,0))
                                valSortx.append(k.valueAt(i,0))
                                valsy.append(k.valueAt(i,1))
                                valSorty.append(k.valueAt(i,1))
                            valSortx.sort()
                            valSorty.sort()
                            minX = valSortx[0]
                            maxX = valSortx[-1]
                            minY = valSorty[0]
                            maxY = valSorty[-1]
                            if math.fabs(valsx.index(maxX)-valsx.index(minX)) == 1:
                                problem = 1
                                if valsx.index(maxX)-valsx.index(minX) < 0:    ###############checking if the curve going up or down
                                    curveXUp = 1
                                else:
                                    curveXDown = 1
                                if valsy.index(maxY)-valsy.index(minY) < 0:    ###############checking if the curve going up or down
                                    curveYUp = 1
                                else:
                                    curveYDown = 1
                                if valsx.index(maxX)+first > ref:                                  ##### kill tail X
                                    if curveXDown == 1: ##### curve X is going down####################################################################################FIXEDforEnd
                                        lastGoodX= k.valueAt(valsx.index(minX)+first,0)
                                        prelastGoodX= k.valueAt(valsx.index(minX)+first-1,0)
                                        diffX= abs(lastGoodX) - abs(prelastGoodX)
                                        offsetX = abs(lastGoodX)+maxX+diffX*2
                                        for i in range(valsx.index(maxX)+first,last+1):
                                            val = k.valueAt(i)[0]
                                            k.setValueAt(val-offsetX,i,0)
                                    if curveXUp == 1: ##### curve X is going up####################################################################################FIXEDforEnd
                                        lastGoodX = k.valueAt(valsx.index(maxX)+first,0) 
                                        prelastGoodX= k.valueAt(valsx.index(maxX)+first-1,0) 
                                        diffX= abs(lastGoodX)- abs(prelastGoodX)
                                        offsetX= maxX+abs(minX)+diffX*2
                                        for i in range(valsx.index(minX)+first,last+1):
                                            val = k.valueAt(i)[0]
                                            k.setValueAt(val+offsetX,i,0)
                                if valsy.index(maxY)+first > ref:                                  ##### kill tail Y
                                    if curveYDown == 1: ##### curve Y is going down#####################################################################################FIXEDforEnd
                                        lastGoodY= k.valueAt(valsy.index(minY)+first,1)
                                        prelastGoodY= k.valueAt(valsy.index(minY)+first-1,1)
                                        diffY= abs(lastGoodY) - abs(prelastGoodY) 
                                        offsetY = abs(lastGoodY)+maxY+diffY*2
                                        for i in range(valsy.index(maxY)+first,last+1):
                                            val = k.valueAt(i)[1]
                                            k.setValueAt(val-offsetY,i,1)
                                    if curveYUp == 1: ##### curve Y is going up####################################################################################FIXEDforEnd
                                        lastGoodY = k.valueAt(valsy.index(maxY)+first,1) 
                                        prelastGoodY= k.valueAt(valsy.index(maxY)+first-1,1) 
                                        diffY=abs(lastGoodY) - abs(prelastGoodY) 
                                        offsetY= maxY+abs(minY)+diffY*2
                                        for i in range(valsy.index(minY)+first,last+1):
                                            val = k.valueAt(i)[1]
                                            k.setValueAt(val+offsetY,i,1)
                                if valsx.index(maxX)+first < ref:                                  ##### kill head X-------------------------------------------------------------------------------------
                                    if curveXDown == 1: ##### curve X is going down#####################################################################################FIXEDforBeginning
                                        firstGoodX= k.valueAt(valsx.index(maxX)+first,0)
                                        prefirstGoodX= k.valueAt(valsx.index(maxX)+first+1,0)
                                        diffX= abs(firstGoodX) - abs(prefirstGoodX) 
                                        offsetX = abs(firstGoodX)+abs(minX)+diffX*2
                                        for i in range(first,valsx.index(maxX)+first):
                                            val = k.valueAt(i)[0]
                                            k.setValueAt(val+offsetX,i,0)
                                    if curveXUp == 1: ##### curve X is going up#####################################################################################FIXEDforBeginning
                                        firstGoodX = k.valueAt(valsx.index(minX)+first,0) 
                                        prefirstGoodX= k.valueAt(valsx.index(minX)+first+1,0) 
                                        diffX= abs(firstGoodX) - abs(prefirstGoodX) 
                                        offsetX= abs(firstGoodX)+maxX+diffX*2
                                        for i in range(first,valsx.index(minX)+first):
                                            val = k.valueAt(i)[0]
                                            k.setValueAt(val-offsetX,i,0)
                                if valsy.index(maxY)+first < ref:                                  ##### kill head Y
                                    if curveYDown == 1: ##### curve Y is going down#####################################################################################FIXEDforBeginning
                                        firstGoodY = k.valueAt(valsy.index(maxY)+first,1)
                                        prefirstGoodY =  k.valueAt(valsy.index(maxY)+first+1,1)
                                        diffY =  abs(firstGoodY) - abs(prefirstGoodY)
                                        offsetY =  abs(firstGoodY)+abs(minY)+diffY*2
                                        for i in range(first,valsy.index(maxY)+first):
                                            val = k.valueAt(i)[1]
                                            k.setValueAt(val+offsetY,i,1)
                                    if curveYUp == 1: ##### curve Y is going up#####################################################################################FIXEDforBeginning
                                        firstGoodY = k.valueAt(valsy.index(minY)+first,1)
                                        prefirstGoodY = k.valueAt(valsy.index(minY)+first+1,1)
                                        diffY = abs(firstGoodY) - abs(prefirstGoodY)
                                        offsetY = abs(firstGoodY)+maxY+diffY*2
                                        for i in range(first,valsy.index(minY)+first):
                                            val = k.valueAt(i)[1]
                                            k.setValueAt(val-offsetY,i,1)

                    last = lastB
                    first = firstB
                else:
                    pass




            # corner pin normal or NST_CProject
            try :
                cp = nuke.nodes.NST_CProject(xpos = x+110, ypos = y)
                cp['camera'].setValue(cam.name())
                cp['translate'].setValue(card['translate'].value())
                cp['rotation'].setValue(card['rotate'].value())
                cp['element'].setValue(label)
                cp.setName("CP_"+label)
                cp['refFrame'].setValue(ref)
            except:
                cp = nuke.nodes.CornerPin2D(label = label +' ('+str(ref)+')', xpos = x+110, ypos = y)  
            cp['to1'].copyAnimations(r1['output'].animations())
            cp['to2'].copyAnimations(r2['output'].animations())
            cp['to3'].copyAnimations(r3['output'].animations())
            cp['to4'].copyAnimations(r4['output'].animations())
            cp['from1'].setValue(r1['output'].getValueAt(ref))
            cp['from2'].setValue(r2['output'].getValueAt(ref))
            cp['from3'].setValue(r3['output'].getValueAt(ref))
            cp['from4'].setValue(r4['output'].getValueAt(ref))

            #transform normal or NST_TProject
            try:
                tr = nuke.nodes.NST_TProject(xpos = x+330, ypos = y)
                tr.setName("TP_"+label)
                tr['translate'].setAnimated() 
            except:
                tr = nuke.nodes.Transform(label = label+' transform ('+str(ref)+')',xpos = x+330, ypos = y)
                tr['translate'].setAnimated()


            # corner pin matrix & roto & transform  
            if C2Tgroup["Matrix"].value() == True or C2Tgroup["Roto"].value() == True or C2Tgroup["Transform"].value() == True:
                cpm = nuke.nodes.CornerPin2D(label = label+' matrix ('+str(ref)+')', xpos = x+440, ypos = y)   
                cpm['transform_matrix'].setAnimated()



                roto = nuke.nodes.Roto( xpos = x+220, ypos = y) 
                roto.setName(roto['name'].value().replace('Roto','R')+"_"+label)
                roto_transform = roto['curves'].rootLayer.getTransform() # transform of root layer in roto
                nuke.show(roto)

                projectionMatrixTo = nuke.math.Matrix4()
                projectionMatrixFrom = nuke.math.Matrix4()
                frame = first
                while frame<last+1:

                    to1x = cp['to1'].valueAt(frame)[0]
                    to1y = cp['to1'].valueAt(frame)[1]
                    to2x = cp['to2'].valueAt(frame)[0]
                    to2y = cp['to2'].valueAt(frame)[1]
                    to3x = cp['to3'].valueAt(frame)[0]
                    to3y = cp['to3'].valueAt(frame)[1]
                    to4x = cp['to4'].valueAt(frame)[0]
                    to4y = cp['to4'].valueAt(frame)[1]

                    from1x = cp['from1'].valueAt(frame)[0]
                    from1y = cp['from1'].valueAt(frame)[1]
                    from2x = cp['from2'].valueAt(frame)[0]
                    from2y = cp['from2'].valueAt(frame)[1]
                    from3x = cp['from3'].valueAt(frame)[0]
                    from3y = cp['from3'].valueAt(frame)[1]
                    from4x = cp['from4'].valueAt(frame)[0]
                    from4y = cp['from4'].valueAt(frame)[1]
                
                    projectionMatrixTo.mapUnitSquareToQuad(to1x,to1y,to2x,to2y,to3x,to3y,to4x,to4y)
                    projectionMatrixFrom.mapUnitSquareToQuad(from1x,from1y,from2x,from2y,from3x,from3y,from4x,from4y)
                    theCornerpinAsMatrix = projectionMatrixTo*projectionMatrixFrom.inverse()
                    theCornerpinAsMatrix.transpose()

                    
                    for i in range(0,16):
                        if C2Tgroup["Matrix"].value() == True:
                            cpm['transform_matrix'].setValueAt(theCornerpinAsMatrix[i],frame,i)
                        if C2Tgroup["Roto"].value() == True:
                            if C2Tgroup["Matrix"].value() == False:
                                cpm['transform_matrix'].setValueAt(theCornerpinAsMatrix[i],frame,i) 
                            roto_transform.getExtraMatrixAnimCurve(0,i).addKey(frame,cpm['transform_matrix'].getValueAt(frame,i))  

                    if C2Tgroup["Transform"].value() == True:
                        tr['translate'].setValueAt((to1x+to2x+to3x+to4x)/4-bg.width()/2,frame,0)
                        tr['translate'].setValueAt((to1y+to2y+to3y+to4y)/4-bg.height()/2,frame,1)
                        tr['center'].setValue([bg.width()/2,bg.height()/2])


                

                    frame = frame + 1
                roto['curves'].changed()
                if C2Tgroup["Matrix"].value() == False:
                    nuke.delete(cpm)  
                if C2Tgroup["Roto"].value() == False:
                    nuke.delete(roto) 
                if C2Tgroup["Transform"].value() == False:
                    nuke.delete(tr) 

            # check for turnover
            k = cp['to1']
            vals = []
            valSort =[]
            for i in range(first,last+1):
                vals.append(k.valueAt(i,0))
                valSort.append(k.valueAt(i,0))
            valSort.sort()
            minVal = valSort[0]
            maxVal = valSort[-1]


            #clean up
            rmL = [r1,r2,r3,r4,a1,a2,a3,a4,aM,bg]
            for i in rmL:
                nuke.delete(i)
            #nuke.delete(bg)
            if axisCase ==1:
                C2Tgroup.setInput(2,axisNode)
                card['label'].setValue(label)
            elif axisCase == 2:#card case
                C2Tgroup.setInput(2,None)
                card.setInput(0,None)
            card['label'].setValue(label)

            if C2Tgroup["CornerPin"].value() == False:
                nuke.delete(cp)            
            if C2Tgroup["Card_1"].value() == False:
                nuke.delete(card)   
            if dialog == False:
                roto.setXYpos(x+100,y)
                #remove all non roto nodes
                nuke.delete(cp)
                nuke.delete(cpm)
            print ('C2T done.!!!!!')


        C2T(True)


def objectOnly():
    a=nuke.thisGroup()

    t = a['translate'].value()
    r = a['rotate'].value()
    s = a['scaling'].value()
    u = a['uniform_scale'].value()
    a.end()
    panel = nuke.Panel("object")
    panel.addSingleLineInput("Object Name:","")
    panel.addEnumerationPulldown("objects:", "Card Axis Cube Sphere Cylinder Light TransformGeo Camera")

    if panel.show(): 
        ob = panel.value("objects:")
        name = panel.value("Object Name:")
        obj = nuke.createNode(ob)
        x = a['xpos'].value()
        y = a['ypos'].value()
        obj.setInput(0,None)
        obj['xpos'].setValue(int(x))
        obj['ypos'].setValue(int(y+100))
        obj['translate'].setValue(t)
        obj['rotate'].setValue(r)
        obj['scaling'].setValue(s)
        obj['uniform_scale'].setValue(u)
        obj.setName(name)
