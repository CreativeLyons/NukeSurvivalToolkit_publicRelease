try:
    toolbar = nuke.toolbar("Nodes")
    NST_filterMenu = toolbar.findItem("NukeSurvivalToolkit/Filter")
    m = NST_filterMenu.addMenu("X_Tools XM", icon="X_Tools.png", index=000)

    m.addCommand("X_Aton_Volumetrics XM", "nuke.createNode(\"{}X_Aton_Volumetrics\")".format(prefixNST), icon="X_Aton.png")
    m.addCommand("X_Denoise XM", "nuke.createNode(\"{}X_Denoise\")".format(prefixNST), icon="X_Denoise.png")
    m.addCommand("X_Sharpen XM", "nuke.createNode(\"{}X_Sharpen\")".format(prefixNST), icon="X_Sharpen.png")
    m.addCommand("X_Soften XM", "nuke.createNode(\"{}X_Soften\")".format(prefixNST), icon="X_Soften.png")
    m.addCommand("X_Distort XM", "nuke.createNode(\"{}X_Distort\")".format(prefixNST), icon="X_Distort.png")
    m.addCommand("X_Tesla XM", "nuke.createNode(\"{}X_Tesla\")".format(prefixNST), icon="X_Tesla.png")
    m.addCommand("Examples/X_Aton_Examples XM", "nuke.createNode('{}X_Aton_Examples.nk')".format(prefixNST), icon="X_Aton.png")
except:
    print "Cannot load X_Tools XM menu"