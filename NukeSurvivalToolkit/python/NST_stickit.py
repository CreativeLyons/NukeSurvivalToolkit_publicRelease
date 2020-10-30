# stickit.py
# Copyright (c) 2017 Mads Hagbarth Damsbo. All Rights Reserved.
# Not for redistribution.

import nuke
import nuke.splinewarp as sw 
import string #This is used by the code. Include!
import math
import struct
import time

'''
REAL TODO:

General Feedback:
In regards to assist its hard to figure if something have been sucessfully been applied or not.
  This could be fixed by making a green label with "Roto Node Assisted", then fade to grey using a timer.

MUST HAVE:
  -Hook up the "Output" options to their respective nodes
    in that regard remove the "hide source" option
  -Check the buttons in the buttom of the advanced tab and remove the ones that we no longer need.
  -Test the heck out of different formats and what not to enure that we don't get bounding issues.
  -option to invert input mask!
  -The ST map should source its X and Y from the Source image, not the overlay image!
  --Add a option to only source the alpha from the Overlay (so that if the source have a alpha it won't carry through.)
  Add another ST frame offset for calculating center motionblur. (or should it be hacked using offset?)

NICE TO HAVE:
  Add a button for the ref frame called "Current Frame"
  Add a status that show if the shot have been tracked and solved (solve range aswell).
    This should also highlight if the "Disable Warp" have been toggeled
  Add some Analyze/Tracking presets (ie; Full Frame, Medium Object, Small Object)
  Add a button that generates a ST-Map node and a vectorblur node outside the node. (Create ST Setup)



DONE
  +Make sure that the ST map matches. (check again!)  


FOR CONSIDERATION:
Consider a workflow to work with fully obscured regions (guides maybe)
Post filter that takes all the keyframes created and does eighter smoothing or reduces the number of keyframes to the bare minimum (based on a threshold)
    Calculate the length of the vector
    Devide each axis by the length to get a normalized vector
    First do a check to ensure that the vector is shorter than the threshold
    Then comput a direction that is the averaged normalized vector from the frames that we inspect
      If the computed direction is within the threshhold then...
  one thing that there is to consider is that you may want to not write down the keyframes first.
  for example in a roto or rotopaint workflow, it might be smart to gther the keyframes, filter, then apply them to the spline.


Save the animation curve.
  Add a interpolate range feature. 
    -You set the in and out point.
    -You hit interpolate (it will do a linear interpolation between the points)
    -Now the user can retrack forward



'''

'''
#Todo:
-Get all points from the CameraTracker and put them into a list
-Create a initial set of points, this could be all points on a certain frame or a general set of points.
  If we take from a certain frame we need to get a list of all points that are on the specified frame
-For every source object we put in a single value that is the XY pos of the object in the specified frame

-For every target object we triangulate the nearby points and get a new position, we do that for all the frames in the framerange specified.
-For every target object we bake animation calculated in the step above


Remember that we must save the new calculated position into a new list or modify the exsisting to get perfect results
'''

'''================================================================================
; Function:          CreateWarpPinPair(myNode):
; Description:       Create a Splinewarp pin pair.
; Parameter(s):      node - The node create pin in
; Return(s):         Returns a pair of pin objects (_curveknob.Stroke objects) [source,target]
;                    specified - Only take knobs with this tag (like "UserTrack" from a cameratracker)
; Note(s):            N/A
;=================================================================================='''
def CreateWarpPinPair(myNode,pointlist,refframe):
  ItemX = pointlist

  #First we want to clear the current splinewarp.
  #As there is no build-in function to do this, we just purge it with default data
  warpCurve = myNode['curves'] 
  warpRoot = warpCurve.rootLayer
  Header = """AddMode 0 0 1 0 {{v x3f99999a}
  {f 0}
  {n
  {layer Root
  {f 0}
  {t x44800000 x44428000}
  {a pt1x 0 pt1y 0 pt2x 0 pt2y 0 pt3x 0 pt3y 0 pt4x 0 pt4y 0 ptex00 0 ptex01 0 ptex02 0 ptex03 0 ptex10 0 ptex11 0 ptex12 0 ptex13 0 ptex20 0 ptex21 0 ptex22 0 ptex23 0 ptex30 0 ptex31 0 ptex32 0 ptex33 0 ptof1x 0 ptof1y 0 ptof2x 0 ptof2y 0 ptof3x 0 ptof3y 0 ptof4x 0 ptof4y 0 pterr 0 ptrefset 0 ptmot x40800000 ptref 0}}}}
  """
  warpCurve.fromScript(Header)
  warpCurve.changed()

  #As we just cleared the curves knob we need to re-fetch it. 
  #If we don't do this Nuke will crash in some cases.
  #This should be reported to TheFoundry.
  warpCurve = myNode['curves'] 
  warpRoot = warpCurve.rootLayer

  #We start off by creating all the pins that we need.
  #We do this in 2 steps. First we create the src then the dst
  for i in range(0, len(ItemX)):
    PinSource = sw.Shape(warpCurve, type="bezier") #single point distortion 
    newpoint = sw.ShapeControlPoint() #create point 
    ConvertedX = float(pointlist[i][int(refframe-float(pointlist[i][0][0]))][1])
    ConvertedY = float(pointlist[i][int(refframe-float(pointlist[i][0][0]))][2])
    newpoint.center = (ConvertedX,ConvertedY) #set center position
    newpoint.leftTangent = (0,0) #set left tangent relative to center
    newpoint.rightTangent = (0,0) #set right tangent relative to center
    PinSource.append(newpoint) #add point to shape 
    PinTarget = sw.Shape(warpCurve, type="bezier") #single point distortion 
    newpointB = sw.ShapeControlPoint() #create point
    newpointB.center = (ConvertedX,ConvertedY) #set center position
    newpointB.leftTangent = (0,0) #set left tangent relative to center
    newpointB.rightTangent = (0,0) #set right tangent relative to center
    PinTarget.append(newpointB) #add point to shape 
    warpRoot.append(PinSource) #add to the rootLayer 
    warpRoot.append(PinTarget) #add to the rootLayer 
    warpCurve.defaultJoin(PinSource,PinTarget) 
    warpCurve.changed() #Update the curve

    PinSource.getTransform().getTranslationAnimCurve(0).removeAllKeys()
    PinSource.getTransform().getTranslationAnimCurve(1).removeAllKeys()
    PinTarget.getTransform().getTranslationAnimCurve(0).removeAllKeys()
    PinTarget.getTransform().getTranslationAnimCurve(1).removeAllKeys()
    PinSource.getTransform().addTranslationKey(refframe,0,0,100.0)
    for ix in range(0, len(pointlist[i])):

      PinTarget.getTransform().getTranslationAnimCurve(0).addKey(pointlist[i][ix][0],float(pointlist[i][ix][1])-float(pointlist[i][int(refframe-float(pointlist[i][0][0]))][1]))
      PinTarget.getTransform().getTranslationAnimCurve(1).addKey(pointlist[i][ix][0],float(pointlist[i][ix][2])-float(pointlist[i][int(refframe-float(pointlist[i][0][0]))][2]))
      #print pointlist[i][ix][0]
    warpCurve.changed() #Update the curve

  CurrentData = warpCurve.toScript().replace('{f 8192}','{f 8224}') #Convert to splinewarp pins
  warpCurve.fromScript(CurrentData)


'''================================================================================
; Function:             ExportCameraTrack(myNode):
; Description:          Extracts all 2D Tracking Featrures from a 3D CameraTracker node (not usertracks).
; Parameter(s):         myNode - A CameraTracker node containing tracking features
; Return:               Output - A list of points formated [ [[Frame,X,Y][...]] [[...][...]] ]
;                           
; Note(s):              N/A
;=================================================================================='''
def ExportCameraTrack(myNode):
    myKnob = myNode.knob("serializeKnob")
    myLines = myKnob.toScript()    
    DataItems = string.split(myLines, '\n')
    Output = []
    for index,line in enumerate(DataItems):
        tempSplit = string.split(line, ' ')
        if (len(tempSplit) > 4 and tempSplit[ len(tempSplit)-1] == "10") or (len(tempSplit) > 6 and  tempSplit[len(tempSplit)-1] == "10"): #Header
            #The first object always have 2 unknown ints, lets just fix it the easy way by offsetting by 2
            if len(tempSplit) > 6 and  tempSplit[6] == "10":
                offsetKey = 2
                offsetItem = 0
            else:
                offsetKey = 0
                offsetItem = 0
            #For some wierd reason the header is located at the first index after the first item. So we go one step down and look for the header data.
            itemHeader = DataItems[index+1]
            itemHeadersplit = string.split(itemHeader, ' ')
            itemHeader_UniqueID = itemHeadersplit[1]

            #So this one is rather wierd but after a certain ammount of items the structure will change again.
            backofs = 0
            lastofs = 0
            firstOffset = 0
            secondOffset = 0
            secondItem = DataItems[index+2]
            secondSplit = string.split(secondItem, ' ')
            if len(secondSplit) == 7:
                 firstOffset = 0

            if len(itemHeadersplit) == 3:
                itemHeader = DataItems[index+2]
                itemHeadersplit = string.split(itemHeader, ' ')
                offsetKey = 2
                offsetItem = 2
                if len(secondSplit) == 11:
                  firstOffset = 1 #In this case the 2nd item will be +1   
                  backofs = 1             
                elif len(secondSplit) == 7:
                  firstOffset = 1
                else:
                  firstOffset = 0 #In this case the 2nd item will be +0


            itemHeader_FirstItem = itemHeadersplit[3+offsetItem]
            itemHeader_NumberOfKeys = itemHeadersplit[4+offsetKey]
        
            #Here we extract the individual XY coordinates
            PositionList =[]
            PositionList.append([LastFrame+(0),float(string.split(DataItems[index+0], ' ')[2])  ,float(string.split(DataItems[index+0], ' ')[3])])
            for x in range(2,int(itemHeader_NumberOfKeys)+1):
                if len(string.split(DataItems[index+x+firstOffset-1], ' '))>7 and len(string.split(DataItems[index+x+firstOffset-1], ' '))<10 and int(string.split(DataItems[index+x+firstOffset-1], ' ')[5]) > 0:
                  Offset = int(string.split(DataItems[index+x+firstOffset-1], ' ')[7])
                  PositionList.append([LastFrame+(x-1),float(string.split(DataItems[Offset+1], ' ')[2])  ,float(string.split(DataItems[Offset+1], ' ')[3])]) 
                  secondOffset = 1
                else:
                  
                  if x==(int(itemHeader_NumberOfKeys)) and backofs == 1:
                    PositionList.append([LastFrame+(x-1),float(string.split(DataItems[int(lastofs)], ' ')[2] ) ,float(string.split(DataItems[int(lastofs)], ' ')[3])])    
                  else:
                    PositionList.append([LastFrame+(x-1),float(string.split(DataItems[index+x+firstOffset-secondOffset], ' ')[2] ) ,float(string.split(DataItems[index+x+firstOffset-secondOffset], ' ')[3])])         
                if len(string.split(DataItems[index+x+firstOffset+secondOffset], ' ')) > 5 and len(string.split(DataItems[index+x+firstOffset+secondOffset], ' ')) < 16:
                  lastofs = str(string.split(DataItems[index+x+firstOffset+secondOffset], ' ')[5])
                else:
                  lastofs = index+x+1

            Output.append(PositionList)
        elif (len(tempSplit) > 8 and tempSplit[1] == "0" and tempSplit[2] == "1"):
            LastFrame = int(tempSplit[3])
        else:  #Content
          pass
    return Output

'''================================================================================
; Function:             GetAnimtionList(myList,myFrame):
; Description:          Returns a list of points that contain animation between myFrame and the following frame
; Parameter(s):         myList - A list of points formated [ [[Frame,X,Y][...]] [[...][...]] ]
                        myFrame - The frame to take into consideration 
; Return:               Output - A list of points formated [ [[Frame,X,Y][...]] [[...][...]] ]
;                           
; Note(s):              N/A
;=================================================================================='''
def GetAnimtionList(myList,nestedPoints,myFrame,_rev=False,_ofs=False):   
    Output = []
    thisFrame = int(myFrame)
    try:
      if _rev: #This will reverse the output
        for i,item in enumerate(nestedPoints[thisFrame]):
            if nestedPoints[thisFrame][i][4]>thisFrame: 
                outThisframe = myList[nestedPoints[thisFrame][i][2]][(thisFrame-nestedPoints[thisFrame][i][3])]
                outNextframe =  myList[nestedPoints[thisFrame][i][2]][(thisFrame-nestedPoints[thisFrame][i][3])+1]
                Output.append([outNextframe,outThisframe])
      elif _ofs: #This is a temporary fix to the strange offset bug
        for i,item in enumerate(nestedPoints[thisFrame]):
            if nestedPoints[thisFrame][i][4]>thisFrame: 
                outThisframe = myList[nestedPoints[thisFrame][i][2]][(thisFrame-nestedPoints[thisFrame][i][3])]
                outNextframe =  myList[nestedPoints[thisFrame][i][2]][(thisFrame-nestedPoints[thisFrame][i][3])+1]
                outThisframe = [outThisframe[0],outThisframe[1]+1,outThisframe[2]+0.01]
                outNextframe = [outNextframe[0],outNextframe[1]+1,outNextframe[2]+0.01]
                Output.append([outNextframe,outThisframe])      
      else:
        for i,item in enumerate(nestedPoints[thisFrame]):
            if nestedPoints[thisFrame][i][4]>thisFrame: 
                outThisframe = myList[nestedPoints[thisFrame][i][2]][(thisFrame-nestedPoints[thisFrame][i][3])]
                outNextframe =  myList[nestedPoints[thisFrame][i][2]][(thisFrame-nestedPoints[thisFrame][i][3])+1]
                Output.append([outThisframe,outNextframe])
    except:
      pass #No points on this frame!
    return Output

'''================================================================================
; Function:             GetNearestPoints(myList,myFrame):
; Note(s):              N/A
;=================================================================================='''
def GetNearestPoints(refpoint,pointList,_rev=False):
  if len(pointList) < 3:
    xOffset = 0.0
    yOffset = 0.0
  else:
    #Distance Calculation
    x1 = refpoint[1]
    y1 = refpoint[2]
    distancelist = []
    #Check if there is more than 3 points at the current frame.
    for item in pointList: #Does it read from the same frame or a new one?
      #print item
      x2 = item[0][1]
      y2 = item[0][2]
      dist = math.hypot(x2-x1, y2-y1)
      distancelist.append(dist+1)

    sorted_lookup = sorted(enumerate(distancelist), key=lambda i:i[1])

    index0 = sorted_lookup[0][0]
    index1 = sorted_lookup[1][0]
    index2 = sorted_lookup[2][0]

    perc0 = 1 / (sorted_lookup[0][1])
    perc1 = 1 / (sorted_lookup[1][1])
    perc2 = 1 / (sorted_lookup[2][1])

    if perc0 == 1:
      perc1 = 0
      perc2 = 0
    perctotal = perc0+perc1+perc2

    Percent0 = perc0 if perctotal == 0 else perc0 / (perctotal)
    Percent1 = perc1 if perctotal == 0 else perc1 / (perctotal)
    Percent2 = perc2 if perctotal == 0 else perc2 / (perctotal)
    x02 = pointList[index0][1][1]
    y02 = pointList[index0][1][2]
    x12 = pointList[index1][1][1]
    y12 = pointList[index1][1][2]
    x22 = pointList[index2][1][1]
    y22 = pointList[index2][1][2]
    x01 = pointList[index0][0][1]
    y01 = pointList[index0][0][2]
    x11 = pointList[index1][0][1]
    y11 = pointList[index1][0][2]
    x21 = pointList[index2][0][1]
    y21 = pointList[index2][0][2]
    xOffset = (((x02-x01) * Percent0) + (( x12-x11) * Percent1) + (( x22-x21) * Percent2))
    yOffset = (((y02-y01) * Percent0) + (( y12-y11) * Percent1) + ((y22-y21) * Percent2))
  return [xOffset, yOffset]

def GrabListData():
    Node = nuke.toNode("si_ct") #change this to your tracker node!
    #01: Get all points from the cameratracker node.
    _return = ExportCameraTrack(Node)

    #02: To optimize the lookups we index all the data into frame lists containing [x,y,index,firstframe,lastframe]
    #     this will give a 40+ times performence boost.
    item_dict = {}
    for list_index, big_lst in enumerate(_return):
        for lst in big_lst:
            if lst[0] in item_dict:
                item_dict[lst[0]] += [lst[1:]+[list_index]+[_return[list_index][0][0], _return[list_index][len(_return[list_index])-1][0]],] # Append
            else:
                item_dict[lst[0]] = [lst[1:]+[list_index]+[_return[list_index][0][0], _return[list_index][len(_return[list_index])-1][0]],] # Initialize
    return [_return,item_dict]

'''================================================================================
Simple median.
;=================================================================================='''
def median(lst):
    sortedLst = sorted(lst)
    lstLen = len(lst)
    index = (lstLen - 1) // 2
    if (lstLen % 2):
        return sortedLst[index]
    else:
        return (sortedLst[index] + sortedLst[index + 1])/2.0

'''================================================================================
RangeKeeper, use to store and calculate frame ranges.
;=================================================================================='''
class rangeKeeper():
  def __init__(self,_type):
    self.frameForRef = 0
    self.StartFrame = 0
    self.EndFrame = 0
    self.type = _type
    self.appendAnimation = False
    self.initvalues()

  def initvalues(self):
    self.appendAnimation = nuke.thisNode().knob("appendAnimation").value()

    if nuke.thisNode().knob("assistStep").value(): #We only run "x" number of frames
      _thisFrame = nuke.frame()
      _startFrame = _thisFrame - int(nuke.thisNode().knob("AssistStepSize").value())
      _endFrame = _thisFrame + int(nuke.thisNode().knob("AssistStepSize").value())
    else: #We run the full range
      _thisFrame = nuke.frame()
      _startFrame = int(nuke.thisNode().knob("InputFrom").value())
      _endFrame = int(nuke.thisNode().knob("InputTo").value()) 
    if self.type == 0: #Both Ways
      self.frameForRef = _thisFrame
      self.StartFrame = _startFrame
      self.EndFrame = _endFrame  
    elif self.type == 1: #Only forward
      self.frameForRef = _thisFrame
      self.StartFrame = _thisFrame
      self.EndFrame = _endFrame 
    elif self.type == 2: #Only Backwards
      self.frameForRef = _thisFrame
      self.StartFrame = _startFrame
      self.EndFrame = _thisFrame


'''================================================================================
; Function:             KeyframeReducer():
; Description:          Removes unwanted keyframes based on a threshold
;                           
; Note(s):              _method  #0 = Local, 1 = Median, 2 = Average
;=================================================================================='''
def KeyframeReducer(knob):
    myKnob = knob
    threshold = 1.5
    firstFrame = 1
    lastFrame = 99
    reduce = False
    for frame in range(firstFrame,lastFrame):
        xd = myKnob.getValueAt(frame)[0]-myKnob.getValueAt(frame+1)[0]
        yd = myKnob.getValueAt(frame)[1]-myKnob.getValueAt(frame+1)[1]
        delta = math.sqrt(xd*xd+yd*yd)
        if delta < threshold:
            if reduce:
                print "Reduce this",frame
                if myKnob.isAnimated():
                    myKnob.removeKeyAt(frame)
            else:
                print help(myKnob.setValueAt)
                #myKnob.removeKeyAt(frame)
                #myKnob.setValueAt(myKnob.getValueAt(frame)[0],frame,0)
                #myKnob.setValueAt(myKnob.getValueAt(frame)[1],frame,1)
                reduce = True
            print frame, delta
        else:
            reduce = False

'''================================================================================
; Function:             Solve2DTransform():
; Description:          Used to solve the trackers in a 2dtracker node.
;                           
; Note(s):              _method  #0 = Local, 1 = Median, 2 = Average
;=================================================================================='''
def CalculatePositionDelta(_method,_refpointList,temp_pos=[0,0]):
  if _method == 0: #If we use local interpolation
    newOffset = GetNearestPoints([0,temp_pos[0],temp_pos[1]],_refpointList)
    _x3 = newOffset[0]
    _y3 = newOffset[1]

  elif _method == 1: #If we use global median interpolation
    xlist = [] #Init the lists
    ylist = []
    for items in _refpointList:
      xlist.append(float(items[1][1])-float(items[0][1])) #Add the motion delta to the list
      ylist.append(float(items[1][2])-float(items[0][2]))        
    _x3 = median(xlist) #Calculate median
    _y3 = median(ylist)

  else: #If we use global average interpolcation
    _x3 = 0 #Init the value
    _y3 = 0
    for items in _refpointList:
      _x3 += float(items[1][1])-float(items[0][1]) #Calculate motion delta
      _y3 += float(items[1][2])-float(items[0][2])
    _x3 = _x3/(len(_refpointList)+0.00001) #Devide by item cound to get average
    _y3 = _y3/(len(_refpointList)+0.00001) 
  return [_x3,_y3]



'''

thisFrame = nuke.frame()
myNode =nuke.toNode("Transform15")
myKnob = myNode["translate"]

animationsX = myKnob.animation(0) #X-axis animations
animationsY = myKnob.animation(1) #Y-axis animations
animationList = [] #List to contain the animationnlist

preProcessList = [] 
postProcessList = [] 
for x,keys in enumerate(animationsX.keys()):
    if keys.x<thisFrame:
        preProcessList.append([keys.x,keys.y,animationsY.keys()[x].y])
    else:
        postProcessList.append([keys.x,keys.y,animationsY.keys()[x].y])  
print preProcessList
print postProcessList



'''
'''================================================================================
; Function:             Solve2DTransform():
; Description:          Used to solve the trackers in a 2dtracker node.
;                           
; Note(s):              N/A
;=================================================================================='''
def Solve2DTransform(_node):
  global RangeKeeper
  #Define Variables
  solve_method = int(nuke.thisNode().knob("AssistType").getValue()) #0 = Local, 1 = Median, 2 = Average
  frameForRef = RangeKeeper.frameForRef
  StartFrame = RangeKeeper.StartFrame
  EndFrame = RangeKeeper.EndFrame
  myNode = _node
  myKnob = myNode.knob("translate")
  myKnobCenter = myNode.knob("center")
  useExsistingKeyframes = True

  #Set some initial defaults
  init_pos = [0,0]
  center_pos = [0,0]
  temp_pos = [0,0]
  _xy = [0,0]
  frameindex = 0
  #Read data from the knobs
  PointData = GrabListData()
  init_pos = myKnob.getValue()
  center_pos = myKnobCenter.getValue()

  if useExsistingKeyframes:
    animationsX = myKnob.animation(0) #X-axis animations
    animationsY = myKnob.animation(1) #Y-axis animations
    if not animationsY or not animationsX:
      useExsistingKeyframes = 0
    else:
      preProcessList = []   #Initialize array
      postProcessList = []  #Initialize array
      for x,keys in enumerate(animationsX.keys()):
          if keys.x<frameForRef: #If the item is below the refframe it should be processed in the back process
              preProcessList.append([keys.x,keys.y,animationsY.keys()[x].y])
          else:
              postProcessList.append([keys.x,keys.y,animationsY.keys()[x].y])  
      frameindex = len(preProcessList)-1 #The next keyframe to compare with is the last in the stack when going backwards

  #Clear animation
  if not RangeKeeper.appendAnimation:
    myKnob.clearAnimated() #Only if overwrite!!
    myKnob.setAnimated(0)
  myKnob.setAnimated(1)

  #Re-write the initial position
  myKnob.setValueAt(init_pos[0],frameForRef,0)
  myKnob.setValueAt(init_pos[1],frameForRef,1)

  #Substract the center position of the transform node
  init_pos[0] += center_pos[0]
  init_pos[1] += center_pos[1]

  temp_pos = init_pos


 


  #--------------------------
  #Resolve backwards [<-----]
  for frame in reversed(range(StartFrame,frameForRef)):
    RefPointList = GetAnimtionList(PointData[0],PointData[1],frame,True)
    _xy = CalculatePositionDelta(solve_method,RefPointList,temp_pos)
    temp_pos = [temp_pos[0]+_xy[0],temp_pos[1]+_xy[1]] #Add our calculated motion delta to the current position
    myKnob.setValueAt(temp_pos[0]-center_pos[0],frame,0) #Add a keyframe with the values
    myKnob.setValueAt(temp_pos[1]-center_pos[1],frame,1)
    if frameindex >=0 and useExsistingKeyframes:
      if frame == preProcessList[frameindex][0]:
        tempX = preProcessList[frameindex][1]
        tempY = preProcessList[frameindex][2]
        print "Reached keyframe",preProcessList[frameindex][0],preProcessList[frameindex][1],preProcessList[frameindex][2]
        print "Dif:", tempX-(temp_pos[0]-center_pos[0]),tempY-(temp_pos[1]-center_pos[1])
        frameindex -= 1

  #-------------------------
  #Resolve forwards [----->]
  temp_pos = init_pos
  for frame in range(frameForRef,EndFrame):
    RefPointList = GetAnimtionList(PointData[0],PointData[1],frame)
    _xy = CalculatePositionDelta(solve_method,RefPointList,temp_pos)
    temp_pos = [temp_pos[0]+_xy[0],temp_pos[1]+_xy[1]] #Add our calculated motion delta to the current position
    myKnob.setValueAt(temp_pos[0]-center_pos[0],frame+1,0)
    myKnob.setValueAt(temp_pos[1]-center_pos[1],frame+1,1)

'''================================================================================
; Function:             SolveCornerpin():
; Description:          Used to solve the points of a cornerpin
;                           
; Note(s):              N/A
;=================================================================================='''
def SolveCornerpin(_node):
  #Define Variables
  solve_method = int(nuke.thisNode().knob("AssistType").getValue()) #0 = Local, 1 = Median, 2 = Average
  frameForRef = nuke.frame()
  StartFrame = int(nuke.thisNode().knob("InputFrom").value())
  EndFrame = int(nuke.thisNode().knob("InputTo").value())
  myNode = _node
  myKnob = myNode.knob("translate")
  myKnobCenter = myNode.knob("center")

  #Set some initial defaults
  init_pos = [0,0]
  center_pos = [0,0]
  temp_pos = [0,0]
  _xy = [0,0]

  #Read data from the knobs
  knobs = [myNode['to1'],myNode['to2'],myNode['to3'],myNode['to4']]
  RefPointList = []
  for myKnob in knobs:
    init_pos = myKnob.getValue()
    RefPointList.append([init_pos,myKnob])
    myKnob.clearAnimated() #Only if overwrite!!
    myKnob.setAnimated(0)
    myKnob.setAnimated(1)   
    myKnob.setValueAt(init_pos[0],frameForRef,0)
    myKnob.setValueAt(init_pos[1],frameForRef,1)


  PointData = GrabListData()

  for item in RefPointList:
    temp_pos = item[0]
    myKnob = item[1]
    #--------------------------
    #Resolve backwards [<-----]
    for frame in reversed(range(StartFrame,frameForRef)):
      RefPointList = GetAnimtionList(PointData[0],PointData[1],frame,True)
      _xy = CalculatePositionDelta(solve_method,RefPointList,temp_pos)
      temp_pos = [temp_pos[0]+_xy[0],temp_pos[1]+_xy[1]] #Add our calculated motion delta to the current position
      myKnob.setValueAt(temp_pos[0]-center_pos[0],frame,0) #Add a keyframe with the values
      myKnob.setValueAt(temp_pos[1]-center_pos[1],frame,1)

    #-------------------------
    #Resolve forwards [----->]
    temp_pos = item[0]
    for frame in range(frameForRef,EndFrame):
      RefPointList = GetAnimtionList(PointData[0],PointData[1],frame)
      _xy = CalculatePositionDelta(solve_method,RefPointList,temp_pos)
      temp_pos = [temp_pos[0]+_xy[0],temp_pos[1]+_xy[1]] #Add our calculated motion delta to the current position
      myKnob.setValueAt(temp_pos[0]-center_pos[0],frame+1,0)
      myKnob.setValueAt(temp_pos[1]-center_pos[1],frame+1,1)

'''================================================================================
; Function:             SolveCurves():
; Description:          Used to solve the curves knobs (like roto, rotopaint and splinewarps)
;                           
; Note(s):              N/A
;=================================================================================='''
def SolveCurves(_node,_isSplineWarp=False):
  #Define Variables
  solve_method = int(nuke.thisNode().knob("AssistType").getValue()) #0 = Local, 1 = Median, 2 = Average
  frameForRef = nuke.frame()
  StartFrame = int(nuke.thisNode().knob("InputFrom").value())
  EndFrame = int(nuke.thisNode().knob("InputTo").value())
  myNode = _node
  myKnob = myNode.knob("translate")
  myKnobCenter = myNode.knob("center")

  #Set some initial defaults
  init_pos = [0,0]
  center_pos = [0,0]
  temp_pos = [0,0]
  _xy = [0,0]

  #Read data from the knobs

  RefPointListInt=[]
  for item in _node["curves"].getSelected(): #Only apply to selected roto items
      for subitem in item:
        try:
          RefPointListInt.append([subitem.center.getPosition(frameForRef)[0],subitem.center.getPosition(frameForRef)[1],subitem.center])  
        except:
          RefPointListInt.append([subitem.getPosition(frameForRef)[0],subitem.getPosition(frameForRef)[1],subitem])
  
  PointData = GrabListData()

  for item in RefPointListInt:
    temp_pos = [item[0],item[1]]
    print "tempbos:",temp_pos
    centerPoint = item[2]
    #--------------------------
    #Resolve backwards [<-----]
    for frame in reversed(range(StartFrame,frameForRef)):
      RefPointList = GetAnimtionList(PointData[0],PointData[1],frame,True)
      _xy = CalculatePositionDelta(solve_method,RefPointList,temp_pos)
      temp_pos = [temp_pos[0]+_xy[0],temp_pos[1]+_xy[1]] #Add our calculated motion delta to the current position
      centerPoint.addPositionKey(frame,[temp_pos[0],temp_pos[1] ]) #Add a keyframe with the values

    #-------------------------
    #Resolve forwards [----->]
    temp_pos = [item[0],item[1]]
    for frame in range(frameForRef,EndFrame):
      RefPointList = GetAnimtionList(PointData[0],PointData[1],frame)
      _xy = CalculatePositionDelta(solve_method,RefPointList,temp_pos)
      temp_pos = [temp_pos[0]+_xy[0],temp_pos[1]+_xy[1]] #Add our calculated motion delta to the current position
      centerPoint.addPositionKey(frame+1,[temp_pos[0],temp_pos[1] ]) #Add a keyframe with the values




'''================================================================================
; Function:             Solve2DTracker():
; Description:          Used to solve the trackers in a 2dtracker node.
;                           
; Note(s):              N/A
;=================================================================================='''
def Solve2DTracker(_node):
  #Define Variables
  solve_method = int(nuke.thisNode().knob("AssistType").getValue()) #0 = Local, 1 = Median, 2 = Average
  frameForRef = nuke.frame()
  StartFrame = int(nuke.thisNode().knob("InputFrom").value())
  EndFrame = int(nuke.thisNode().knob("InputTo").value())

  #Grap the number of trackers.
  n_tracks = int(_node["tracks"].toScript().split(" ")[3])

  #Constants etc.
  numColumns = 31
  colTrackX = 2
  colTrackY = 3
  RefPointList = []

  for x in range(0,n_tracks):
    track_a = [float(_node.knob("tracks").getValue(numColumns*x + colTrackX)),float(_node.knob("tracks").getValue(numColumns*x + colTrackY))]
    RefPointList.append(track_a)
  print "the ref point list:",RefPointList

  #Grap data from the camera tracker and convert it into a format we can use.
  PointData = GrabListData()

  print "--Initializing Main Loop--"
  trackIdx = 0
  for item in RefPointList:
    temp_pos = item
    #--------------------------
    #Resolve backwards [<-----]
    for frame in reversed(range(StartFrame,frameForRef)):
      RefPointList = GetAnimtionList(PointData[0],PointData[1],frame,True)
      _xy = CalculatePositionDelta(solve_method,RefPointList,temp_pos)
      temp_pos = [temp_pos[0]+_xy[0],temp_pos[1]+_xy[1]] #Add our calculated motion delta to the current position
      _node.knob("tracks").setValueAt(temp_pos[0],frame,numColumns*trackIdx + colTrackX)
      _node.knob("tracks").setValueAt(temp_pos[1],frame,numColumns*trackIdx + colTrackY)   

    #-------------------------
    #Resolve forwards [----->]
    temp_pos = item
    for frame in range(frameForRef,EndFrame):
      RefPointList = GetAnimtionList(PointData[0],PointData[1],frame)
      _xy = CalculatePositionDelta(solve_method,RefPointList,temp_pos)
      temp_pos = [temp_pos[0]+_xy[0],temp_pos[1]+_xy[1]] #Add our calculated motion delta to the current position
      _node.knob("tracks").setValueAt(temp_pos[0],frame+1,numColumns*trackIdx + colTrackX)
      _node.knob("tracks").setValueAt(temp_pos[1],frame+1,numColumns*trackIdx + colTrackY)   
    trackIdx += 1




def Initializer(_method):
  global RangeKeeper
  RangeKeeper = rangeKeeper(_method)
  ResolveSelectedNodes()


'''================================================================================
; Function:             ResolveSelectedNodes():
; Description:          Used to find what functions to run for the given nodes.
;                           
; Note(s):              N/A
;=================================================================================='''
def ResolveSelectedNodes():
  frameForRef = int(nuke.thisNode().knob("RefrenceFrameInput").value()) #Not used here... yet
  StartFrame = int(nuke.thisNode().knob("InputFrom").value())
  EndFrame = int(nuke.thisNode().knob("InputTo").value())
  selectedNodes = nuke.root().selectedNodes()
  sucess = False
  for item in selectedNodes:
    itemclass = item.Class()
    if itemclass == "CornerPin2D":
      sucess = True
      SolveCornerpin(item)
      print "Cornerpin"

    elif itemclass == "Transform" or itemclass == "TransformMasked":
      sucess = True
      Solve2DTransform(item)
      print "Transform"

    elif itemclass == "Roto" or itemclass == "RotoPaint":
      sucess = True
      if nuke.thisNode().knob("assist_rototransform").value():
        Solve2DTransform(item)
      else:
        SolveCurves(item)
      print "roto or paint"

    elif itemclass == "SplineWarp3":
      sucess = True
      SolveCurves(item,True)
      print "SplineWarp3"

    elif itemclass == "Tracker4":
      sucess = True
      Solve2DTracker(item)
      print "Tracker"

    else:
      print "selected node not supported:",itemclass
  if not sucess:
    nuke.message("Please select a assistable node in the nodegraph.")

'''================================================================================
; Function:             StickIT():
; Description:          Used to solve the base build-in warping module
;                           
; Note(s):              N/A
;=================================================================================='''
def StickIT():
  #Define Variables
  frameForRef = int(nuke.thisNode().knob("RefrenceFrameInput").value())
  StartFrame = int(nuke.thisNode().knob("InputFrom").value())
  EndFrame = int(nuke.thisNode().knob("InputTo").value())

  if frameForRef > EndFrame or frameForRef < StartFrame:
    nuke.message("You must set a reference frame inside the active range")
  else:
    taskB = nuke.ProgressTask('Calculating Solve, please wait...') 

    NodePin = nuke.toNode("si_sw") #change this to your tracker node!

    #Grap data from the camera tracker and convert it into a format we can use.
    PointData = GrabListData()

    #03: Get a set of reference points. This is the points we want to move.
    RefPointList = GetAnimtionList(PointData[0],PointData[1],frameForRef,False,True)
    #04: Go through all of the frames and triangulate best points to move the refpoints with.
    start = time.clock()

    finalAnimation = []
    for item in RefPointList:
      zx =  item[0][1]
      zy =  item[0][2]
      tempAnimation = []
      tempAnimation.append([frameForRef,item[0][1],item[0][2]]) #Add a keyframe on the reference frame
      #Now start from the ref frame and move back
      for frame in reversed(range(StartFrame,frameForRef)):
          newOffset = GetNearestPoints(item[0],GetAnimtionList(PointData[0],PointData[1],frame,True))
          tempAnimation.append([frame,item[0][1]+newOffset[0],item[0][2]+newOffset[1]])
          item[0][1] = item[0][1]+newOffset[0]
          item[0][2] = item[0][2]+newOffset[1]
      #Now start from the ref frame and move forward
      for frame in range(frameForRef,EndFrame):
          newOffset = GetNearestPoints([0,zx,zy],GetAnimtionList(PointData[0],PointData[1],frame))
          tempAnimation.append([frame+1,zx+newOffset[0],zy+newOffset[1]])
          zx = zx+newOffset[0]
          zy = zy+newOffset[1]
      #Now add the animation created to the animation list
      finalAnimation.append(sorted(tempAnimation)) 

    #print finalAnimation
    end = time.clock()
    print "%.2gs" % (end-start)
    CreateWarpPinPair(NodePin,finalAnimation,frameForRef)
    del(taskB)


#GLOBALS:

RangeKeeper = 0