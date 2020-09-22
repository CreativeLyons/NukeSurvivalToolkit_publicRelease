import sys
import nuke
import os
import webbrowser

#*****************************************************************
#*****************************************************************
#******************ADD THIS TO YOUR FILE INIT.PY******************
#Expression_path = "/Users/yourPath/.nuke/Expression"
#nuke.pluginAddPath(Expression_path)
#*****************************************************************
#*****************************************************************

Expression_path = str(os.path.dirname(__file__))


toolbar = nuke.toolbar("Nodes")
m = toolbar.addMenu("NukeSurvivalToolkit/Draw/Expression Nodes AG", icon = os.path.join(Expression_path, "icon/expr.png"), index=000 )

m.addMenu( 'Creations', icon = os.path.join(Expression_path, "icon/01.png") )
m.addMenu( 'Alpha', icon = os.path.join(Expression_path, "icon/02.png") )
m.addMenu( 'Pixel', icon = os.path.join(Expression_path, "icon/03.png") )
m.addMenu( 'Keying and Despill', icon = os.path.join(Expression_path, "icon/04.png") )
m.addMenu( 'Transform', icon = os.path.join(Expression_path, "icon/05.png") )
m.addMenu( '3D and Deep', icon = os.path.join(Expression_path, "icon/06.png") )



#CREATIONS
m.addCommand('Creations/Random/Random Colors', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Creations/Random/Random_colors.nk") + "\")")
m.addCommand('Creations/Random/Random every Frame', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Creations/Random/Random_every_frame.nk") + "\")")
m.addCommand('Creations/Random/Random every Pixel', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Creations/Random/Random_every_pixel.nk") + "\")")
m.addCommand('Creations/Noise/Noise', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Creations/Noise/Noise.nk") + "\")")
m.addCommand('Creations/Noise/fBm', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Creations/Noise/fBm.nk") + "\")")
m.addCommand('Creations/Noise/Turbulence', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Creations/Noise/turbulence.nk") + "\")")
m.addCommand('Creations/lines vertical', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Creations/Lines_Vertical.nk") + "\")")
m.addCommand('Creations/lines horizontal', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Creations/Lines_Horizontal.nk") + "\")")
m.addCommand('Creations/lines vertical animated', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Creations/Lines_Vertical_Animated.nk") + "\")")
m.addCommand('Creations/lines horizontal animated', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Creations/Lines_Horizontal_Animated.nk") + "\")")
m.addCommand('Creations/circles', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Creations/circles.nk") + "\")")
m.addCommand('Creations/circles user', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Creations/circles_user.nk") + "\")")
m.addCommand('Creations/points', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Creations/points.nk") + "\")")
m.addCommand('Creations/points advanced', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Creations/points_advanced.nk") + "\")")
m.addCommand('Creations/bricks', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Creations/bricks.nk") + "\")")
m.addCommand('Creations/gradient horizontal', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Creations/gradient_horizontal.nk") + "\")")
m.addCommand('Creations/gradient horizontal invert', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Creations/gradient_horizontal_invert.nk") + "\")")
m.addCommand('Creations/gradient vertical', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Creations/gradient_vertical.nk") + "\")")
m.addCommand('Creations/gradient vertical invert', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Creations/gradient_vertical_invert.nk") + "\")")
m.addCommand('Creations/gradient 4 corners', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Creations/GradientCorner.nk") + "\")")
m.addCommand('Creations/radial', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Creations/radial.nk") + "\")")
m.addCommand('Creations/radial gradient', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Creations/radial_gradient.nk") + "\")")
m.addCommand('Creations/radial rays', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Creations/radial_rays.nk") + "\")")
m.addCommand('Creations/Trunc', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Creations/Trunc.nk") + "\")")



#ALPHA
m.addCommand('Alpha/alpha binary', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Alpha/alpha_binary.nk") + "\")")
m.addCommand('Alpha/alpha comparison', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Alpha/alpha_comparison.nk") + "\")")
m.addCommand('Alpha/alpha exists?', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Alpha/alpha_exists.nk") + "\")")
m.addCommand('Alpha/alpha sum', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Alpha/alpha_sum.nk") + "\")")



#PIXEL
m.addCommand('Pixel/absolute value', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Pixel/abs.nk") + "\")")
m.addCommand('Pixel/check negative', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Pixel/check_negative.nk") + "\")")
m.addCommand('Pixel/check nan inf pixels', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Pixel/check_nan_inf.nk") + "\")")
m.addCommand('Pixel/create nan pixel', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Pixel/create_nan.nk") + "\")")
m.addCommand('Pixel/kill nan pixel', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Pixel/kill_nan.nk") + "\")")
m.addCommand('Pixel/create inf pixel', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Pixel/create_inf.nk") + "\")")
m.addCommand('Pixel/kill inf pixel', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Pixel/kill_inf.nk") + "\")")



#TRANSFORM
m.addCommand('Transform/Coordinates', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Transform/coordinates.nk") + "\")")
m.addCommand('Transform/UV Map', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Transform/UV_map.nk") + "\")")
m.addCommand('Transform/UV to Vector', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Transform/UV_to_Vector.nk") + "\")")
m.addCommand('Transform/Vector to UV', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Transform/Vector_to_UV.nk") + "\")")
m.addCommand('Transform/transform', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Transform/transform.nk") + "\")")
m.addCommand('Transform/transform advanced', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Transform/transform_advanced.nk") + "\")")
m.addCommand('Transform/twist', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Transform/twist.nk") + "\")")
m.addCommand('Transform/STMap_invert', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Transform/STMap_invert.nk") + "\")")





#3D and DEEP
m.addCommand('3D and Deep/Normal Pass - Relight', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Deep_3D/normalPass_relight.nk") + "\")")
m.addCommand('3D and Deep/C4x4', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Deep_3D/C4x4.nk") + "\")")
m.addCommand('3D and Deep/Deep Thickness', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Deep_3D/deepThickness.nk") + "\")")
m.addCommand('3D and Deep/Deep to Depth', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Deep_3D/deepToDepth.nk") + "\")")
m.addCommand('3D and Deep/Deep from Depth', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Deep_3D/deepFromDepth.nk") + "\")")
m.addCommand('3D and Deep/Depth normalize', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Deep_3D/depth_normalize.nk") + "\")")



#KEYING and DESPILL
m.addCommand('Keying and Despill/despill green', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Keying_Despill/despill_green.nk") + "\")")
m.addCommand('Keying and Despill/despill green list', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Keying_Despill/despill_green_list.nk") + "\")")
m.addCommand('Keying and Despill/despill blue', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Keying_Despill/despill_blue.nk") + "\")")
m.addCommand('Keying and Despill/despill blue list', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Keying_Despill/despill_blue_list.nk") + "\")")
m.addCommand('Keying and Despill/keying', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Keying_Despill/keying.nk") + "\")")
m.addCommand('Keying and Despill/differenceKey', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Keying_Despill/differenceKey.nk") + "\")")
m.addCommand('Keying and Despill/IBKGizmo_Expression', "nuke.nodePaste(\"" + os.path.join(Expression_path + "/Keying_Despill/IBKGizmo_Expression.nk") + "\")")

m.addSeparator()


#INFO
m.addCommand('Info e Tutorial', "nuke.tcl('start', 'http://www.andreageremia.it/tutorial_expression_node.html')", icon = os.path.join(Expression_path, "icon/question_mark.png"))
