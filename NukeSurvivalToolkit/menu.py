#*****************************************************************
#*****************************************************************
# This file will setup the NukeSurvivalToolkit Menu on your Toolbar
# Written by Tony Lyons 09/2020 | www.CreativeLyons.com | www.CompositingMentor.com
#*****************************************************************
#*****************************************************************

# Imports
import nuke
import sys
import os
from pathlib import Path

############################################################################################################

# Add PluginPaths to tools and icons
nuke.pluginAddPath('./gizmos')
nuke.pluginAddPath('./python')
nuke.pluginAddPath('./icons')
nuke.pluginAddPath('./images')
nuke.pluginAddPath('./nk_files')

# Import some helpful functions for the NST
import NST_helper

# This is the prefix being used to customize the gizmo's in this toolkit
global prefixNST
prefixNST = "NST_"

# Store the location of this menu.py to help with nuke.nodePaste() which requires a filepath to paste
# Use Path.as_posix() to ensure forward slashes on all platforms (fixes Windows path issues)
NST_FolderPath = Path(__file__).parent.as_posix()
NST_helper.NST_FolderPath = NST_FolderPath

############################################################################################################
# Helpers to keep code readable

def nk_path(filename, prefix=False):
    """Return full path to an .nk file in nk_files folder."""
    name = f"{prefixNST}{filename}" if prefix else filename
    return f"{NST_FolderPath}/nk_files/{name}"

def icon_path(filename):
    """Return full path to an icon file."""
    return f"{NST_FolderPath}/icons/{filename}"

############################################################################################################
# User Configuration Variables
############################################################################################################

# Documentation behavior/config (kept in menu.py for explicit user editing)
NST_helper.NST_DOCS_ONLINE_URL = "https://creativelyons.github.io/NukeSurvivalToolkit_Wiki/"
NST_helper.NST_DOCS_ONLINE_TIMEOUT_SECONDS = 1.5
NST_helper.NST_DOCS_PDF_NAME = "NukeSurvivalToolkit_Documentation_Release_v2.1.0.pdf"
NST_helper.NST_DOCS_OFFLINE_INDEX = Path("NST_Documentation/index.html")

# Set to True to load the Expression Nodes AG submenu under Draw; set to False to skip it
LOAD_EXPRESSION_MENU = False

############################################################################################################
# End of User Configuration Variables
############################################################################################################

############################################################################################################
# Start of Menu Creation
############################################################################################################

# Create NukeSurivalToolkit Menu
toolbar = nuke.menu('Nodes')
NST_menu = toolbar.addMenu('NukeSurvivalToolkit', icon = "SurvivalToolkit.png")


############################################################################################################
############################################################################################################

# Create Documentation Submenu
documentationMenu = NST_menu.addMenu("Documentation", icon="info_icon.png", index=00)
documentationMenu.addCommand("Wiki\\/Docs (Auto)", "NST_helper.openNSTDocumentationDefault()", icon="wiki_default.png")
documentationMenu.addCommand("Wiki (Online)", "NST_helper.openNSTDocumentationOnline()", icon="wiki_online.png")
documentationMenu.addCommand("Wiki (Offline)", "NST_helper.openNSTDocumentationOffline()", icon="wiki_offline.png")
documentationMenu.addCommand("Docs (PDF)", "NST_helper.openNSTDocumentationPDF()", icon="StickyNote.png")

############################################################################################################
############################################################################################################


# Create Image Menu
imageMenu = NST_menu.addMenu('Image', icon = 'ToolbarImage.png', index = 10)

imageMenu.addCommand('LabelFromRead TL', f"nuke.createNode('{prefixNST}LabelFromRead')", icon="LabelFromRead.png")

############################################################################################################
############################################################################################################

# Create Draw Menu
drawMenu = NST_menu.addMenu('Draw', icon = 'ToolbarDraw.png', index = 20)

if LOAD_EXPRESSION_MENU:
    expressionMenu = drawMenu.addMenu("Expression Nodes AG", icon=icon_path("expr.png"), index=000)
    expressionMenu.addMenu('Creations', icon=icon_path("expr_01.png"))
    expressionMenu.addMenu('Alpha', icon=icon_path("expr_02.png"))
    expressionMenu.addMenu('Pixel', icon=icon_path("expr_03.png"))
    expressionMenu.addMenu('Keying and Despill', icon=icon_path("expr_04.png"))
    expressionMenu.addMenu('Transform', icon=icon_path("expr_05.png"))
    expressionMenu.addMenu('3D and Deep', icon=icon_path("expr_06.png"))

    #CREATIONS
    expressionMenu.addCommand('Creations/Random/Random Colors', f'nuke.nodePaste("{nk_path("Random_colors.nk")}")')
    expressionMenu.addCommand('Creations/Random/Random every Frame', f'nuke.nodePaste("{nk_path("Random_every_frame.nk")}")')
    expressionMenu.addCommand('Creations/Random/Random every Pixel', f'nuke.nodePaste("{nk_path("Random_every_pixel.nk")}")')
    #expressionMenu.addCommand('Creations/Noise/Noise', f'nuke.nodePaste("{nk_path("Noise.nk")}")')
    #expressionMenu.addCommand('Creations/Noise/fBm', f'nuke.nodePaste("{nk_path("fBm.nk")}")')
    #expressionMenu.addCommand('Creations/Noise/Turbulence', f'nuke.nodePaste("{nk_path("turbulence.nk")}")')
    expressionMenu.addCommand('Creations/lines vertical', f'nuke.nodePaste("{nk_path("Lines_Vertical.nk")}")')
    expressionMenu.addCommand('Creations/lines horizontal', f'nuke.nodePaste("{nk_path("Lines_Horizontal.nk")}")')
    expressionMenu.addCommand('Creations/lines vertical animated', f'nuke.nodePaste("{nk_path("Lines_Vertical_Animated.nk")}")')
    expressionMenu.addCommand('Creations/lines horizontal animated', f'nuke.nodePaste("{nk_path("Lines_Horizontal_Animated.nk")}")')
    expressionMenu.addCommand('Creations/circles', f'nuke.nodePaste("{nk_path("circles.nk")}")')
    expressionMenu.addCommand('Creations/circles user', f'nuke.nodePaste("{nk_path("circles_user.nk")}")')
    expressionMenu.addCommand('Creations/points', f'nuke.nodePaste("{nk_path("points.nk")}")')
    expressionMenu.addCommand('Creations/points advanced', f'nuke.nodePaste("{nk_path("points_advanced.nk")}")')
    expressionMenu.addCommand('Creations/bricks', f'nuke.nodePaste("{nk_path("bricks.nk")}")')
    expressionMenu.addCommand('Creations/gradient horizontal', f'nuke.nodePaste("{nk_path("gradient_horizontal.nk")}")')
    expressionMenu.addCommand('Creations/gradient horizontal invert', f'nuke.nodePaste("{nk_path("gradient_horizontal_invert.nk")}")')
    expressionMenu.addCommand('Creations/gradient vertical', f'nuke.nodePaste("{nk_path("gradient_vertical.nk")}")')
    expressionMenu.addCommand('Creations/gradient vertical invert', f'nuke.nodePaste("{nk_path("gradient_vertical_invert.nk")}")')
    expressionMenu.addCommand('Creations/gradient 4 corners', f'nuke.nodePaste("{nk_path("GradientCorner.nk")}")')
    expressionMenu.addCommand('Creations/radial', f'nuke.nodePaste("{nk_path("radial.nk")}")')
    expressionMenu.addCommand('Creations/radial gradient', f'nuke.nodePaste("{nk_path("radial_gradient.nk")}")')
    expressionMenu.addCommand('Creations/radial rays', f'nuke.nodePaste("{nk_path("radial_rays.nk")}")')
    expressionMenu.addCommand('Creations/Trunc', f'nuke.nodePaste("{nk_path("Trunc.nk")}")')

    #ALPHA
    expressionMenu.addCommand('Alpha/alpha binary', f'nuke.nodePaste("{nk_path("alpha_binary.nk")}")')
    expressionMenu.addCommand('Alpha/alpha comparison', f'nuke.nodePaste("{nk_path("alpha_comparison.nk")}")')
    expressionMenu.addCommand('Alpha/alpha exists?', f'nuke.nodePaste("{nk_path("alpha_exists.nk")}")')
    expressionMenu.addCommand('Alpha/alpha sum', f'nuke.nodePaste("{nk_path("alpha_sum.nk")}")')

    #PIXEL
    expressionMenu.addCommand('Pixel/absolute value', f'nuke.nodePaste("{nk_path("abs.nk")}")')
    expressionMenu.addCommand('Pixel/check negative', f'nuke.nodePaste("{nk_path("check_negative.nk")}")')
    expressionMenu.addCommand('Pixel/check nan inf pixels', f'nuke.nodePaste("{nk_path("check_nan_inf.nk")}")')
    expressionMenu.addCommand('Pixel/create nan pixel', f'nuke.nodePaste("{nk_path("create_nan.nk")}")')
    expressionMenu.addCommand('Pixel/kill nan pixel', f'nuke.nodePaste("{nk_path("kill_nan.nk")}")')
    expressionMenu.addCommand('Pixel/create inf pixel', f'nuke.nodePaste("{nk_path("create_inf.nk")}")')
    expressionMenu.addCommand('Pixel/kill inf pixel', f'nuke.nodePaste("{nk_path("kill_inf.nk")}")')

    #TRANSFORM
    expressionMenu.addCommand('Transform/Coordinates', f'nuke.nodePaste("{nk_path("coordinates.nk")}")')
    expressionMenu.addCommand('Transform/UV to Vector', f'nuke.nodePaste("{nk_path("UV_to_Vector.nk")}")')
    expressionMenu.addCommand('Transform/Vector to UV', f'nuke.nodePaste("{nk_path("Vector_to_UV.nk")}")')
    expressionMenu.addCommand('Transform/transform', f'nuke.nodePaste("{nk_path("transform.nk")}")')
    expressionMenu.addCommand('Transform/transform advanced', f'nuke.nodePaste("{nk_path("transform_advanced.nk")}")')
    expressionMenu.addCommand('Transform/twist', f'nuke.nodePaste("{nk_path("twist.nk")}")')
    expressionMenu.addCommand('Transform/STMap_invert', f'nuke.nodePaste("{nk_path("STMap_invert.nk")}")')

    #3D and DEEP
    expressionMenu.addCommand('3D and Deep/Normal Pass - Relight', f'nuke.nodePaste("{nk_path("normalPass_relight.nk")}")')
    expressionMenu.addCommand('3D and Deep/C4x4', f'nuke.nodePaste("{nk_path("C4x4.nk")}")')
    expressionMenu.addCommand('3D and Deep/Deep to Depth', f'nuke.nodePaste("{nk_path("deepToDepth.nk")}")')
    expressionMenu.addCommand('3D and Deep/Depth normalize', f'nuke.nodePaste("{nk_path("depth_normalize.nk")}")')

    #KEYING and DESPILL
    expressionMenu.addCommand('Keying and Despill/despill green', f'nuke.nodePaste("{nk_path("despill_green.nk")}")')
    expressionMenu.addCommand('Keying and Despill/despill green list', f'nuke.nodePaste("{nk_path("despill_green_list.nk")}")')
    expressionMenu.addCommand('Keying and Despill/despill blue', f'nuke.nodePaste("{nk_path("despill_blue.nk")}")')
    expressionMenu.addCommand('Keying and Despill/despill blue list', f'nuke.nodePaste("{nk_path("despill_blue_list.nk")}")')
    expressionMenu.addCommand('Keying and Despill/keying', f'nuke.nodePaste("{nk_path("keying.nk")}")')
    expressionMenu.addCommand('Keying and Despill/differenceKey', f'nuke.nodePaste("{nk_path("differenceKey.nk")}")')
    expressionMenu.addCommand('Keying and Despill/IBKGizmo_Expression', f'nuke.nodePaste("{nk_path("IBKGizmo_Expression.nk")}")')

    expressionMenu.addSeparator()

    #INFO
    expressionMenu.addCommand('Info e Tutorial', "nuke.tcl('start', 'http://www.andreageremia.it/tutorial_expression_node.html')", icon=icon_path("question_mark.png"))

drawMenu.addSeparator()

drawMenu.addCommand('ConstantPro TL', f"nuke.createNode('{prefixNST}ConstantPro')", icon="Constant.png")
drawMenu.addCommand('HexColor NW', f"nuke.createNode('{prefixNST}HexColor')", icon="Constant.png")
drawMenu.addCommand('GradMagic TL', f"nuke.createNode('{prefixNST}GradMagic')", icon="GradMagic.png")
drawMenu.addCommand('NoiseAdvanced TL', f"nuke.createNode('{prefixNST}NoiseAdvanced')", icon="Noise.png")
drawMenu.addCommand('RadialAdvanced TL', f"nuke.createNode('{prefixNST}RadialAdvanced')", icon="Radial.png")
drawMenu.addCommand('UV Map AG', f"nuke.createNode('{prefixNST}UV_Map')", icon="AG_UVMap.png")
drawMenu.addCommand("SpotLight TL", f"nuke.createNode('{prefixNST}SpotLight')", icon="Radial.png")
drawMenu.addCommand("Rings of Power TL", f"nuke.createNode('{prefixNST}Rings_of_Power')", icon="MergeIn.png")

drawMenu.addSeparator()

drawMenu.addCommand('WaterLens MJT', f"nuke.createNode('{prefixNST}WaterLens')", icon="WaterLens.png")
drawMenu.addCommand("Silk MHD", f"nuke.createNode('{prefixNST}h_silk')", icon="h_silk.png")

# Try to add GradientEditor
try:
    import ColorGradientUi
    drawMenu.addCommand("GradientEditor MHD", f"nuke.createNode('{prefixNST}h_gradienteditor')", icon="h_gradienteditor.png")
except ImportError as e:
    print(f"Could not load ColorGradientUi from HagbarthTools folder: {e}")
    pass

drawMenu.addSeparator()

drawMenu.addCommand('VoronoiGradient NW', f"nuke.createNode('{prefixNST}VoronoiGradient')", icon="GradMagic.png")
drawMenu.addCommand('CellNoise NKPD', f"nuke.createNode('{prefixNST}CellNoise')", icon="Noise.png")
drawMenu.addCommand('LineTool NKPD', f"nuke.createNode('{prefixNST}LineTool')", icon="nukepedia_icon.png")
drawMenu.addCommand('PlotScanline NKPD', f"nuke.createNode('{prefixNST}PlotScanline')", icon="nukepedia_icon.png")
drawMenu.addCommand('SliceTool FR', f"nuke.createNode('{prefixNST}SliceTool')", icon="Histogram.png")
drawMenu.addCommand('PerspectiveGuide NKPD', f"nuke.createNode('{prefixNST}PerspectiveGuide')", icon="nukepedia_icon.png")

drawMenu.addSeparator()

drawMenu.addCommand('DasGrain FH', f"nuke.createNode('{prefixNST}DasGrain')", icon="Grain.png")
drawMenu.addCommand('LumaGrain LUMA', f"nuke.createNode('{prefixNST}LumaGrain')", icon="nukepedia_icon.png")
drawMenu.addCommand('Grain_Advanced SPIN', f"nuke.createNode('{prefixNST}Grain_Advanced')", icon="spin_tools.png")

drawMenu.addSeparator()

drawMenu.addCommand("X_Tesla XM", f"nuke.createNode('{prefixNST}X_Tesla')", icon="X_Tesla.png")
drawMenu.addCommand('SpotFlare MHD', f"nuke.createNode('{prefixNST}SpotFlare')", icon="Flare.png")
drawMenu.addCommand('FlareSuperStar NKPD', f"nuke.createNode('{prefixNST}FlareSuperStar')", icon="nukepedia_icon.png")
drawMenu.addCommand('AutoFlare NKPD', f"NST_helper.filepathCreateNode('{prefixNST}AutoFlare2')", icon="Flare.png")
drawMenu.addCommand("BokehBuilder KB", f"nuke.createNode('{prefixNST}BokehBuilder')", icon="K_BokehBuilder.png")
drawMenu.addCommand("LensEngine KB", f"nuke.createNode('{prefixNST}LensEngine')", icon="K_LensEngine.png")


############################################################################################################
############################################################################################################

# Create Time Menu
timeMenu = NST_menu.addMenu('Time', icon = 'ToolbarTime.png', index = 30)

timeMenu.addCommand('apLoop AP', f'nuke.createNode("{prefixNST}apLoop")', icon='apLoop.png')

timeMenu.addSeparator()

timeMenu.addCommand('FrameHold Special AG', f"nuke.createNode('{prefixNST}FrameHoldSpecial')", icon="FrameHold.png")
timeMenu.addCommand('Looper DB', f"nuke.createNode('{prefixNST}Looper')", icon="nukepedia_icon.png")
timeMenu.addCommand('FrameMedian MHD', f"nuke.createNode('{prefixNST}FrameMedian')", icon="FrameBlend.png")
timeMenu.addCommand('TimeMachine NKPD', f"nuke.createNode('{prefixNST}TimeMachine')", icon="nukepedia_icon.png")
timeMenu.addCommand('FrameFiller MJT', f"nuke.createNode('{prefixNST}FrameFiller')", icon="FrameFiller.png")

############################################################################################################
############################################################################################################

# Create Channel Menu
channelMenu = NST_menu.addMenu('Channel', icon = 'ToolbarChannel.png', index = 40)

channelMenu.addCommand('BinaryAlpha TL', f"nuke.createNode('{prefixNST}BinaryAlpha')", icon="BumpBoss.png")
channelMenu.addCommand('ChannelCombiner TL', f"nuke.createNode('{prefixNST}ChannelCombiner')", icon="ChannelMerge.png")
channelMenu.addCommand('ChannelControl TL', f"nuke.createNode('{prefixNST}ChannelControl')", icon="LayerChannel.png")
channelMenu.addCommand('ChannelCreator TL', f"nuke.createNode('{prefixNST}ChannelCreator')", icon="Add.png")
channelMenu.addCommand('InjectMatteChannel TL', f"nuke.createNode('{prefixNST}InjectMatteChannel')", icon="ChannelMerge.png")
channelMenu.addCommand('ID_Extractor TL', f"nuke.createNode('{prefixNST}ID_Extractor')", icon="Shuffle.png")

channelMenu.addSeparator()

channelMenu.addCommand('streamCart MJT', f"nuke.createNode('{prefixNST}streamCart')", icon="streamCart.png")
channelMenu.addCommand('renameChannels AG', f"nuke.createNode('{prefixNST}renameChannels')", icon="nukepedia_icon.png")


############################################################################################################
############################################################################################################

# Create Color Menu
colorMenu = NST_menu.addMenu('Color', icon = 'ToolbarColor.png', index = 50)

colorMenu.addCommand('BlacksMatch TL', f"nuke.createNode('{prefixNST}BlacksMatch')", icon="BlacksMatch.png")
colorMenu.addCommand('ColorCopy TL', f"nuke.createNode('{prefixNST}ColorCopy')", icon="Crosstalk.png")
colorMenu.addCommand('Contrast TL', f"nuke.createNode('{prefixNST}Contrast')", icon="ColorCorrect.png")
colorMenu.addCommand('GradeLayerPass TL', f"nuke.createNode('{prefixNST}GradeLayerPass')", icon="Grade.png")
colorMenu.addCommand('HighlightSuppress TL', f"nuke.createNode('{prefixNST}HighlightSuppress')", icon="ColorLookup.png")
colorMenu.addCommand('ShadowMult TL', f"nuke.createNode('{prefixNST}ShadowMult')", icon="SpotLight.png")
colorMenu.addCommand('WhiteSoftClip TL', f"nuke.createNode('{prefixNST}WhiteSoftClip')", icon="SoftClip.png")
colorMenu.addCommand('WhiteBalance TL', f"nuke.createNode('{prefixNST}WhiteBalance')", icon="HueShift.png")


colorMenu.addSeparator()

colorMenu.addCommand('apColorSampler AP', f'nuke.createNode("{prefixNST}ColorSampler")', icon='ColorSampler.png')
colorMenu.addCommand('apVignette AP', f'nuke.createNode("{prefixNST}apVignette")', icon='apeVignette.png')
colorMenu.addCommand('GammaPlus MJT', f"nuke.createNode('{prefixNST}GammaPlus')", icon="GammaPlus.png")
colorMenu.addCommand('MonochromePlus CF', f"nuke.createNode('{prefixNST}MonochromePlus')", icon="Saturation.png")
colorMenu.addCommand('aeRelight2D AE', f"nuke.createNode('{prefixNST}aeRelight2D')", icon="ReLight.png")

colorMenu.addSeparator()

colorMenu.addCommand('Suppress_RGBCMY SPIN', f'nuke.createNode("{prefixNST}Suppress_RGBCMY")', icon='spin_tools.png')
colorMenu.addCommand('BiasedSaturation NKPD', f"nuke.createNode('{prefixNST}BiasedSaturation')", icon="Saturation.png")
colorMenu.addCommand('HSL_Tool NKPD', f"nuke.createNode('{prefixNST}HSL_Tool')", icon="HSVTool.png")

############################################################################################################
############################################################################################################

# Create Filter Menu

filterMenu = NST_menu.addMenu('Filter', icon = 'ToolbarFilter.png', index = 60)

glowMenu = filterMenu.addMenu("Glows", icon="Glow.png")
glowMenu.addCommand('apGlow AP', f'nuke.createNode("{prefixNST}apeGlow")', icon='apGlow.png')
glowMenu.addCommand('ExponGlow TL', f'nuke.createNode("{prefixNST}ExponGlow")', icon='Glow.png')
glowMenu.addCommand('Glow_Exponential SPIN', f'nuke.createNode("{prefixNST}Glow_Exponential")', icon="spin_tools.png")
glowMenu.addCommand('bm_OpticalGlow BM', f"nuke.createNode('{prefixNST}bm_OpticalGlow')", icon='bm_OpticalGlow_icon.png')

filterMenu.addSeparator()

BlurMenu = filterMenu.addMenu("Blurs", icon="Median.png")

BlurMenu.addCommand('ExponBlurSimple TL', f"nuke.createNode('{prefixNST}ExponBlurSimple')", icon="Glow.png")
BlurMenu.addCommand('DirectionalBlur TL', f"nuke.createNode('{prefixNST}DirectionalBlur')", icon="DirBlur.png")
BlurMenu.addCommand('MotionBlurPaint AG', f"nuke.createNode('{prefixNST}MotionBlurPaint')", icon="MotionBlur2D.png")
BlurMenu.addCommand('iBlur NKPD', f"nuke.createNode('{prefixNST}iBlurU')", icon="Blur.png")
BlurMenu.addCommand("WaveletBlur MHD", f"nuke.createNode('{prefixNST}WaveletBlur')", icon="h_tools.png")

filterMenu.addSeparator()

EdgesMenu = filterMenu.addMenu("Edges", icon="FilterErode.png")
EdgesMenu.addCommand('apEdgePush AP', f'nuke.createNode("{prefixNST}apEdgePush")', icon='apEdgePush.png')
EdgesMenu.addCommand('apEdgeCrush AP', f'nuke.createNode("{prefixNST}apEdgeCrush")', icon='Dither.png')
EdgesMenu.addCommand('EdgeDetectAlias TL', f"nuke.createNode('{prefixNST}EdgeDetectAlias')", icon="FilterErod.png")
EdgesMenu.addCommand('AntiAliasingFilter AG', f"nuke.createNode('{prefixNST}AntiAliasingFilter')", icon="nukepedia_icon.png")
EdgesMenu.addCommand('ErodeSmooth TL', f"nuke.createNode('{prefixNST}ErodeSmooth')", icon="FilterErode.png")
EdgesMenu.addCommand('iErode PP', f"nuke.createNode('{prefixNST}iErode')", icon="FilterErode.png")
EdgesMenu.addCommand('Edge_RimLight AG', f"nuke.createNode('{prefixNST}Edge_RimLight')", icon="nukepedia_icon.png")
EdgesMenu.addCommand('EdgeDetectPRO AG', f"nuke.createNode('{prefixNST}EdgeDetectPRO')", icon="nukepedia_icon.png")
EdgesMenu.addCommand('Erode_Fine SPIN', f"nuke.createNode('{prefixNST}Erode_Fine')", icon="spin_tools.png")
EdgesMenu.addCommand('Edge_Expand SPIN', f"nuke.createNode('{prefixNST}Edge_Expand')", icon="spin_tools.png")
EdgesMenu.addCommand('Edge RB', f"nuke.createNode('{prefixNST}Edge')", icon="nukepedia_icon.png")
EdgesMenu.addCommand('KillOutline NKPD', f"nuke.createNode('{prefixNST}KillOutline')", icon="nukepedia_icon.png")
EdgesMenu.addCommand('ColorSmear NKPD', f"nuke.createNode('{prefixNST}ColorSmear')", icon="nukepedia_icon.png")
EdgesMenu.addCommand('EdgeFromAlpha FR', f"nuke.createNode('{prefixNST}EdgeFromAlpha')", icon="nukepedia_icon.png")
EdgesMenu.addCommand('VectorExtendEdge NKPD', f"nuke.createNode('{prefixNST}VectorExtendEdge')", icon="nukepedia_icon.png")
EdgesMenu.addCommand('GuidedBlur RF', f"nuke.createNode('{prefixNST}GuidedBlur')", icon="edgeBlur.png")
EdgesMenu.addSeparator()
EdgesMenu.addCommand('FractalBlur NKPD', f"nuke.createNode('{prefixNST}FractalBlur')", icon="nukepedia_icon.png")

filterMenu.addSeparator()

distortMenu = filterMenu.addMenu("Distortions", icon="IDistort.png")
distortMenu.addCommand('Glass FR', f"nuke.createNode('{prefixNST}Glass')", icon="nukepedia_icon.png")
distortMenu.addCommand('HeatWave DB', f"nuke.createNode('{prefixNST}HeatWave')", icon="HeatWave_Icon.png")
distortMenu.addCommand("X_Distort XM", f"nuke.createNode('{prefixNST}X_Distort')", icon="X_Distort.png")

filterMenu.addSeparator()

X_ToolsMenu = filterMenu.addMenu("X_Tools XM", icon="X_Tools.png")
X_ToolsMenu.addCommand("X_Aton_Volumetrics XM", f"nuke.createNode('{prefixNST}X_Aton_Volumetrics')", icon="X_Aton.png")
X_ToolsMenu.addCommand("X_Denoise XM", f"nuke.createNode('{prefixNST}X_Denoise')", icon="X_Denoise.png")
X_ToolsMenu.addCommand("X_Sharpen XM", f"nuke.createNode('{prefixNST}X_Sharpen')", icon="X_Sharpen.png")
X_ToolsMenu.addCommand("X_Soften XM", f"nuke.createNode('{prefixNST}X_Soften')", icon="X_Soften.png")

filterMenu.addSeparator()

filterMenu.addCommand('BeautifulSkin TL', f"nuke.createNode('{prefixNST}BeautifulSkin')", icon="Median.png")
filterMenu.addCommand('BlacksExpon TL', f"nuke.createNode('{prefixNST}BlacksExpon')", icon="Toe.png")
filterMenu.addCommand('aeShadows AE', f"nuke.createNode('{prefixNST}aeShadows')", icon="aeShadows_icon.png")
filterMenu.addCommand('Halation TL', f"nuke.createNode('{prefixNST}Halation')", icon="EdgeBlur.png")
filterMenu.addCommand('HighPass TL', f"nuke.createNode('{prefixNST}HighPass')", icon="Invert.png")
filterMenu.addCommand('Diffusion TL', f"nuke.createNode('{prefixNST}Diffusion')", icon="Spark.png")

filterMenu.addSeparator()

filterMenu.addCommand('LightWrapPro TL', f"nuke.createNode('{prefixNST}LightWrapPro')", icon="LightWrap.png")
filterMenu.addCommand('bm_Lightwrap BM', f"nuke.createNode('{prefixNST}bm_Lightwrap')", icon="bm_Lightwrap_icon.png")

filterMenu.addSeparator()

filterMenu.addCommand('iConvolve AP', f'nuke.createNode("{prefixNST}iConvolve")', icon='ap_tools.png')
filterMenu.addCommand('ConvolutionMatrix AG', f'nuke.createNode("{prefixNST}ConvolutionMatrix")', icon="ColorMatrix.png")

#Add apChroma submenu
apChromaMenu = filterMenu.addMenu("apChroma Tools AP", icon="apChroma.png")
apChromaMenu.addCommand('apChroma AP', f'nuke.createNode("{prefixNST}apChroma")', icon='apChroma.png')
apChromaMenu.addCommand('apChromaMerge AP', f'nuke.createNode("{prefixNST}apChromaMergeNew")', icon='apChroma.png')
apChromaMenu.addCommand('apChromaBlur AP', f'nuke.createNode("{prefixNST}apChromaBlurNew")', icon='apChroma.png')
apChromaMenu.addCommand('apChromaTransform AP', f'nuke.createNode("{prefixNST}apChromaTransformNew")', icon='apChroma.png')
apChromaMenu.addCommand('apChromaUnpremult AP', f'nuke.createNode("{prefixNST}apChromaUnpremult")', icon='apChroma.png')
apChromaMenu.addCommand('apChromaPremult AP', f'nuke.createNode("{prefixNST}apChromaPremult")', icon='apChroma.png')

filterMenu.addSeparator()

filterMenu.addCommand('Chromatik SPIN', f"nuke.createNode('{prefixNST}Chromatik')", icon='spin_tools.png')
filterMenu.addCommand('ChromaticAberration fxT', f"nuke.createNode('{prefixNST}fxT_ChromaticAberration')", icon='ColorLookup.png')
filterMenu.addCommand("ChromaSmear LJ", f"nuke.createNode('{prefixNST}ChromaSmear')", icon="ColorLookup.png")

filterMenu.addSeparator()

filterMenu.addCommand('CatsEyeDefocus NKPD', f"nuke.createNode('{prefixNST}CatsEyeDefocus')", icon="nukepedia_icon.png")
filterMenu.addCommand('DefocusSwirlyBokeh NKPD', f"nuke.createNode('{prefixNST}DefocusSwirlyBokeh')", icon="nukepedia_icon.png")
filterMenu.addCommand('deHaze NKPD', f"nuke.createNode('{prefixNST}deHaze')", icon="nukepedia_icon.png")
filterMenu.addCommand('RankFilter JP', f"nuke.createNode('{prefixNST}RankFilter')", icon="Median.png")
filterMenu.addCommand('RadialDilate CF', f"nuke.createNode('{prefixNST}RadialDilate')", icon="ErodeFast.png")
filterMenu.addCommand('DeflickerVelocity NKPD', f"nuke.createNode('{prefixNST}DeflickerVelocity')", icon="nukepedia_icon.png")
filterMenu.addCommand('FillSampler NKPD', f"nuke.createNode('{prefixNST}FillSampler')", icon="nukepedia_icon.png")
filterMenu.addCommand('MECfiller NKPD', f"nuke.createNode('{prefixNST}MECfiller')", icon="nukepedia_icon.png")

############################################################################################################
############################################################################################################

# Create Keyer Menu
keyerMenu = NST_menu.addMenu('Keyer', icon = 'ToolbarKeyer.png', index = 70)

keyerMenu.addCommand('apDespill AP', f'nuke.createNode("{prefixNST}apDespill_v2")', icon='apDespill.png')
keyerMenu.addCommand('SpillCorrect SPIN', f"nuke.createNode('{prefixNST}Spill_Correct')", icon='spin_tools.png')
keyerMenu.addCommand('DespillToColor NKPD', f"nuke.createNode('{prefixNST}DespillToColor')", icon="nukepedia_icon.png")

keyerMenu.addSeparator()

keyerMenu.addCommand('AdditiveKeyerPro TL', f"nuke.createNode('{prefixNST}AdditiveKeyerPro')", icon="Bilateral.png")
keyerMenu.addCommand('apScreenClean AP', f'nuke.createNode("{prefixNST}apeScreenClean")', icon='apScreenClean.png')
keyerMenu.addCommand('apScreenGrow AP', f'nuke.createNode("{prefixNST}apeScreenGrow")', icon='apScreenGrow.png')

keyerMenu.addSeparator()

keyerMenu.addCommand('KeyChew NKPD', f"nuke.createNode('{prefixNST}KeyChew')", icon="Keyer.png")
keyerMenu.addCommand('LumaKeyer DR', f"nuke.createNode('{prefixNST}LumaKeyer')", icon="Keyer.png")
keyerMenu.addCommand('PointCloudKeyer IS', f"nuke.createNode('{prefixNST}PointCloudKeyer')", icon="PointCloudGenerator.png")

############################################################################################################
############################################################################################################

# Create Merge Menu
mergeMenu = NST_menu.addMenu('Merge', icon = 'ToolbarMerge.png', index = 80)

mergeMenu.addCommand('ContactSheetAuto TL', f"nuke.createNode('{prefixNST}ContactSheetAuto')", icon="ContactSheet.png")
mergeMenu.addCommand('KeymixBBox TL', f"nuke.createNode('{prefixNST}KeymixBBox')", icon="Keymix.png")
mergeMenu.addCommand('MergeAtmos TL', f"nuke.createNode('{prefixNST}MergeAtmos')", icon="PointCloudMesh.png")
mergeMenu.addCommand('MergeBlend TL', f"nuke.createNode('{prefixNST}MergeBlend')", icon="Dissolve.png")

mergeMenu.addSeparator()

mergeMenu.addCommand('MergeAll AP', f"nuke.createNode('{prefixNST}MergeAll')", icon="Merge.png")

############################################################################################################
############################################################################################################

# Create Transform Menu
transformMenu = NST_menu.addMenu('Transform', icon = 'ToolbarTransform.png', index = 90)

# Add Vector Tools SubMenu
VMTmenu = transformMenu.addMenu('Vector Math Tools VM', icon = 'Math.png')

VMT_mathMenu = VMTmenu.addMenu('Math', icon = 'Math.png')
VMT_mathAxisMenu = VMT_mathMenu.addMenu('Axis', icon = 'Axis.png')
VMT_mathMatrixFourMenu = VMT_mathMenu.addMenu('Matrix4', icon = 'Matrix4.png')
VMT_mathVectorTwoMenu = VMT_mathMenu.addMenu('Vector2', icon = 'Vector2.png')
VMT_mathVectorThreeMenu = VMT_mathMenu.addMenu('Vector3', icon = 'Vector3.png')

VMT_mathAxisMenu.addCommand('Invert Axis', f"nuke.createNode('{prefixNST}InvertAxis')", icon = 'Axis.png')
VMT_mathAxisMenu.addCommand('Zero Axis', f"nuke.createNode('{prefixNST}ZeroAxis')", icon = 'Axis.png')

VMT_mathMatrixFourMenu.addCommand('Invert Matrix4', f"nuke.createNode('{prefixNST}InvertMatrix4')", icon = 'InvertMatrix4.png')
VMT_mathMatrixFourMenu.addCommand('Product Matrix4', f"nuke.createNode('{prefixNST}ProductMatrix4')", icon = 'ProductMatrix4.png')
VMT_mathMatrixFourMenu.addCommand('Rotate Matrix4', f"nuke.createNode('{prefixNST}RotateMatrix4')", icon = 'RotateMatrix4.png')
VMT_mathMatrixFourMenu.addCommand('Scale Matrix4', f"nuke.createNode('{prefixNST}ScaleMatrix4')", icon = 'ScaleMatrix4.png')
VMT_mathMatrixFourMenu.addCommand('Transform Matrix4', f"nuke.createNode('{prefixNST}TransformMatrix4')", icon = 'TransformMatrix4.png')
VMT_mathMatrixFourMenu.addCommand('Translate Matrix4', f"nuke.createNode('{prefixNST}TranslateMatrix4')", icon = 'TranslateMatrix4.png')
VMT_mathMatrixFourMenu.addCommand('Transpose Matrix4', f"nuke.createNode('{prefixNST}TransposeMatrix4')", icon = 'TransposeMatrix4.png')

VMT_mathVectorTwoMenu.addCommand('Cross Product Vector2', f"nuke.createNode('{prefixNST}CrossProductVector2')", icon = 'CrossProductVector3.png')
VMT_mathVectorTwoMenu.addCommand('Dot Product Vector2', f"nuke.createNode('{prefixNST}DotProductVector2')", icon = 'DotProductVector3.png')
VMT_mathVectorTwoMenu.addCommand('Magnitude Vector2', f"nuke.createNode('{prefixNST}MagnitudeVector2')", icon = 'MagnitudeVector3.png')
VMT_mathVectorTwoMenu.addCommand('Normalize Vector2', f"nuke.createNode('{prefixNST}NormalizeVector2')", icon = 'NormalizeVector3.png')
VMT_mathVectorTwoMenu.addCommand('Rotate Vector2', f"nuke.createNode('{prefixNST}RotateVector2')", icon = 'RotateVector3.png')
VMT_mathVectorTwoMenu.addCommand('Transform Vector2', f"nuke.createNode('{prefixNST}TransformVector2')", icon = 'TransformVector3.png')

VMT_mathVectorThreeMenu.addCommand('Cross Product Vector3', f"nuke.createNode('{prefixNST}CrossProductVector3')", icon = 'CrossProductVector3.png')
VMT_mathVectorThreeMenu.addCommand('Dot Product Vector3', f"nuke.createNode('{prefixNST}DotProductVector3')", icon = 'DotProductVector3.png')
VMT_mathVectorThreeMenu.addCommand('Magnitude Vector3', f"nuke.createNode('{prefixNST}MagnitudeVector3')", icon = 'MagnitudeVector3.png')
VMT_mathVectorThreeMenu.addCommand('Multiply Vector3 Matrix3', f"nuke.createNode('{prefixNST}MultiplyVector3Matrix3')", icon = 'ProductVector3.png')
VMT_mathVectorThreeMenu.addCommand('Normalize Vector3', f"nuke.createNode('{prefixNST}NormalizeVector3')", icon = 'NormalizeVector3.png')
VMT_mathVectorThreeMenu.addCommand('Rotate Vector3', f"nuke.createNode('{prefixNST}RotateVector3')", icon = 'RotateVector3.png')
VMT_mathVectorThreeMenu.addCommand('Transform Vector3', f"nuke.createNode('{prefixNST}TransformVector3')", icon = 'TransformVector3.png')

VMT_generateMenu = VMTmenu.addMenu('Generate', icon = 'IdentityMatrix4.png')
VMT_generateMenu.addCommand('Generate Matrix4', f"nuke.createNode('{prefixNST}GenerateMatrix4')", icon = 'IdentityMatrix4.png')
VMT_generateMenu.addCommand('Generate STMap', f"nuke.createNode('{prefixNST}GenerateSTMap')", icon = 'AG_UVMap.png')

VMT_convertMenu = VMTmenu.addMenu('Convert', icon = 'ProductVector3.png')
VMT_convertMenu.addCommand('Luma To Vector3', f"nuke.createNode('{prefixNST}LumaToVector3')", icon = 'vectorToolsBW.png')
VMT_convertMenu.addCommand('STMap To Vector2', f"nuke.createNode('{prefixNST}STMapToVector2')", icon = 'Vector2.png')
VMT_convertMenu.addCommand('Vector2 To STMap', f"nuke.createNode('{prefixNST}Vector2ToSTMap')", icon = 'AG_UVMap.png')
VMT_convertMenu.addCommand('Vector3 To Matrix4', f"nuke.createNode('{prefixNST}Vector3ToMatrix4')", icon = 'ProductVector3.png')

transformMenu.addCommand('vector3DMathExpression EL', f"nuke.createNode('{prefixNST}vector3DMathExpression')", icon = 'vectorTools.png')
transformMenu.addCommand('Vectors_Direction EL', f"nuke.createNode('{prefixNST}Vectors_Direction')", icon = 'vectorTools.png')
transformMenu.addCommand('Vectors_to_Degrees EL', f"nuke.createNode('{prefixNST}Vectors_to_Degrees')", icon = 'vectorTools.png')

# Add VectorTracker python file
try:
    nuke.load(f'{prefixNST}VectorTracker.py')
    transformMenu.addCommand('VectorTracker NKPD', f"nuke.createNode('{prefixNST}VectorTracker.gizmo')", icon = 'vectorTools.png')
except RuntimeError as e:
    print(f"Could not load VectorTracker.py: {e}")
    pass

transformMenu.addSeparator()


transformMenu.addCommand('AutoCropTool TL', f"nuke.createNode('{prefixNST}AutoCropTool')", icon="AutoCrop.png")
transformMenu.addCommand('BBoxToFormat TL', f"nuke.createNode('{prefixNST}BBoxToFormat')", icon="Rectangle.png")
transformMenu.addCommand('ImagePlane3D TL', f"nuke.createNode('{prefixNST}ImagePlane3D')", icon="Card.png")
transformMenu.addCommand('Matrix_Inverse TL', f"nuke.createNode('{prefixNST}Matrix4x4_Inverse')", icon="ColorMatrix.png")
transformMenu.addCommand('Matrix4x4Math TL', f"nuke.createNode('{prefixNST}Matrix4x4Math')", icon="ColorMath.png")
transformMenu.addCommand('MirrorBorder TL', f"nuke.createNode('{prefixNST}MirrorBorder')", icon="AdjBBox.png")
transformMenu.addCommand('TransformCutOut TL', f"nuke.createNode('{prefixNST}TransformCutOut')", icon="MergeOut.png")
transformMenu.addCommand('iMorph AP', f"nuke.createNode('{prefixNST}iMorph')", icon="VectorDistort.png")
transformMenu.addCommand('Symmetry TL', f"nuke.createNode('{prefixNST}Symmetry')", icon="Convolve.png")

transformMenu.addSeparator()

transformMenu.addCommand('RP_Reformat MJT', f"nuke.createNode('{prefixNST}RP_Reformat')", icon='RP_Reformat.png')
transformMenu.addCommand('InverseMatrix3x3 MJT', f"nuke.createNode('{prefixNST}InverseMatrix33')", icon='iMatrix33.png')
transformMenu.addCommand('InverseMatrix4x4 MJT', f"nuke.createNode('{prefixNST}InverseMatrix44')", icon='iMatrix44.png')

transformMenu.addSeparator()

try:
    import NST_cardToTrack
    transformMenu.addCommand('CardToTrack AK', f"nuke.createNode('{prefixNST}CardToTrack')", icon='Card.png')
except ImportError as e:
    print(f"Could not load NST_cardToTrack.py: {e}")
    pass

transformMenu.addCommand('CProject AK', f"nuke.createNode('{prefixNST}CProject')", icon='CornerPin.png')
transformMenu.addCommand('TProject AK', f"nuke.createNode('{prefixNST}TProject')", icon='Transform.png')

transformMenu.addCommand("StickIt MHD", f"nuke.createNode('{prefixNST}h_stickit')", icon="h_stickit.png")
transformMenu.addSeparator()

transformMenu.addCommand('TransformMatrix AG', f"nuke.createNode('{prefixNST}TransformMatrix')", icon="Transform.png")
transformMenu.addCommand('CornerPin2D_Matrix AG', f"nuke.createNode('{prefixNST}CornerPin2D_Matrix')", icon="CornerPin.png")
transformMenu.addCommand('RotoPaintTransform AG', f"nuke.createNode('{prefixNST}RotoPaintTransform')", icon="RotoPaint.png")

transformMenu.addSeparator()

transformMenu.addCommand('IIDistort EL', f"nuke.createNode('{prefixNST}IIDistort')", icon="nukepedia_icon.png")
transformMenu.addCommand('bm_CameraShake BM', f"nuke.createNode('{prefixNST}bm_CameraShake')", icon="bm_CameraShake_icon.png")
transformMenu.addCommand('ITransform AE', f"nuke.createNode('{prefixNST}iTransform_ae')", icon="STMap.png")
transformMenu.addCommand('MorphDissolve SPIN', f"nuke.createNode('{prefixNST}MorphDissolve')", icon="spin_tools.png")
transformMenu.addCommand('RotoCentroid NKPD', f"nuke.createNode('{prefixNST}RotoCentroid')", icon="nukepedia_icon.png")
transformMenu.addCommand('STmapInverse NKPD', f"nuke.createNode('{prefixNST}STmapInverse')", icon="nukepedia_icon.png")
transformMenu.addCommand('TransformMix NKPD', f"nuke.createNode('{prefixNST}TransformMix')", icon="Transform.png")
transformMenu.addCommand('PlanarProjection NKPD', f"nuke.createNode('{prefixNST}PlanarProjection')", icon="nukepedia_icon.png")
transformMenu.addCommand('Reconcile3DFast DR', f"nuke.createNode('{prefixNST}Reconcile3DFast')", icon="Reconcile3D.png")

############################################################################################################
############################################################################################################

# Create 3D Menu

ThreeDMenu = NST_menu.addMenu('3D', icon = 'Toolbar3D.png', index = 100)

ThreeDMenu.addCommand('aPCard AP', f'nuke.createNode("{prefixNST}aPCard")', icon='ap_tools.png')
ThreeDMenu.addCommand('DummyCam', f'nuke.createNode("{prefixNST}DummyCam")', icon='DummyCam.png')

ThreeDMenu.addSeparator()

ThreeDMenu.addCommand('mScatterGeo MJT', f'nuke.createNode("{prefixNST}mScatterGeo")', icon='mScatterGeo.png')
ThreeDMenu.addCommand('GeoToPoints MHD', f"nuke.createNode('{prefixNST}GeoToPoints')", icon="nukepedia_icon.png")
ThreeDMenu.addCommand('origami MJT', f'nuke.createNode("{prefixNST}origami")', icon='origami.png')
ThreeDMenu.addCommand('RayDeepAO MJT', f'nuke.createNode("{prefixNST}RayDeepAO")', icon='RayDeepAO.png')
ThreeDMenu.addCommand('SceneDepthCalculator MJT', f'nuke.createNode("{prefixNST}SceneDepthCalculator")', icon='SceneDepthCalculator.png')
ThreeDMenu.addCommand('SSMesh MJT', f'nuke.createNode("{prefixNST}SSMesh")', icon='SSMesh.png')
ThreeDMenu.addCommand('Unify3DCoordinate MJT', f'nuke.createNode("{prefixNST}Unify3DCoordinate")', icon='Unify3DCoordinate.png')
ThreeDMenu.addCommand('UVEditor MJT', f'nuke.createNode("{prefixNST}UVEditor")', icon='UVEditor.png')

ThreeDMenu.addSeparator()

ThreeDMenu.addCommand('Distance3D NKPD', f"nuke.createNode('{prefixNST}Distance3D')", icon="nukepedia_icon.png")
ThreeDMenu.addCommand('DistanceBetween_CS NKPD', f"nuke.createNode('{prefixNST}DistanceBetween_CS')", icon="nukepedia_icon.png")
ThreeDMenu.addCommand('Lightning3D EL', f"nuke.createNode('{prefixNST}Lightning3D')", icon="nukepedia_icon.png")
ThreeDMenu.addCommand('Noise3DTexture NKPD', f"nuke.createNode('{prefixNST}Noise3DTexture')", icon="noise3dicon.png")
ThreeDMenu.addCommand('GodRaysProjector CF', f"nuke.createNode('{prefixNST}GodRaysProjector')", icon="VolumeRays.png")
ThreeDMenu.addCommand('MirrorDimension TL', f"nuke.createNode('{prefixNST}MirrorDimension')", icon="Mirror.png")

############################################################################################################
############################################################################################################

# Create Paricles Menu

particlesMenu = NST_menu.addMenu('Particles', icon = 'ToolbarParticles.png', index = 110)

particlesMenu.addCommand('waterSchmutz DR', f"nuke.createNode('{prefixNST}waterSchmutz')", icon="WaterLens.png")
particlesMenu.addCommand('RainMaker MR', f"nuke.createNode('{prefixNST}RainMaker')", icon="ParticleDrag.png")
particlesMenu.addCommand('Sparky DB', f"nuke.createNode('{prefixNST}Sparky')", icon="Sparky.png")
particlesMenu.addCommand('ParticleLights MHD', f"nuke.createNode('{prefixNST}ParticleLights')", icon="ToolbarParticles.png")
particlesMenu.addCommand('ParticleKiller NKPD', f"nuke.createNode('{prefixNST}ParticleKiller')", icon="ToolbarParticles.png")


############################################################################################################
############################################################################################################

# Create Deep Menu

deepMenu = NST_menu.addMenu('Deep', icon = 'ToolbarDeep.png', index = 120)

deep2VP_suite = deepMenu.addMenu("Deep2VP Suite MJT", icon='Deep2VP.png')

deep2VP_suite.addCommand('Deep2VP MJT', f"nuke.createNode('{prefixNST}Deep2VP')", icon="Deep2VP.png")
deep2VP_suite.addCommand('DVPColorCorrect MJT', f"nuke.createNode('{prefixNST}DVPColorCorrect')", icon="DVPColorCorrect.png")
deep2VP_suite.addCommand('DVPortal MJT', f"nuke.createNode('{prefixNST}DVPortal')", icon="DVPortal.png")
deep2VP_suite.addCommand('DVPToImage MJT', f"nuke.createNode('{prefixNST}DVPToImage')", icon="DVPToImage.png")

deep2VP_suite.addSeparator()

deep2VP_suite.addCommand('DVPfresnel MJT', f"nuke.createNode('{prefixNST}DVPfresnel')", icon="DVPfresnel.png")
deep2VP_suite.addCommand('DVPrelight MJT', f"nuke.createNode('{prefixNST}DVPrelight')", icon="DVPrelight.png")
deep2VP_suite.addCommand('DVPrelightPT MJT', f"nuke.createNode('{prefixNST}DVPrelightPT')", icon="DVPrelightPT.png")
deep2VP_suite.addCommand('DVPscene MJT', f"nuke.createNode('{prefixNST}DVPscene')", icon="DVPscene.png")
deep2VP_suite.addCommand('DVPsetLight MJT', f"nuke.createNode('{prefixNST}DVPsetLight')", icon="DVPsetLight.png")

deep2VP_suite.addSeparator()

deep2VP_suite.addCommand('DVPattern MJT', f"nuke.createNode('{prefixNST}DVPattern')", icon="DVPattern.png")
deep2VP_suite.addCommand('DVPmatte MJT', f"nuke.createNode('{prefixNST}DVPmatte')", icon="DVPmatte.png")
deep2VP_suite.addCommand('DVProjection MJT', f"nuke.createNode('{prefixNST}DVProjection')", icon="DVProjection.png")

deep2VP_suite.addSeparator()

deep2VP_suite.addCommand('DVP_ToonShader MJT', f"nuke.createNode('{prefixNST}DVP_ToonShader')", icon="DVP_ToonShader.png")
deep2VP_suite.addCommand('DVP_Shader MJT', f"nuke.createNode('{prefixNST}DVP_Shader')", icon="DVP_Shader.png")

deepMenu.addSeparator()

deepMenu.addCommand('DeepBoolean MJT', f"nuke.createNode('{prefixNST}DeepBoolean')", icon="DeepBoolean.png")
deepMenu.addCommand('DeepFromPosition MJT', f"nuke.createNode('{prefixNST}DeepFromPosition')", icon="DeepFromPosition.png")
deepMenu.addCommand('DeepSampleCount MJT', f"nuke.createNode('{prefixNST}DeepSampleCount')", icon="DeepSampleCount.png")
deepMenu.addCommand('DeepSer MJT', f"nuke.createNode('{prefixNST}DeepSer')", icon="DeepSer.png")

deepMenu.addSeparator()

deepMenu.addCommand('DeepFromDepth AG', f"nuke.createNode('{prefixNST}DeepFromDepth')", icon="DeepRecolor.png")
deepMenu.addCommand('DeepToPosition TL', f"nuke.createNode('{prefixNST}DeepToPosition')", icon="Deep2VPosition.png")
deepMenu.addCommand('DeepRecolorMatte TL', f"nuke.createNode('{prefixNST}DeepRecolorMatte')", icon="DeepRecolor.png")

deepMenu.addSeparator()
deepMenu.addCommand('Deep Thickness AG', f'nuke.nodePaste("{nk_path("deepThickness.nk")}")')
deepMenu.addCommand('DeepMerge_Advanced BM', f"nuke.createNode('{prefixNST}DeepMerge_Advanced')", icon="DeepMerge.png")
deepMenu.addCommand('DeepCropSoft NKPD', f"nuke.createNode('{prefixNST}DeepCropSoft')", icon="DeepCrop.png")
deepMenu.addCommand('DeepKeyMix NKPD', f"nuke.createNode('{prefixNST}DeepKeyMix')", icon="DeepMerge.png")
deepMenu.addCommand('DeepHoldoutSmoother NKPD', f"nuke.createNode('{prefixNST}DeepHoldoutSmoother')", icon="DeepHoldout.png")
deepMenu.addCommand('DeepCopyBBox NKPD', f"nuke.createNode('{prefixNST}DeepCopyBBox')", icon="DeepMerge.png")


############################################################################################################
############################################################################################################

# Create CG Menu

cgMenu = NST_menu.addMenu('CG', icon = 'RenderManShader.png', index = 130)

cgMenu.addCommand('UV Mapper TL', f"nuke.createNode('{prefixNST}UV_Mapper')", icon="Tile.png")

cgMenu.addSeparator()

PNZsuite = cgMenu.addMenu('PNZsuite MJT', icon = 'ConvertPNZ.png')
PNZsuite.addCommand('ConvertPNZ MJT', f'nuke.createNode("{prefixNST}ConvertPNZ")', icon='ConvertPNZ.png')
PNZsuite.addCommand('P2N MJT', f'nuke.createNode("{prefixNST}P2N")', icon='P2N.png')
PNZsuite.addCommand('P2Z MJT', f'nuke.createNode("{prefixNST}P2Z")', icon='P2Z.png')
PNZsuite.addCommand('Z2N MJT', f'nuke.createNode("{prefixNST}Z2N")', icon='Z2N.png')
PNZsuite.addCommand('Z2P MJT', f'nuke.createNode("{prefixNST}Z2P")', icon='Z2P.png')

PosToolkit = cgMenu.addMenu('PosToolkit MJT', icon = 'PosMatte_MJ.png')
PosToolkit.addCommand('PosMatte MJT', f'nuke.createNode("{prefixNST}PosMatte_MJ")', icon='PosMatte_MJ.png')
PosToolkit.addCommand('PosPattern MJT', f'nuke.createNode("{prefixNST}PosPattern_MJ")', icon='PosPattern_MJ.png')
PosToolkit.addCommand('PosProjection MJT', f'nuke.createNode("{prefixNST}PosProjection_MJ")', icon='PosProjection_MJ.png')

cgMenu.addSeparator()

cgMenu.addCommand('Noise_3D SPIN', f'nuke.createNode("{prefixNST}Noise3D_spin")', icon='spin_tools.png')
cgMenu.addCommand('Noise4D MHD', f'nuke.nodePaste("{nk_path("Noise4D.nk", prefix=True)}")', icon='Noise.png')
cgMenu.addCommand('Relight_Simple SPIN', f'nuke.createNode("{prefixNST}Relight_Simple")', icon='spin_tools.png')
cgMenu.addCommand('ReProject_3D SPIN', f'nuke.createNode("{prefixNST}ReProject_3D")', icon='spin_tools.png')


cgMenu.addSeparator()

cgMenu.addCommand('C44Kernel AP', f'nuke.createNode("{prefixNST}C44Kernel")', icon='C44Kernel.png')
cgMenu.addCommand('apDirLight AP', f'nuke.createNode("{prefixNST}apDirLight")', icon='apDirLight.png')
cgMenu.addCommand('apFresnel AP', f'nuke.createNode("{prefixNST}apFresnel")', icon='ap_tools.png')
cgMenu.addCommand('CameraNormals NKPD', f"nuke.createNode('{prefixNST}CameraNormals')", icon="Camera.png")
cgMenu.addCommand('NormalsRotate NKPD', f"nuke.createNode('{prefixNST}NormalsRotate')", icon="SpotLight.png")
cgMenu.addCommand('Relight_bb NKPD', f"nuke.createNode('{prefixNST}Relight_bb')", icon="SpotLight.png")
cgMenu.addCommand('EnvReflect_bb NKPD', f"nuke.createNode('{prefixNST}EnvReflect_BB')", icon="Sphere.png")
cgMenu.addCommand('N_Reflection NKPD', f"nuke.createNode('{prefixNST}N_Reflection')", icon="Sphere.png")
cgMenu.addCommand('aeRefracTHOR AE', f"nuke.createNode('{prefixNST}aeRefracTHOR')", icon="aeRefracTHOR_icon.png")
cgMenu.addCommand('Emission NW', f"nuke.createNode('{prefixNST}Emission')", icon="Light.png")
cgMenu.addCommand('SimpleSSS MHD', f"nuke.createNode('{prefixNST}SimpleSSS')", icon="Toolbar3D.png")

cgMenu.addSeparator()

cgMenu.addCommand('aPmatte AP', f'nuke.createNode("{prefixNST}aPMatte_v2")', icon='aPmatte.png')
cgMenu.addCommand('P_Ramp NKPD', f"nuke.createNode('{prefixNST}F_P_Ramp')", icon="F_pramp.png")
cgMenu.addCommand('P_Project NKPD', f"nuke.createNode('{prefixNST}F_P_Project')", icon="F_pproject.png")
cgMenu.addCommand('Glue_P LS', f"nuke.createNode('{prefixNST}GlueP')", icon="PosProjection_MJ.png")
cgMenu.addCommand('P_Noise_Advanced NKPD', f"nuke.createNode('{prefixNST}P_Noise_Advanced')", icon="Noise.png")

cgMenu.addSeparator()

cgMenu.addCommand('LightSwitch TL', f"nuke.createNode('{prefixNST}LightSwitch')", icon="Switch.png")
cgMenu.addCommand('LightSwitchPuppet TL', f'nuke.nodePaste("{nk_path("LightSwitchPuppet.nk", prefix=True)}")', icon="Switch.png")


############################################################################################################
############################################################################################################

# Create Curves Menu

curvesMenu = NST_menu.addMenu('Curves', icon = 'ParticleCurve.png', index = 140)

waveMachineMenu = curvesMenu.addMenu("Wave Machine FL", icon='waveMachine.png')
waveMachineMenu.addCommand('WaveMaker FL', f"nuke.createNode('{prefixNST}waveMaker')", icon="waveMaker.png")
waveMachineMenu.addCommand('WaveCustom FL', f"nuke.createNode('{prefixNST}waveCustom')", icon="waveCustom.png")
waveMachineMenu.addCommand('WaveGrade FL', f"nuke.createNode('{prefixNST}waveGrade')", icon="waveGrade.png")
waveMachineMenu.addCommand('WaveRetime FL', f"nuke.createNode('{prefixNST}waveRetime')", icon="waveRetime.png")
waveMachineMenu.addCommand('WaveMerge FL', f"nuke.createNode('{prefixNST}waveMerge')", icon="waveMerge.png")

curvesMenu.addSeparator()

curvesMenu.addCommand('Randomizer TL', f"nuke.createNode('{prefixNST}Randomizer')", icon="RenderMan.png")
curvesMenu.addCommand('AnimationCurve AG', f"nuke.createNode('{prefixNST}AnimationCurve')", icon="nukepedia_icon.png")
curvesMenu.addCommand('bm_CurveRemapper BM', f"nuke.createNode('{prefixNST}bm_CurveRemapper')", icon="bm_CurveRemapper_icon.png")
curvesMenu.addCommand('bm_NoiseGen BM', f"nuke.createNode('{prefixNST}bm_NoiseGen')", icon="bm_NoiseGen_icon.png")

############################################################################################################
############################################################################################################

# Create Utilities Menu

utilitiesMenu = NST_menu.addMenu('Utilities', icon = 'Modify.png', index = 150)

utilitiesMenu.addCommand('GUI Switch TL', f"nuke.createNode('{prefixNST}GUI_Switch')", icon="Switch.png")
utilitiesMenu.addCommand('NAN INF Killer TL', f"nuke.createNode('{prefixNST}NAN_INF_Killer')", icon="Assert.png")

utilitiesMenu.addSeparator()

utilitiesMenu.addCommand('apViewerBlocker AP', f'nuke.createNode("{prefixNST}apViewerBlocker")', icon='ap_tools.png')
utilitiesMenu.addCommand('Python_and_TCL AG', f'nuke.createNode("{prefixNST}Python_and_TCL")', icon="nukepedia_icon.png")

utilitiesMenu.addCommand('RotoQC NKPD', f"nuke.createNode('{prefixNST}RotoQC')", icon="Roto.png")
utilitiesMenu.addCommand('bm_MatteCheck BM', f"nuke.createNode('{prefixNST}bm_MatteCheck')", icon="bm_MatteCheck_icon.png")

utilitiesMenu.addSeparator()

utilitiesMenu.addCommand('viewer_render MJT', f'nuke.createNode("{prefixNST}viewer_render")', icon='viewer_render.png')
utilitiesMenu.addCommand('NukeZ MJT', f'nuke.createNode("{prefixNST}NukeZ")', icon='NukeZ.png')
utilitiesMenu.addCommand('Pyclopedia MJT', f'nuke.createNode("{prefixNST}Pyclopedia")', icon='Pyclopedia.png')


############################################################################################################
############################################################################################################

# Create Templates Menu

templatesMenu = NST_menu.addMenu('Templates', icon = 'PointsTo3D.png', index = 200)

templatesMenu.addCommand('Advanced Keying Template Stamps TL', f'nuke.nodePaste("{nk_path("AdvancedKeyingTemplate_Stamps.nk", prefix=True)}")', icon="Keyer.png")
templatesMenu.addCommand('Advanced Keying Template TL', f'nuke.nodePaste("{nk_path("AdvancedKeyingTemplate.nk", prefix=True)}")', icon="Keyer.png")
templatesMenu.addCommand('STMap Keyer Setup EL', f'nuke.nodePaste("{nk_path("STMap_Keying_Setup.nk", prefix=True)}")', icon="HueKeyer.png")

templatesMenu.addSeparator()

gizmoDemoMenu = templatesMenu.addMenu("Gizmo Demo Scripts", icon='Group.png')

gizmoDemoMenu.addCommand('WaterLens Demo MJT', f'NST_helper.filepathCreateNode("{nk_path("WaterLens_sampleScript.nk", prefix=True)}")', icon="WaterLens.png")
gizmoDemoMenu.addCommand('SSMesh Demo MJT', f'nuke.nodePaste("{nk_path("SSMesh_demo.nk", prefix=True)}")', icon="SSMesh.png")
gizmoDemoMenu.addCommand('UVEditor Demo MJT', f'nuke.nodePaste("{nk_path("UVEditor_demo_clean.nk", prefix=True)}")', icon="UVEditor.png")
gizmoDemoMenu.addCommand('Sparky Demo DB', f'nuke.nodePaste("{nk_path("SparkyExampleScene.nk", prefix=True)}")', icon="Sparky.png")
gizmoDemoMenu.addCommand('ParticleLights Demo MHD', f'nuke.nodePaste("{nk_path("ParticleLights_ExampleScript.nk", prefix=True)}")', icon="ToolbarParticles.png")
gizmoDemoMenu.addCommand("X_Aton Volumetric Demo XM", f'nuke.nodePaste("{nk_path("X_Aton_Examples.nk", prefix=True)}")', icon="X_Aton.png")
