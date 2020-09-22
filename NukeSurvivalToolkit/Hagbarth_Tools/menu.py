''' Add this to your menu.py '''


##Hagbarth Tools
toolbar = nuke.toolbar("Nodes")
m = toolbar.addMenu("NukeSurvivalToolkit/Draw/Hagbarth Tools MHD", icon="h_tools.png", index=000)

# Add Silk

m.addCommand("Silk MHD", "nuke.createNode(\"{}h_silk\")".format(prefixNST), icon="h_silk.png")

# Add GradientEditor
try:
    import ColorGradientUi
except:
    print "Could not load ColorGradientUi from HagbarthTools"
    pass


m.addCommand("GradientEditor MHD", "nuke.createNode(\"{}h_gradienteditor\")".format(prefixNST), icon="h_gradienteditor.png")

# Add StickIt

m.addCommand("StickIt MHD", "nuke.createNode(\"{}h_stickit\")".format(prefixNST), icon="h_stickit.png")

m.addCommand("WaveletBlur MHD", "nuke.createNode(\"{}WaveletBlur\")".format(prefixNST), icon="h_tools.png")

