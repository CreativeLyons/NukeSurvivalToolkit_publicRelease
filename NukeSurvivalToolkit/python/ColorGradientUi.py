#(C) Copyright Mads Hagbarth Damsbo 2016 -- Not for redistribution.
#Version 1.1
import sys, math, os
import nuke,nukescripts
try:
    import PySide.QtGui as QtGui
    import PySide.QtCore as QtCore
    from PySide.QtGui import *
    from PySide.QtCore import *
except:
    import h_Qt
    from h_Qt import QtGui
    from h_Qt import QtCore
    from h_Qt.QtGui import *
    from h_Qt.QtCore import *
from nukescripts import panels
import datetime
import operator

try:
	import ConfigParser
except:
	import configparser as ConfigParser
PresetsFile = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),'presets/GradientPresets.cfg')
config = ConfigParser.RawConfigParser()
config.read(PresetsFile)


#nuke.toNode(inputNode.name()+".HueVsHue").knob("lut").editCurve("amount",myCurve.replace("amount","curve")[10:-1])



#Projekt Variabler


'''Constant
Linear
Smooth
Catmull-Rom
Horizontal
'''



class SectionPanel(nukescripts.PythonPanel):
    def __init__(self):
        nukescripts.PythonPanel.__init__(self, 'Add Custom Gradient Preset')
        self.category = nuke.String_Knob('cat', 'Preset Category')
        self.name = nuke.String_Knob('name', 'Preset Name')
        self.addKnob(self.category)
        self.addKnob(self.name)


def saveTemplate(_curves):
	global PresetsFile
	global config
	#print config.get('Section1', 'value')
	p = SectionPanel()
	if p.showModalDialog():
		try:
			config.add_section(p.category.value())
		except:
			pass
		config.read(PresetsFile)
		config.set(p.category.value(), p.name.value(),_curves)

		# Writing our configuration file to 'example.cfg'
		with open(PresetsFile, 'wb') as configfile:
		    config.write(configfile)
		config.read(PresetsFile)



#This function is used to set the curve of a color lookup node.
#The input is a node and a (sorted) list of colors formated:
#[[R,G,B,A,INDEX],[...]]
#Index being the X offset
def setColorCurve(node,colorlist,parent,_object):
	#Interpolation = parent['Interpolation'].value()
	Interpolation = _object.interpolationMenu.currentText()
	parent['Interpolation'].setValue(_object.interpolationMenu.currentIndex ())

	if Interpolation == "Constant":
		interp = "K"
		interpB = "K"
	elif Interpolation == "Linear":
		interp = "L"
		interpB = "L"
	elif Interpolation == "Smooth":
		interp = "Z"
		interpB = "Z"
	elif Interpolation == "Catmull-Rom":
		interp = "R"
		interpB = "R"
	elif Interpolation == "Horizontal":
		interp = "H"
		interpB = "s0"
	else: #"Default // Cubic "
		interp = "C"
		interpB = "C"

	curveR = 'curve '
	curveG = 'curve '
	curveB = 'curve '
	curveA = 'curve '
	for x,item in enumerate(colorlist):
		if x == len(colorlist)-1:
			curveR += "%s x%s %s %s" %("L",item[-1],item[0],interpB)
			curveG += "%s x%s %s %s" %("L",item[-1],item[1],interpB)
			curveB += "%s x%s %s %s" %("L",item[-1],item[2],interpB)
			curveA += "%s x%s %s %s" %("L",item[-1],item[3],interpB)
		elif x==0:
			curveR += "%s x%s %s" %(interpB,item[-1],item[0])
			curveG += "%s x%s %s" %(interpB,item[-1],item[1])
			curveB += "%s x%s %s" %(interpB,item[-1],item[2])
			curveA += "%s x%s %s" %(interpB,item[-1],item[3])
		else:
			curveR += "%s x%s %s" %(interp,item[-1],item[0])
			curveG += "%s x%s %s" %(interp,item[-1],item[1])
			curveB += "%s x%s %s" %(interp,item[-1],item[2])
			curveA += "%s x%s %s" %(interp,item[-1],item[3])
	node['lut'].editCurve("red",curveR)
	node['lut'].editCurve("green",curveG)
	node['lut'].editCurve("blue",curveB)
	node['lut'].editCurve("alpha",curveA)
	node['chek'].execute() #Force Update the node.


def LoadCurveDataX(_curves):
	#Warning, this was specifically designed to only work with uniform pairs. Will not work if there are no pairs!
	curves = _curves.splitlines()
	red_split = curves[1][10:-1].split(" ")
	green_split = curves[2][12:-1].split(" ")
	blue_split = curves[3][11:-1].split(" ")
	alpha_split = curves[4][12:-1].split(" ")
	Interpolation = ""
	Index = -1.0
	colorlist = []
	for x,item in enumerate(red_split):
		if item[0:1].isdigit():
			if Index == -1.0: #First and lasty entry does sometimes not have a index.
				if x <= 2:
					Index = 0
				else:
					Index = 1
			colorlist.append([float(red_split[x]),float(green_split[x]),float(blue_split[x]),float(alpha_split[x]),Interpolation,float(Index)])
			Interpolation = ""
			Index = -1.0
		else:
			if item[1:]:
				Index = item[1:]
			elif item[0:1] == "k":
				Index = 0
			else:
 				Interpolation = item
	return colorlist


class ColorValue:
	def __init__(self):
		self.position = 0 #Position is a value between 0 and 1
		self.color = QColor.fromRgbF(1, 1, 1, 1)
		self.distance = 1
		self.selected = False

class GradientWidget(QtGui.QWidget):
	def __init__(self, parent=None, mainDiameter=138, outerRingWidth=10,my_node="None"):
		QtGui.QWidget.__init__(self, parent)
		self._parent = parent
		self.myTimer = QtCore.QTime() #Used to limit the trigger times of mousemove events
		self.colorLookupNode = my_node.node("ColorLookup1")
		self.thisNode = my_node
		self.colorList = [] #Used to store all the colors
		self.selectedHandle = False
		self.selectedHandels = []
		# this is the pixel diameter of the actual color wheel, without the extra decorations drawn as part of this widget
		#self.testPointsSetup()
		self.initCurve()

	def initCurve(self,fromNode=True,_data=""):  #This function is used when you load the toolset/gizmo. It will fetch data from the colorlookup node
		self.colorList = []
		if fromNode: #Should we read the data from a node or some input
			colorlist = LoadCurveDataX(self.colorLookupNode["lut"].toScript())
		else:
			colorlist = LoadCurveDataX(_data)
		if len(colorlist) <= 1:
			self.testPointsSetup()
		else:
			for item in colorlist:
				ReturnItem = ColorValue()
				ReturnItem.position = item[-1]
				ReturnItem.color = QColor.fromRgbF(item[0], item[1], item[2], item[3])
				self.colorList.append(ReturnItem)
				self._update()

	def sliderUpdate(self,_color):
		for item in self.colorList:
			if item.selected:
				item.color = _color
				self._update()
				break

	def _update(self): #A function that is being called when changes have been made that needs to reflect in the UI
		self.colorNodeUpdate()
		self.repaint()

	def paintEvent(self, evt):
		painter = QtGui.QPainter(self)
		painter.setRenderHint(QtGui.QPainter.Antialiasing)
		#painter.begin(self)
		self.drawRectangles(painter)
		#painter.end()

	def setSelection(self,_item):
		for item in self.colorList:
			item.selected = False
		_item.selected = True
		self._parent.updateSlider(_item.color)
		self._update()

	def testPointsSetup(self): #DEBRICATED!!
		self.colorList.append(ColorValue())
		self.colorList.append(ColorValue())
		self.colorList[1].position = 1
		self.colorList[1].color = QColor.fromRgbF(0, 0, 0, 1)


	def getColorAtOffset(self,posx):

		#Get the points last and next point.
		sorted_x = sorted(self.colorList,key=operator.attrgetter('position'))
		current_index = len(sorted_x)
		for x,item in enumerate(sorted_x):
			if posx > item.position:
				pass
			else:
				current_index = x
				break

		if current_index == 0:
			itemA = sorted_x[0]
			itemB = sorted_x[0]
		elif current_index == len(sorted_x):
			itemA = sorted_x[-1]
			itemB = sorted_x[-1]
		else:
			itemA = sorted_x[current_index-1]
			itemB = sorted_x[current_index]

		#Calcualte how far between the two we are and get a color value
		_dist = itemB.position-itemA.position
		_distP = posx-itemA.position
		if _dist == 0.0:
			_distT = 0.0
		else:
			_distT = _distP/_dist
		_red = _distT*itemA.color.getRgbF()[0] + (1-_distT)*itemB.color.getRgbF()[0]
		_green = _distT*itemA.color.getRgbF()[1] + (1-_distT)*itemB.color.getRgbF()[1]
		_blue = _distT*itemA.color.getRgbF()[2] + (1-_distT)*itemB.color.getRgbF()[2]
		_alpha = _distT*itemA.color.getRgbF()[3] + (1-_distT)*itemB.color.getRgbF()[3]
		return QColor.fromRgbF(_green, _blue,_alpha,_red).rgba() #MUST BE A NUKE BUG THAT ITS GREEN BLUE ALPHA RED!!!



	def drawRectangles(self, painter):
		self.widget_offset = 10
		self.widget_width = self.width()-(self.widget_offset*2)
		self.widget_height = 40
		self.widget_top = 15
		self.handle_width = 7

		color = QtGui.QColor(0, 0, 0)
		color.setNamedColor('#008080')
		painter.setPen(color)
		gradient = QLinearGradient(self.widget_width+(self.widget_offset*2), 0, 0, 0)

		painter.setBrush(Qt.CrossPattern)
		painter.drawRect(self.widget_offset, self.widget_top+10, self.widget_width-1, self.widget_height)

		for item in self.colorList:
			if item.selected:
				painter.drawEllipse(QtCore.QPoint((item.position*self.widget_width)+self.widget_offset,self.widget_top) , 10, 10 ) #DRAW THE OUTER BLACK CIRCLE
			gradient.setColorAt(1-item.position, item.color)
			painter.setBrush(item.color)
			painter.drawEllipse(QtCore.QPoint((item.position*self.widget_width)+self.widget_offset,self.widget_top) , 7, 7 ) #DRAW THE OUTER BLACK CIRCLE
			painter.drawRect((item.position*self.widget_width)-self.handle_width+self.widget_offset,self.widget_top+15+self.widget_height , self.handle_width*2, self.handle_width*2 ) #DRAW THE OUTER BLACK CIRCLE

		painter.setBrush(gradient)

		painter.drawRect(self.widget_offset, self.widget_top+10, self.widget_width-1, self.widget_height)


	def getNearestHandle(self,posx,posy,dc=False):
		for item in self.colorList:
			item.distance = abs(posx-item.position)
		sorted_x = sorted(self.colorList,key=operator.attrgetter('distance'))
		if sorted_x[0].distance <= self.handle_width/float(self.widget_width):
			if abs(posy-(self.widget_top)) <= self.handle_width: #The Main Color Handle
				if dc:
					#This part is triggered when you click a allready exsisting color chip (hence you want to edit the color)
					_tempcol = sorted_x[0].color.getRgbF()
					V = nuke.getColor(QColor.fromRgbF(_tempcol[1], _tempcol[2],_tempcol[3],_tempcol[0]).rgba() )
					if V:
						R = (255 & V >> 24) / 255.0
						G = (255 & V >> 16) / 255.0
						B = (255 & V >> 8) / 255.0
						A = (255 & V >> 0) / 255.0
						sorted_x[0].color = QColor.fromRgbF(R, G, B, A)
						self._update()
				self.setSelection(sorted_x[0])
				return sorted_x[0]
			elif abs(posy-(self.widget_top+15+self.widget_height+self.handle_width)) <= self.handle_width: #The Deletion Handle
				self.colorList.remove(sorted_x[0])
				self._update()
				return False
			else:
				return False
		else:
			if dc: #If the user double clicks, we add a new handle
				#This part is triggered when you click to create a new color chip
				ReturnItem = ColorValue()
				ReturnItem.position = posx
				#print self.getColorAtOffset(posx)
				V = nuke.getColor(self.getColorAtOffset(posx))
				if V:
					R = (255 & V >> 24) / 255.0
					G = (255 & V >> 16) / 255.0
					B = (255 & V >> 8) / 255.0
					A = (255 & V >> 0) / 255.0
					ReturnItem.color = QColor.fromRgbF(R, G, B, A)
				self.colorList.append(ReturnItem)
				self._update()
				self.setSelection(ReturnItem)
				return ReturnItem
			else:
				return False


	def mousePressEvent(self, evt):
		self.myTimer.start()
		self.selectedHandle = self.getNearestHandle(max(0,min(1,(evt.x()-(self.widget_offset))/float(self.widget_width))),evt.y())
		if not self.selectedHandle:
			#We should not do anything...
			pass
		else:
			pass

	def mouseReleaseEvent(self,evt):
		if not self.selectedHandle:
			#We should not do anything...
			pass
		else:
			self.colorNodeUpdate()

	def mouseDoubleClickEvent(self, evt):
		self.myTimer.start()
		self.selectedHandle = self.getNearestHandle(max(0,min(1,(evt.x()-(self.widget_offset))/float(self.widget_width))),evt.y(),True)
		if not self.selectedHandle:
			#We should not do anything...
			pass

	def mouseMoveEvent(self, evt):
		self.setstate = 1
		if not self.selectedHandle:
			pass
		else:
			nMilliseconds = self.myTimer.elapsed()
			if nMilliseconds < 1:
				pass
			else:
				self.selectedHandle.position = max(0,min(1,(evt.x()-(self.widget_offset))/float(self.widget_width)))
				self._update()
				self.myTimer.restart()

	def colorNodeUpdate(self):
		colorList = []
		for item in self.colorList:
			color = item.color.getRgbF()
			colorList.append([color[0],color[1],color[2],color[3],item.position])
		colorList = sorted(colorList, key=lambda x: x[-1], reverse=False)
		setColorCurve(self.colorLookupNode,colorList,self.thisNode,self._parent)



#The labels used for the presets tab
class GradientLabel(QtGui.QLabel):
	masterSignal = QtCore.Signal(object)
	def __init__(self, _gradient="",name=""):
		super(GradientLabel, self).__init__()
		self.setFixedHeight(30)
		self.GradientData = _gradient
		self.Name = name
		self.colorList = []
		self.ExtractColorData()

	def mouseReleaseEvent(self, ev):
		self.masterSignal.emit(self.GradientData)

	def ExtractColorData(self):
		colorlist = LoadCurveDataX(self.GradientData)
		for item in colorlist:
			ReturnItem = ColorValue()
			ReturnItem.position = item[-1]
			ReturnItem.color = QColor.fromRgbF(item[0], item[1], item[2], item[3])
			self.colorList.append(ReturnItem)

	def paintEvent(self, evt):
		painter = QtGui.QPainter(self)
		painter.setRenderHint(QtGui.QPainter.Antialiasing)
		#painter.begin(self)
		self.drawRectangles(painter)
		#painter.end()

	def drawRectangles(self, painter):
		self.widget_offset = 0
		self.widget_width = self.width()-(self.widget_offset*2)
		self.widget_height = 28
		self.widget_top = 0

		gradient = QLinearGradient(self.widget_width+(self.widget_offset*2), 0, 0, 0)
		for item in self.colorList:
			gradient.setColorAt(1-item.position, item.color)
		painter.setBrush(gradient)
		painter.drawRect(self.widget_offset, self.widget_top, self.widget_width, self.widget_height)




#Basic toolbutton with a additional event filter.
class MyToolButton(QtGui.QToolButton):
	def __init__(self, *args):
		QtGui.QToolButton.__init__(self, *args)
	def eventFilter(self, menu, event):
		if event.type() == QtCore.QEvent.MouseButtonRelease:
			if self.underMouse():
				menu.menu().close()
				return True
		return False


class Example(QtGui.QWidget):
	def __init__(self, parent=None,myNode="none"):
		global config
		QtGui.QWidget.__init__(self, None)
		self.setGeometry(900, 900, 800, 600)
		#self.setWindowTitle('ColorBars')
		self.baseNode = myNode
		self.setMinimumHeight(160)
		self.setMinimumWidth(200)

		self.interpolationLabel = QLabel("Interpolation")
		self.interpolationMenu = QComboBox()
		self.interpolationMenu.addItem("Constant")
		self.interpolationMenu.addItem("Linear")
		self.interpolationMenu.addItem("Smooth")
		self.interpolationMenu.addItem("Catmull-Rom")
		self.interpolationMenu.addItem("Cubic")
		self.interpolationMenu.addItem("Horizontal")
		self.interpolationMenu.setCurrentIndex(int(myNode['Interpolation'].getValue()))

		self.presetMenu = MyToolButton()
		self.presetMenu.setText("Gradient Presets  ")
		self.menu = QtGui.QMenu('Presets')

		self.UpdatePresetList()

		self.presetMenu.setMenu(self.menu)

		self.presetMenu.installEventFilter(self.presetMenu)
		self.gradientUI = GradientWidget(self, 138, 10,myNode)
		self.hue = QSlider(Qt.Horizontal)
		self.sat = QSlider(Qt.Horizontal)
		self.lum = QSlider(Qt.Horizontal)
		self.interpolationMenu.currentIndexChanged.connect(self.gradientUI.colorNodeUpdate)
		self.hue.valueChanged.connect(self.sliderUpdate)
		self.sat.valueChanged.connect(self.sliderUpdate)
		self.lum.valueChanged.connect(self.sliderUpdate)
		self.hue.setRange(0,255)
		self.sat.setRange(0,255)
		self.lum.setRange(0,255)

		layout = QtGui.QGridLayout()
		sub_layout = QtGui.QHBoxLayout()
		dropdown_layout = QtGui.QHBoxLayout()
		dropdown_layout.addWidget(self.presetMenu)
		dropdown_layout.addWidget(self.interpolationLabel)
		dropdown_layout.addWidget(self.interpolationMenu)
		dropdown_layout.addStretch()
		layout.addLayout(dropdown_layout,0,0)
		layout.addWidget(self.gradientUI,1,0)
		layout.addLayout(sub_layout,2,0)
		sub_layout.addWidget(self.hue)
		sub_layout.addWidget(self.sat)
		sub_layout.addWidget(self.lum)
		#layout.setRowStretch(0,0)
		self.setLayout(layout)
		self.UpdateStylesheet()
		self.show()

	@QtCore.Slot(object)
	def gradientClicked(self, values):
		self.gradientUI.initCurve(False,values)

	def addPreset(self):
		saveTemplate(self.baseNode.node("ColorLookup1")["lut"].toScript())
		self.UpdatePresetList()

	def UpdatePresetList(self):
		for item in self.menu.actions():
			self.menu.removeAction(item)
		#Read the presets. Look for all the sections
		config.read(PresetsFile)
		sections = config.sections()
		for section in sections:
			gradients = config.items(section)
			submenu = QtGui.QMenu(section)
			submenu.setMinimumWidth(300)
			self.menu.addMenu(submenu)
			for gradient in gradients:
				qle=GradientLabel(gradient[1],gradient[0])
				qle.masterSignal.connect(self.gradientClicked)
				wac=QtGui.QWidgetAction(submenu)
				wac.setDefaultWidget(qle)
				action=submenu.addAction(wac);

		addAction = QtGui.QAction('+ADD PRESET', self)
		addAction.triggered.connect(self.addPreset)
		self.menu.addAction(addAction)

	def updateSlider(self,_color):
		self.hue.setValue(_color.hsvHueF()*255 )
		self.sat.setValue(_color.hsvSaturationF()*255)
		self.lum.setValue(_color.valueF()*255)


	def sliderUpdate(self):
		self.gradientUI.sliderUpdate(QColor.fromHsvF(self.hue.value()/255.0,self.sat.value()/255.0,self.lum.value()/255.0,1.0))

	def updateValue(self):
		pass

	def UpdateStylesheet(self):
		self.hue.setStyleSheet(self.hue.styleSheet()+"""QSlider::groove:horizontal {
		border: 1px solid #999999;
		height: 8px; /* the groove expands to the size of the slider by default. by giving it a height, it has a fixed size */
		background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
		stop: 0.000 rgb(255, 0, 0),
		stop: 0.167 rgb(255, 255, 0),
		stop: 0.333 rgb(0, 255, 0),
		stop: 0.500 rgb(0, 255, 255),
		stop: 0.667 rgb(0, 0, 255),
		stop: 0.833 rgb(255, 0, 255),
		stop: 1.0 rgb(255, 0, 0));
		margin: 2px 0;
		}
		QSlider::handle:horizontal {
			background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #5f5f5f);
			border: 1px solid #008080;
			width: 18px;
			margin: -2px 0; /* handle is placed by default on the contents rect of the groove. Expand outside the groove */
			border-radius: 3px;
		}""")
		self.sat.setStyleSheet(self.sat.styleSheet()+"""QSlider::groove:horizontal {
		border: 1px solid #999999;
		height: 8px; /* the groove expands to the size of the slider by default. by giving it a height, it has a fixed size */
		background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
		stop: 0.000 rgb(0, 0, 0),
		stop: 1.0 rgb(255, 0, 0));
		margin: 2px 0;
		}
		QSlider::handle:horizontal {
			background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #5f5f5f);
			border: 1px solid #008080;
			width: 18px;
			margin: -2px 0; /* handle is placed by default on the contents rect of the groove. Expand outside the groove */
			border-radius: 3px;
		}""")
		self.lum.setStyleSheet(self.lum.styleSheet()+"""QSlider::groove:horizontal {
		border: 1px solid #999999;
		height: 8px; /* the groove expands to the size of the slider by default. by giving it a height, it has a fixed size */
		background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
		stop: 0.000 rgb(0, 0, 0),
		stop: 1.0 rgb(255, 255, 255));
		margin: 2px 0;
		}
		QSlider::handle:horizontal {
			background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #5f5f5f);
			border: 1px solid #008080;
			width: 18px;
			margin: -2px 0; /* handle is placed by default on the contents rect of the groove. Expand outside the groove */
			border-radius: 3px;
		}""")


class ColorWheelKnob_GRADIENT:
	def __init__( self ):
		self.instance = 0
		return None

	def makeUI( self ):
		self.instance = Example(None,nuke.thisNode())
		return self.instance

defined = 1
