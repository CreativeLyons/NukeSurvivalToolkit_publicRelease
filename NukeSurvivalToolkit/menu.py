#*****************************************************************
#*****************************************************************
# This file will setup the NukeSurvivalToolkit Menu on your Toolbar
# Written by Tony Lyons 09/2020 | www.CreativeLyons.com | www.CompositingMentor.com
#*****************************************************************
#*****************************************************************

import nuke
import sys
import os
import webbrowser
import NST_helper

# This is the prefix being used to customize the gizmo's in this toolkit
prefixNST = "NST_"

# Store the location of this menu.py to help with nuke.nodePaste() which requires a filepath to paste
NST_FolderPath = os.path.dirname(__file__)
NST_helper.NST_FolderPath = NST_FolderPath

# give the name of the help doc .pdf in main folder
NST_helpDoc = "NukeSurvivalToolkit_Documentation_Release_v1.1.0.pdf"

# creating full filepath to the help doc
NST_helpDoc_os_path = os.path.join(NST_FolderPath, NST_helpDoc)
NST_helpDocPath = "file:///{}".format(NST_helpDoc_os_path)


############################################################################################################
############################################################################################################

# Create NukeSurivalToolkit Menu
toolbar = nuke.menu('Nodes')
m = toolbar.addMenu('NukeSurvivalToolkit', icon = "SurvivalToolkit.png")


############################################################################################################
############################################################################################################

# Create Button to Open NukeSurivalToolkit Documentation
def openNSTDocumentation():
    webbrowser.open(NST_helpDocPath)

m.addCommand("Documentation", "openNSTDocumentation()", icon="info_icon.png")

############################################################################################################
############################################################################################################


# Create Image Menu
imageMenu = m.addMenu('Image', icon = 'ToolbarImage.png', index = 10)

imageMenu.addCommand('LabelFromRead TL', "nuke.createNode('{}LabelFromRead')".format(prefixNST), icon="LabelFromRead.png")
############################################################################################################
############################################################################################################

# Create Draw Menu
drawMenu = m.addMenu('Draw', icon = 'ToolbarDraw.png', index = 20)

drawMenu.addCommand('GradMagic TL', "nuke.createNode('{}GradMagic')".format(prefixNST), icon="GradMagic.png")
drawMenu.addCommand('NoiseAdvanced TL', "nuke.createNode('{}NoiseAdvanced')".format(prefixNST), icon="Noise.png")
drawMenu.addCommand('RadialAdvanced TL', "nuke.createNode('{}RadialAdvanced')".format(prefixNST), icon="Radial.png")

drawMenu.addSeparator()

drawMenu.addCommand('WaterLens MJT', "nuke.createNode('{}WaterLens')".format(prefixNST), icon="WaterLens.png")

drawMenu.addSeparator()

drawMenu.addCommand('VoronoiGradient NKPD', "nuke.createNode('{}VoronoiGradient')".format(prefixNST), icon="GradMagic.png")
drawMenu.addCommand('CellNoise NKPD', "nuke.createNode('{}CellNoise')".format(prefixNST), icon="Noise.png")
drawMenu.addCommand('LineTool NKPD', "nuke.createNode('{}LineTool')".format(prefixNST), icon="nukepedia_icon.png")
drawMenu.addCommand('PlotScanline NKPD', "nuke.createNode('{}PlotScanline')".format(prefixNST), icon="nukepedia_icon.png")
drawMenu.addCommand('SliceTool FR', "nuke.createNode('{}SliceTool')".format(prefixNST), icon="Histogram.png")
drawMenu.addCommand('PerspectiveGuide NKPD', "nuke.createNode('{}PerspectiveGuide')".format(prefixNST), icon="nukepedia_icon.png")

drawMenu.addSeparator()

drawMenu.addCommand('DasGrain FH', "nuke.createNode('{}DasGrain')".format(prefixNST), icon="Grain.png")
drawMenu.addCommand('LumaGrain LUMA', "nuke.createNode('{}LumaGrain')".format(prefixNST), icon="nukepedia_icon.png")
drawMenu.addCommand('Grain_Advanced SPIN', "nuke.createNode('{}Grain_Advanced')".format(prefixNST), icon="spin_tools.png")

drawMenu.addSeparator()

drawMenu.addCommand('SpotFlare MHD', "nuke.createNode('{}SpotFlare')".format(prefixNST), icon="Flare.png")
drawMenu.addCommand('FlareSuperStar NKPD', "nuke.createNode('{}FlareSuperStar')".format(prefixNST), icon="nukepedia_icon.png")
drawMenu.addCommand('AutoFlare NKPD', "NST_helper.filepathCreateNode('{}AutoFlare2')".format(prefixNST), icon="Flare.png")

############################################################################################################
############################################################################################################

# Create Time Menu
timeMenu = m.addMenu('Time', icon = 'ToolbarTime.png', index = 30)

timeMenu.addCommand('apLoop AP', 'nuke.createNode("{}apLoop")'.format(prefixNST), icon='apLoop.png')

timeMenu.addSeparator()

timeMenu.addCommand('Looper NKPD', "nuke.createNode('{}Looper')".format(prefixNST), icon="nukepedia_icon.png")
timeMenu.addCommand('FrameMedian MHD', "nuke.createNode('{}FrameMedian')".format(prefixNST), icon="FrameBlend.png")
timeMenu.addCommand('TimeMachine NKPD', "nuke.createNode('{}TimeMachine')".format(prefixNST), icon="nukepedia_icon.png")
timeMenu.addCommand('FrameFiller MJT', "nuke.createNode('{}FrameFiller')".format(prefixNST), icon="FrameFiller.png")

############################################################################################################
############################################################################################################

# Create Channel Menu
channelMenu = m.addMenu('Channel', icon = 'ToolbarChannel.png', index = 40)

channelMenu.addCommand('BinaryAlpha TL', "nuke.createNode('{}BinaryAlpha')".format(prefixNST), icon="BumpBoss.png")
channelMenu.addCommand('ChannelCombiner TL', "nuke.createNode('{}ChannelCombiner')".format(prefixNST), icon="ChannelMerge.png")
channelMenu.addCommand('ChannelControl TL', "nuke.createNode('{}ChannelControl')".format(prefixNST), icon="LayerChannel.png")
channelMenu.addCommand('ChannelCreator TL', "nuke.createNode('{}ChannelCreator')".format(prefixNST), icon="Add.png")
channelMenu.addCommand('InjectMatteChannel TL', "nuke.createNode('{}InjectMatteChannel')".format(prefixNST), icon="ChannelMerge.png")


channelMenu.addSeparator()

channelMenu.addCommand('streamCart MJT', "nuke.createNode('{}streamCart')".format(prefixNST), icon="streamCart.png")
channelMenu.addCommand('renameChannels AG', "nuke.createNode('{}renameChannels')".format(prefixNST), icon="nukepedia_icon.png")


############################################################################################################
############################################################################################################

# Create Color Menu
colorMenu = m.addMenu('Color', icon = 'ToolbarColor.png', index = 50)

colorMenu.addCommand('BlacksMatch TL', "nuke.createNode('{}BlacksMatch')".format(prefixNST), icon="BlacksMatch.png")
colorMenu.addCommand('ColorCopy TL', "nuke.createNode('{}ColorCopy')".format(prefixNST), icon="Crosstalk.png")
colorMenu.addCommand('Contrast TL', "nuke.createNode('{}Contrast')".format(prefixNST), icon="ColorCorrect.png")
colorMenu.addCommand('GradeLayerPass TL', "nuke.createNode('{}GradeLayerPass')".format(prefixNST), icon="Grade.png")
colorMenu.addCommand('HighlightSuppress TL', "nuke.createNode('{}HighlightSuppress')".format(prefixNST), icon="ColorLookup.png")
colorMenu.addCommand('ShadowMult TL', "nuke.createNode('{}ShadowMult')".format(prefixNST), icon="SpotLight.png")
colorMenu.addCommand('WhiteSoftClip TL', "nuke.createNode('{}WhiteSoftClip')".format(prefixNST), icon="SoftClip.png")
colorMenu.addCommand('WhiteBalance TL', "nuke.createNode('{}WhiteBalance')".format(prefixNST), icon="HueShift.png")

colorMenu.addSeparator()

colorMenu.addCommand('apColorSampler AP', 'nuke.createNode("{}ColorSampler")'.format(prefixNST), icon='ColorSampler.png')
colorMenu.addCommand('apVignette AP', 'nuke.createNode("{}apVignette")'.format(prefixNST), icon='apeVignette.png')
colorMenu.addCommand('GammaPlus MJT', "nuke.createNode('{}GammaPlus')".format(prefixNST), icon="GammaPlus.png")

colorMenu.addSeparator()

colorMenu.addCommand('Suppress_RGBCMY SPIN', 'nuke.createNode("{}Suppress_RGBCMY")'.format(prefixNST), icon='spin_tools.png')
colorMenu.addCommand('BiasedSaturation NKPD', "nuke.createNode('{}BiasedSaturation')".format(prefixNST), icon="Saturation.png")
colorMenu.addCommand('HSL_Tool NKPD', "nuke.createNode('{}HSL_Tool')".format(prefixNST), icon="HSVTool.png")

############################################################################################################
############################################################################################################

# Create Filter Menu

filterMenu = m.addMenu('Filter', icon = 'ToolbarFilter.png', index = 60)


glowMenu = filterMenu.addMenu("Glows", icon="Glow.png")

glowMenu.addCommand('apGlow AP', 'nuke.createNode("{}apeGlow")'.format(prefixNST), icon='apGlow.png')
glowMenu.addCommand('ExponGlow TL', 'nuke.createNode("{}ExponGlow")'.format(prefixNST), icon='Glow.png')
glowMenu.addCommand('Glow_Exponential SPIN', 'nuke.createNode("{}Glow_Exponential")'.format(prefixNST), icon="spin_tools.png")
glowMenu.addCommand('bm_OpticalGlow BM', "nuke.createNode('{}bm_OpticalGlow')".format(prefixNST), icon='bm_OpticalGlow_icon.png')

filterMenu.addSeparator()

BlurMenu = filterMenu.addMenu("Blurs", icon="Median.png")

BlurMenu.addCommand('ExponBlurSimple TL', "nuke.createNode('{}ExponBlurSimple')".format(prefixNST), icon="Glow.png")
BlurMenu.addCommand('DirectionalBlur TL', "nuke.createNode('{}DirectionalBlur')".format(prefixNST), icon="DirBlur.png")
BlurMenu.addCommand('iBlur NKPD', "nuke.createNode('{}iBlurU')".format(prefixNST), icon="Blur.png")

filterMenu.addSeparator()

EdgesMenu = filterMenu.addMenu("Edges", icon="FilterErode.png")

EdgesMenu.addCommand('apEdgePush AP', 'nuke.createNode("{}apEdgePush")'.format(prefixNST), icon='apEdgePush.png')
EdgesMenu.addCommand('EdgeDetectAlias TL', "nuke.createNode('{}EdgeDetectAlias')".format(prefixNST), icon="FilterErod.png")
EdgesMenu.addCommand('AntiAliasingFilter AG', "nuke.createNode('{}AntiAliasingFilter')".format(prefixNST), icon="nukepedia_icon.png")
EdgesMenu.addCommand('ErodeSmooth TL', "nuke.createNode('{}ErodeSmooth')".format(prefixNST), icon="FilterErode.png")

EdgesMenu.addCommand('Edge_RimLight AG', "nuke.createNode('{}Edge_RimLight')".format(prefixNST), icon="nukepedia_icon.png")
EdgesMenu.addCommand('EdgeDetectPRO AG', "nuke.createNode('{}EdgeDetectPRO')".format(prefixNST), icon="nukepedia_icon.png")

EdgesMenu.addCommand('Erode_Fine SPIN', "nuke.createNode('{}Erode_Fine')".format(prefixNST), icon="spin_tools.png")
EdgesMenu.addCommand('Edge_Expand SPIN', "nuke.createNode('{}Edge_Expand')".format(prefixNST), icon="spin_tools.png")

EdgesMenu.addCommand('Edge RB', "nuke.createNode('{}Edge')".format(prefixNST), icon="nukepedia_icon.png")
EdgesMenu.addCommand('KillOutline NKPD', "nuke.createNode('{}KillOutline')".format(prefixNST), icon="nukepedia_icon.png")
EdgesMenu.addCommand('ColorSmear NKPD', "nuke.createNode('{}ColorSmear')".format(prefixNST), icon="nukepedia_icon.png")
EdgesMenu.addCommand('EdgeFromAlpha FR', "nuke.createNode('{}EdgeFromAlpha')".format(prefixNST), icon="nukepedia_icon.png")
EdgesMenu.addCommand('VectorExtendEdge NKPD', "nuke.createNode('{}VectorExtendEdge')".format(prefixNST), icon="nukepedia_icon.png")
EdgesMenu.addSeparator()
EdgesMenu.addCommand('FractalBlur NKPD', "nuke.createNode('{}FractalBlur')".format(prefixNST), icon="nukepedia_icon.png")

filterMenu.addSeparator()

distortMenu = filterMenu.addMenu("Distortions", icon="IDistort.png")

distortMenu.addCommand('Glass FR', "nuke.createNode('{}Glass')".format(prefixNST), icon="nukepedia_icon.png")
distortMenu.addCommand('HeatWave NKPD', "nuke.createNode('{}HeatWave')".format(prefixNST), icon="HeatWave_Icon.png")

filterMenu.addSeparator()

filterMenu.addCommand('BeautifulSkin TL', "nuke.createNode('{}BeautifulSkin')".format(prefixNST), icon="Median.png")
filterMenu.addCommand('BlacksExpon TL', "nuke.createNode('{}BlacksExpon')".format(prefixNST), icon="Toe.png")
filterMenu.addCommand('Halation TL', "nuke.createNode('{}Halation')".format(prefixNST), icon="EdgeBlur.png")
filterMenu.addCommand('HighPass TL', "nuke.createNode('{}HighPass')".format(prefixNST), icon="Invert.png")
filterMenu.addCommand('Diffusion TL', "nuke.createNode('{}Diffusion')".format(prefixNST), icon="Spark.png")

filterMenu.addSeparator()

filterMenu.addCommand('LightWrapPro TL', "nuke.createNode('{}LightWrapPro')".format(prefixNST), icon="LightWrap.png")
filterMenu.addCommand('bm_Lightwrap BM', "nuke.createNode('{}bm_Lightwrap')".format(prefixNST), icon="bm_Lightwrap_icon.png")

filterMenu.addSeparator()

filterMenu.addCommand('iConvolve AP', 'nuke.createNode("{}iConvolve")'.format(prefixNST), icon='ap_tools.png')
filterMenu.addCommand('ConvolutionMatrix AG', 'nuke.createNode("{}ConvolutionMatrix")'.format(prefixNST), icon="ColorMatrix.png")

#Add apChroma submenu
apChromaMenu = filterMenu.addMenu("apChroma Tools AP", icon="apChroma.png")
apChromaMenu.addCommand('apChroma AP', 'nuke.createNode("{}apChroma")'.format(prefixNST), icon='apChroma.png')
apChromaMenu.addCommand('apChromaMerge AP', 'nuke.createNode("{}apChromaMergeNew")'.format(prefixNST), icon='apChroma.png')
apChromaMenu.addCommand('apChromaBlur AP', 'nuke.createNode("{}apChromaBlurNew")'.format(prefixNST), icon='apChroma.png')
apChromaMenu.addCommand('apChromaTransform AP', 'nuke.createNode("{}apChromaTransformNew")'.format(prefixNST), icon='apChroma.png')
apChromaMenu.addCommand('apChromaUnpremult AP', 'nuke.createNode("{}apChromaUnpremult")'.format(prefixNST), icon='apChroma.png')
apChromaMenu.addCommand('apChromaPremult AP', 'nuke.createNode("{}apChromaPremult")'.format(prefixNST), icon='apChroma.png')

filterMenu.addSeparator()

filterMenu.addCommand('Chromatik SPIN', "nuke.createNode('{}Chromatik')".format(prefixNST), icon='spin_tools.png')
filterMenu.addCommand('CatsEyeDefocus NKPD', "nuke.createNode('{}CatsEyeDefocus')".format(prefixNST), icon="nukepedia_icon.png")
filterMenu.addCommand('DefocusSwirlyBokeh NKPD', "nuke.createNode('{}DefocusSwirlyBokeh')".format(prefixNST), icon="nukepedia_icon.png")
filterMenu.addCommand('deHaze NKPD', "nuke.createNode('{}deHaze')".format(prefixNST), icon="nukepedia_icon.png")
filterMenu.addCommand('DeflickerVelocity NKPD', "nuke.createNode('{}DeflickerVelocity')".format(prefixNST), icon="nukepedia_icon.png")
filterMenu.addCommand('FillSampler NKPD', "nuke.createNode('{}FillSampler')".format(prefixNST), icon="nukepedia_icon.png")
filterMenu.addCommand('MECfiller NKPD', "nuke.createNode('{}MECfiller')".format(prefixNST), icon="nukepedia_icon.png")

############################################################################################################
############################################################################################################

# Create Keyer Menu
keyerMenu = m.addMenu('Keyer', icon = 'ToolbarKeyer.png', index = 70)

keyerMenu.addCommand('apDespill AP', 'nuke.createNode("{}apDespill")'.format(prefixNST), icon='apDespill.png')
keyerMenu.addCommand('SpillCorrect SPIN', "nuke.createNode('{}Spill_Correct')".format(prefixNST), icon='spin_tools.png')
keyerMenu.addCommand('DespillToColor NKPD', "nuke.createNode('{}DespillToColor')".format(prefixNST), icon="nukepedia_icon.png")

keyerMenu.addSeparator()

keyerMenu.addCommand('AdditiveKeyerPro TL', "nuke.createNode('{}AdditiveKeyerPro')".format(prefixNST), icon="Bilateral.png")
keyerMenu.addCommand('apScreenClean AP', 'nuke.createNode("{}apeScreenClean")'.format(prefixNST), icon='apScreenClean.png')
keyerMenu.addCommand('apScreenGrow AP', 'nuke.createNode("{}apeScreenGrow")'.format(prefixNST), icon='apScreenGrow.png')

keyerMenu.addSeparator()

keyerMenu.addCommand('KeyChew NKPD', "nuke.createNode('{}KeyChew')".format(prefixNST), icon="Keyer.png")
keyerMenu.addCommand('LumaKeyer DR', "nuke.createNode('{}LumaKeyer')".format(prefixNST), icon="Keyer.png")

############################################################################################################
############################################################################################################

# Create Merge Menu
mergeMenu = m.addMenu('Merge', icon = 'ToolbarMerge.png', index = 80)

mergeMenu.addCommand('ContactSheetAuto TL', "nuke.createNode('{}ContactSheetAuto')".format(prefixNST), icon="ContactSheet.png")
mergeMenu.addCommand('KeymixBBox TL', "nuke.createNode('{}KeymixBBox')".format(prefixNST), icon="Keymix.png")
mergeMenu.addCommand('MergeAtmos TL', "nuke.createNode('{}MergeAtmos')".format(prefixNST), icon="PointCloudMesh.png")
mergeMenu.addCommand('MergeBlend TL', "nuke.createNode('{}MergeBlend')".format(prefixNST), icon="Dissolve.png")

mergeMenu.addSeparator()

mergeMenu.addCommand('MergeAll AP', "nuke.createNode('{}MergeAll')".format(prefixNST), icon="Merge.png")

############################################################################################################
############################################################################################################

# Create Transform Menu
transformMenu = m.addMenu('Transform', icon = 'ToolbarTransform.png', index = 90)

transformMenu.addCommand('vector3DMathExpression EL', "nuke.createNode('{}vector3DMathExpression')".format(prefixNST), icon = 'vectorTools.png')
transformMenu.addCommand('Vectors_Direction EL', "nuke.createNode('{}Vectors_Direction')".format(prefixNST), icon = 'vectorTools.png')
transformMenu.addCommand('Vectors_to_Degrees EL', "nuke.createNode('{}Vectors_to_Degrees')".format(prefixNST), icon = 'vectorTools.png')

# Add VectorTracker python file
try:
    nuke.load('{}VectorTracker.py'.format(prefixNST))
except:
    print "Could not load VectorTracker.py"
    pass
transformMenu.addCommand('VectorTracker NKPD', "nuke.createNode('{}VectorTracker.gizmo')".format(prefixNST), icon = 'vectorTools.png')

transformMenu.addSeparator()

transformMenu.addCommand('AutoCropTool TL', "nuke.createNode('{}AutoCropTool')".format(prefixNST), icon="AutoCrop.png")
transformMenu.addCommand('BBoxToFormat TL', "nuke.createNode('{}BBoxToFormat')".format(prefixNST), icon="Rectangle.png")
transformMenu.addCommand('ImagePlane3D TL', "nuke.createNode('{}ImagePlane3D')".format(prefixNST), icon="Card.png")
transformMenu.addCommand('Matrix_Inverse TL', "nuke.createNode('{}Matrix4x4_Inverse')".format(prefixNST), icon="ColorMatrix.png")
transformMenu.addCommand('Matrix4x4Math TL', "nuke.createNode('{}Matrix4x4Math')".format(prefixNST), icon="ColorMath.png")
transformMenu.addCommand('MirrorBorder TL', "nuke.createNode('{}MirrorBorder')".format(prefixNST), icon="AdjBBox.png")
transformMenu.addCommand('TransformCutOut TL', "nuke.createNode('{}TransformCutOut')".format(prefixNST), icon="MergeOut.png")
transformMenu.addCommand('iMorph TL', "nuke.createNode('{}iMorph')".format(prefixNST), icon="Blend.png")

transformMenu.addSeparator()

transformMenu.addCommand('RP_Reformat MJT', "nuke.createNode('{}RP_Reformat')".format(prefixNST), icon='RP_Reformat.png')
transformMenu.addCommand('inverseMatrix MJT', "nuke.createNode('{}inverseMatrix')".format(prefixNST), icon='inverseMatrix.png')

transformMenu.addSeparator()

transformMenu.addCommand('CardToTrack AK', "nuke.createNode('{}CardToTrack')".format(prefixNST), icon='Card.png')
transformMenu.addCommand('CProject AK', "nuke.createNode('{}CProject')".format(prefixNST), icon='CornerPin.png')
transformMenu.addCommand('TProject AK', "nuke.createNode('{}TProject')".format(prefixNST), icon='Transform.png')


transformMenu.addSeparator()

transformMenu.addCommand('TransformMatrix AG', "nuke.createNode('{}TransformMatrix')".format(prefixNST), icon="Transform.png")
transformMenu.addCommand('CornerPin2D_Matrix AG', "nuke.createNode('{}CornerPin2D_Matrix')".format(prefixNST), icon="CornerPin.png")

transformMenu.addSeparator()

transformMenu.addCommand('IIDistort EL', "nuke.createNode('{}IIDistort')".format(prefixNST), icon="nukepedia_icon.png")
transformMenu.addCommand('bm_CameraShake BM', "nuke.createNode('{}bm_CameraShake')".format(prefixNST), icon="bm_CameraShake_icon.png")
transformMenu.addCommand('ITransform FR', "nuke.createNode('{}ITransformU')".format(prefixNST), icon="STMap.png")
transformMenu.addCommand('MorphDissolve SPIN', "nuke.createNode('{}MorphDissolve')".format(prefixNST), icon="spin_tools.png")
transformMenu.addCommand('RotoCentroid NKPD', "nuke.createNode('{}RotoCentroid')".format(prefixNST), icon="nukepedia_icon.png")
transformMenu.addCommand('STmapInverse NKPD', "nuke.createNode('{}STmapInverse')".format(prefixNST), icon="nukepedia_icon.png")
transformMenu.addCommand('TransformMix NKPD', "nuke.createNode('{}TransformMix')".format(prefixNST), icon="nukepedia_icon.png")
transformMenu.addCommand('PlanarProjection NKPD', "nuke.createNode('{}PlanarProjection')".format(prefixNST), icon="nukepedia_icon.png")
transformMenu.addCommand('Reconcile3DFast DR', "nuke.createNode('{}Reconcile3DFast')".format(prefixNST), icon="Reconcile3D.png")


############################################################################################################
############################################################################################################

# Create 3D Menu

ThreeDMenu = m.addMenu('3D', icon = 'Toolbar3D.png', index = 100)

ThreeDMenu.addCommand('aPCard AP', 'nuke.createNode("{}aPCard")'.format(prefixNST), icon='ap_tools.png')
ThreeDMenu.addCommand('DummyCam', 'nuke.createNode("{}DummyCam")'.format(prefixNST), icon='DummyCam.png')

ThreeDMenu.addSeparator()

ThreeDMenu.addCommand('mScatterGeo MJT', 'nuke.createNode("{}mScatterGeo")'.format(prefixNST), icon='mScatterGeo.png')
ThreeDMenu.addCommand('GeoToPoints MHD', "nuke.createNode('{}GeoToPoints')".format(prefixNST), icon="nukepedia_icon.png")
ThreeDMenu.addCommand('origami MJT', 'nuke.createNode("{}origami")'.format(prefixNST), icon='origami.png')
ThreeDMenu.addCommand('RayDeepAO MJT', 'nuke.createNode("{}RayDeepAO")'.format(prefixNST), icon='RayDeepAO.png')
ThreeDMenu.addCommand('SceneDepthCalculator MJT', 'nuke.createNode("{}SceneDepthCalculator")'.format(prefixNST), icon='SceneDepthCalculator.png')
ThreeDMenu.addCommand('SSMesh MJT', 'nuke.createNode("{}SSMesh")'.format(prefixNST), icon='SSMesh.png')
ThreeDMenu.addCommand('Unify3DCoordinate MJT', 'nuke.createNode("{}Unify3DCoordinate")'.format(prefixNST), icon='Unify3DCoordinate.png')
ThreeDMenu.addCommand('UVEditor MJT', 'nuke.createNode("{}UVEditor")'.format(prefixNST), icon='UVEditor.png')

ThreeDMenu.addSeparator()

ThreeDMenu.addCommand('Distance3D NKPD', "nuke.createNode('{}Distance3D')".format(prefixNST), icon="nukepedia_icon.png")
ThreeDMenu.addCommand('DistanceBetween_CS NKPD', "nuke.createNode('{}DistanceBetween_CS')".format(prefixNST), icon="nukepedia_icon.png")
ThreeDMenu.addCommand('Lightning3D EL', "nuke.createNode('{}Lightning3D')".format(prefixNST), icon="nukepedia_icon.png")
ThreeDMenu.addCommand('Noise3DTexture NKPD', "nuke.createNode('{}Noise3DTexture')".format(prefixNST), icon="noise3dicon.png")


############################################################################################################
############################################################################################################

# Create Paricles Menu

particlesMenu = m.addMenu('Particles', icon = 'ToolbarParticles.png', index = 110)

particlesMenu.addCommand('waterSchmutz DR', "nuke.createNode('{}waterSchmutz')".format(prefixNST), icon="WaterLens.png")
particlesMenu.addCommand('Sparky DB', "nuke.createNode('{}Sparky')".format(prefixNST), icon="Sparky.png")
particlesMenu.addCommand('ParticleLights MHD', "nuke.createNode('{}ParticleLights')".format(prefixNST), icon="ToolbarParticles.png")
particlesMenu.addCommand('ParticleKiller NKPD', "nuke.createNode('{}ParticleKiller')".format(prefixNST), icon="ToolbarParticles.png")


############################################################################################################
############################################################################################################

# Create Deep Menu

deepMenu = m.addMenu('Deep', icon = 'ToolbarDeep.png', index = 120)

deep2VP_suite = deepMenu.addMenu("Deep2VP Suite MJT", icon='Deep2VPosition.png')
deep2VP_suite.addCommand('Deep2VPosition MJT', "nuke.createNode('{}Deep2VPosition')".format(prefixNST), icon="Deep2VPosition.png")
deep2VP_suite.addCommand('DVPattern MJT', "nuke.createNode('{}DVPattern')".format(prefixNST), icon="DVPattern.png")
deep2VP_suite.addCommand('DVPfresnel MJT', "nuke.createNode('{}DVPfresnel')".format(prefixNST), icon="DVPfresnel.png")
deep2VP_suite.addCommand('DVPmatte MJT', "nuke.createNode('{}DVPmatte')".format(prefixNST), icon="DVPmatte.png")
deep2VP_suite.addCommand('DVPort MJT', "nuke.createNode('{}DVPort')".format(prefixNST), icon="DVPort.png")
deep2VP_suite.addCommand('DVPrelight MJT', "nuke.createNode('{}DVPrelight')".format(prefixNST), icon="DVPrelight.png")
deep2VP_suite.addCommand('DVProjection MJT', "nuke.createNode('{}DVProjection')".format(prefixNST), icon="DVProjection.png")
deep2VP_suite.addCommand('DVPscene MJT', "nuke.createNode('{}DVPscene')".format(prefixNST), icon="DVPscene.png")
deep2VP_suite.addCommand('DVPsetLight MJT', "nuke.createNode('{}DVPsetLight')".format(prefixNST), icon="DVPsetLight.png")
deep2VP_suite.addCommand('DVPToImage MJT', "nuke.createNode('{}DVPToImage')".format(prefixNST), icon="DVPToImage.png")

deepMenu.addSeparator()

deepMenu.addCommand('DeepBoolean MJT', "nuke.createNode('{}DeepBoolean')".format(prefixNST), icon="DeepBoolean.png")
deepMenu.addCommand('DeepFromPosition MJT', "nuke.createNode('{}DeepFromPosition')".format(prefixNST), icon="DeepFromPosition.png")
deepMenu.addCommand('DeepSampleCount MJT', "nuke.createNode('{}DeepSampleCount')".format(prefixNST), icon="DeepSampleCount.png")
deepMenu.addCommand('DeepSer MJT', "nuke.createNode('{}DeepSer')".format(prefixNST), icon="DeepSer.png")

deepMenu.addSeparator()

deepMenu.addCommand('DeepToPosition TL', "nuke.createNode('{}DeepToPosition')".format(prefixNST), icon="Deep2VPosition.png")
deepMenu.addCommand('DeepRecolorMatte TL', "nuke.createNode('{}DeepRecolorMatte')".format(prefixNST), icon="DeepRecolor.png")

deepMenu.addSeparator()

deepMenu.addCommand('DeepMerge_Advanced BM', "nuke.createNode('{}DeepMerge_Advanced')".format(prefixNST), icon="DeepMerge.png")
deepMenu.addCommand('DeepCropSoft NKPD', "nuke.createNode('{}DeepCropSoft')".format(prefixNST), icon="DeepCrop.png")
deepMenu.addCommand('DeepKeyMix NKPD', "nuke.createNode('{}DeepKeyMix')".format(prefixNST), icon="DeepMerge.png")
deepMenu.addCommand('DeepHoldoutSmoother NKPD', "nuke.createNode('{}DeepHoldoutSmoother')".format(prefixNST), icon="DeepHoldout.png")
deepMenu.addCommand('DeepCopyBBox NKPD', "nuke.createNode('{}DeepCopyBBox')".format(prefixNST), icon="DeepMerge.png")


############################################################################################################
############################################################################################################

# Create CG Menu

cgMenu = m.addMenu('CG', icon = 'RenderManShader.png', index = 130)

cgMenu.addCommand('UV Mapper TL', "nuke.createNode('{}UV_Mapper')".format(prefixNST), icon="Tile.png")

cgMenu.addSeparator()

PNZsuite = cgMenu.addMenu('PNZsuite MJT', icon = 'ConvertPNZ.png')
PNZsuite.addCommand('ConvertPNZ MJT', 'nuke.createNode("{}ConvertPNZ")'.format(prefixNST), icon='ConvertPNZ.png')
PNZsuite.addCommand('P2N MJT', 'nuke.createNode("{}P2N")'.format(prefixNST), icon='P2N.png')
PNZsuite.addCommand('P2Z MJT', 'nuke.createNode("{}P2Z")'.format(prefixNST), icon='P2Z.png')
PNZsuite.addCommand('Z2N MJT', 'nuke.createNode("{}Z2N")'.format(prefixNST), icon='Z2N.png')
PNZsuite.addCommand('Z2P MJT', 'nuke.createNode("{}Z2P")'.format(prefixNST), icon='Z2P.png')

PosToolkit = cgMenu.addMenu('PosToolkit MJT', icon = 'PosMatte_MJ.png')
PosToolkit.addCommand('PosMatte MJT', 'nuke.createNode("{}PosMatte_MJ")'.format(prefixNST), icon='PosMatte_MJ.png')
PosToolkit.addCommand('PosPattern MJT', 'nuke.createNode("{}PosPattern_MJ")'.format(prefixNST), icon='PosPattern_MJ.png')
PosToolkit.addCommand('PosProjection MJT', 'nuke.createNode("{}PosProjection_MJ")'.format(prefixNST), icon='PosProjection_MJ.png')


cgMenu.addSeparator()

cgMenu.addCommand('Noise_3D SPIN', 'nuke.createNode("{}Noise3D_spin")'.format(prefixNST), icon='spin_tools.png')
cgMenu.addCommand('Noise4D MHD', 'nuke.nodePaste("{}/NukepediaTools/13_CG/{}Noise4D.nk")'.format(NST_FolderPath, prefixNST), icon='Noise.png')
cgMenu.addCommand('Relight_Simple SPIN', 'nuke.createNode("{}Relight_Simple")'.format(prefixNST), icon='spin_tools.png')
cgMenu.addCommand('ReProject_3D SPIN', 'nuke.createNode("{}ReProject_3D")'.format(prefixNST), icon='spin_tools.png')


cgMenu.addSeparator()

cgMenu.addCommand('C44Kernel AP', 'nuke.createNode("{}C44Kernel")'.format(prefixNST), icon='C44Kernel.png')
cgMenu.addCommand('apDirLight AP', 'nuke.createNode("{}apDirLight")'.format(prefixNST), icon='apDirLight.png')
cgMenu.addCommand('apFresnel AP', 'nuke.createNode("{}apFresnel")'.format(prefixNST), icon='ap_tools.png')
cgMenu.addCommand('CameraNormals NKPD', "nuke.createNode('{}CameraNormals')".format(prefixNST), icon="Camera.png")
cgMenu.addCommand('NormalsRotate NKPD', "nuke.createNode('{}NormalsRotate')".format(prefixNST), icon="SpotLight.png")
cgMenu.addCommand('Relight_bb NKPD', "nuke.createNode('{}Relight_bb')".format(prefixNST), icon="SpotLight.png")
cgMenu.addCommand('EnvReflect_bb NKPD', "nuke.createNode('{}EnvReflect_BB')".format(prefixNST), icon="Sphere.png")
cgMenu.addCommand('N_Reflection NKPD', "nuke.createNode('{}N_Reflection')".format(prefixNST), icon="Sphere.png")

cgMenu.addCommand('SimpleSSS MHD', "nuke.createNode('{}SimpleSSS')".format(prefixNST), icon="Toolbar3D.png")

cgMenu.addSeparator()

cgMenu.addCommand('aPmatte AP', 'nuke.createNode("{}aPMatte_v2")'.format(prefixNST), icon='aPmatte.png')
cgMenu.addCommand('P_Ramp NKPD', "nuke.createNode('{}F_P_Ramp')".format(prefixNST), icon="F_pramp.png")
cgMenu.addCommand('P_Project NKPD', "nuke.createNode('{}F_P_Project')".format(prefixNST), icon="F_pproject.png")
cgMenu.addCommand('Glue_P LS', "nuke.createNode('{}GlueP')".format(prefixNST), icon="PosProjection_MJ.png")
cgMenu.addCommand('P_Noise_Advanced NKPD', "nuke.createNode('{}P_Noise_Advanced')".format(prefixNST), icon="Noise.png")

############################################################################################################
############################################################################################################

# Create Curves Menu

curvesMenu = m.addMenu('Curves', icon = 'ParticleCurve.png', index = 140)

waveMachineMenu = curvesMenu.addMenu("Wave Machine FL", icon='waveMachine.png')
waveMachineMenu.addCommand('WaveMaker FL', "nuke.createNode('{}waveMaker')".format(prefixNST), icon="waveMaker.png")
waveMachineMenu.addCommand('WaveCustom FL', "nuke.createNode('{}waveCustom')".format(prefixNST), icon="waveCustom.png")
waveMachineMenu.addCommand('WaveGrade FL', "nuke.createNode('{}waveGrade')".format(prefixNST), icon="waveGrade.png")
waveMachineMenu.addCommand('WaveRetime FL', "nuke.createNode('{}waveRetime')".format(prefixNST), icon="waveRetime.png")
waveMachineMenu.addCommand('WaveMerge FL', "nuke.createNode('{}waveMerge')".format(prefixNST), icon="waveMerge.png")

curvesMenu.addSeparator()

curvesMenu.addCommand('Randomizer TL', "nuke.createNode('{}Randomizer')".format(prefixNST), icon="RenderMan.png")
curvesMenu.addCommand('AnimationCurve AG', "nuke.createNode('{}AnimationCurve')".format(prefixNST), icon="nukepedia_icon.png")
curvesMenu.addCommand('bm_CurveRemapper BM', "nuke.createNode('{}bm_CurveRemapper')".format(prefixNST), icon="bm_CurveRemapper_icon.png")
curvesMenu.addCommand('bm_NoiseGen BM', "nuke.createNode('{}bm_NoiseGen')".format(prefixNST), icon="bm_NoiseGen_icon.png")

############################################################################################################
############################################################################################################

# Create Utilities Menu

utilitiesMenu = m.addMenu('Utilities', icon = 'Modify.png', index = 150)

utilitiesMenu.addCommand('GUI Switch TL', "nuke.createNode('{}GUI_Switch')".format(prefixNST), icon="Switch.png")
utilitiesMenu.addCommand('NAN INF Killer TL', "nuke.createNode('{}NAN_INF_Killer')".format(prefixNST), icon="Assert.png")

utilitiesMenu.addSeparator()

utilitiesMenu.addCommand('apViewerBlocker AP', 'nuke.createNode("{}apViewerBlocker")'.format(prefixNST), icon='ap_tools.png')
utilitiesMenu.addCommand('Python_and_TCL AG', 'nuke.createNode("{}Python_and_TCL")'.format(prefixNST), icon="nukepedia_icon.png")

utilitiesMenu.addCommand('RotoQC NKPD', "nuke.createNode('{}RotoQC')".format(prefixNST), icon="Roto.png")
utilitiesMenu.addCommand('bm_MatteCheck BM', "nuke.createNode('{}bm_MatteCheck')".format(prefixNST), icon="bm_MatteCheck_icon.png")

utilitiesMenu.addSeparator()

utilitiesMenu.addCommand('viewer_render MJT', 'nuke.createNode("{}viewer_render")'.format(prefixNST), icon='viewer_render.png')
utilitiesMenu.addCommand('NukeZ MJT', 'nuke.createNode("{}NukeZ")'.format(prefixNST), icon='NukeZ.png')
utilitiesMenu.addCommand('Pyclopedia MJT', 'nuke.createNode("{}Pyclopedia")'.format(prefixNST), icon='Pyclopedia.png')


############################################################################################################
############################################################################################################

# Create Templates Menu

templatesMenu = m.addMenu('Templates', icon = 'PointsTo3D.png', index = 200)

templatesMenu.addCommand('Advanced Keying Template Stamps TL', "nuke.nodePaste('{}/LyonsTools/gizmos/00_Templates/{}AdvancedKeyingTemplate_Stamps.nk')".format(NST_FolderPath, prefixNST), icon="Keyer.png")
templatesMenu.addCommand('Advanced Keying Template TL', "nuke.nodePaste('{}/LyonsTools/gizmos/00_Templates/{}AdvancedKeyingTemplate.nk')".format(NST_FolderPath, prefixNST), icon="Keyer.png")
templatesMenu.addCommand('STMap Keyer Setup EL', "nuke.nodePaste('{}/NukepediaTools/00_Templates/{}STMap_Keying_Setup.nk')".format(NST_FolderPath, prefixNST), icon="HueKeyer.png")

templatesMenu.addSeparator()

gizmoDemoMenu = templatesMenu.addMenu("Gizmo Demo Scripts", icon='Group.png')

gizmoDemoMenu.addCommand('WaterLens Demo MJT', "NST_helper.filepathCreateNode('{}/MJT_Labs/Draw/WaterLens_11/demo_script/{}WaterLens_sampleScript.nk')".format(NST_FolderPath, prefixNST), icon="WaterLens.png")
gizmoDemoMenu.addCommand('SSMesh Demo MJT', "nuke.nodePaste('{}/MJT_Labs/3D/SSMesh_v13/demo_script/{}SSMesh_demo.nk')".format(NST_FolderPath, prefixNST), icon="SSMesh.png")
gizmoDemoMenu.addCommand('UVEditor Demo MJT', "nuke.nodePaste('{}/MJT_Labs/3D/UVEditor_v14/demo_script/{}UVEditor_demo_clean.nk')".format(NST_FolderPath, prefixNST), icon="UVEditor.png")
gizmoDemoMenu.addCommand('Sparky Demo DB', "nuke.nodePaste('{}/NukepediaTools/11_Particles/DB_Sparky_v1.5/ExampleScene/{}SparkyExampleScene.nk')".format(NST_FolderPath, prefixNST), icon="Sparky.png")
gizmoDemoMenu.addCommand('ParticleLights Demo MHD', "nuke.nodePaste('{}/Hagbarth_Tools/{}ParticleLights_ExampleScript.nk')".format(NST_FolderPath, prefixNST), icon="ToolbarParticles.png")


