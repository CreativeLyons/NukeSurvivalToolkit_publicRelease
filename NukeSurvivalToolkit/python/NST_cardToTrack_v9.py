'''
CardToTrack is a nuke group designed to help extract position of the object in 3D space
and represent it as corner pin in a screen space.

Single consolidated module for all supported Nuke versions (15 and lower, 16 and higher).
- Nuke 16+: Uses fromScript optimization, Undo.disable during calculation, "with C2Tgroup".
- Nuke 15 and lower: Uses begin/end for group context, setKey fallback when fromScript
  is unavailable, and skips Undo.disable when not available.
'''

__author__ = "Alexey Kuchinski"
__copyright__ = "Copyright 2023, Alexey Kuchinski"
__credits__ = ["Peter Mercell", "Adrian Pueyo", "Helge Stang", "Eyal Sirazi", "Marco Meyer", "Tony Lyons", "Mark Joey Tang", "Pete O'Connell", "Ivan Busquets","Ben Dickson","Trixter Folks!!!!!"]
__version__ = "9.6"
__email__ = "lamakaha@gmail.com"
__status__ = "Perpetual Beta"

import time
import nuke
import math
import re

# Version check: one code path for all Nuke versions, with minimal branching where APIs differ.
NUKE_16_PLUS = (nuke.NUKE_VERSION_MAJOR > 15)

def _undo_disable():
    if hasattr(nuke, 'Undo'):
        nuke.Undo.disable()

def _undo_enable():
    if hasattr(nuke, 'Undo'):
        nuke.Undo.enable()

# -------------------------------------------------------------------------------------
# OPTIMIZATION HELPERS
# -------------------------------------------------------------------------------------

def set_anim_curve_from_data(knob, data_list_per_channel):
    """
    Constructs a Nuke animation and applies it to the knob.
    Nuke 16+: uses fromScript for speed. Nuke 15 and lower: uses setKey per channel.
    """
    if NUKE_16_PLUS and hasattr(knob, 'fromScript'):
        full_script = ""
        for channel_data in data_list_per_channel:
            if channel_data:
                curve_str = "{curve "
                keys_str = " ".join([f"x{int(f)} {val:.6f}" for f, val in channel_data])
                curve_str += keys_str + "} "
            else:
                curve_str = "{curve} "
            full_script += curve_str
        if full_script.strip():
            knob.fromScript(full_script)
        return
    # Nuke 15 and lower: setKey per channel (avoid isAnimated(ch_idx) for API compatibility)
    aSize = 1 if knob.singleValue() else knob.arraySize()
    for ch_idx in range(min(len(data_list_per_channel), aSize)):
        channel_data = data_list_per_channel[ch_idx]
        if not channel_data:
            continue
        try:
            knob.setAnimated(ch_idx)
        except Exception:
            pass
        anim = knob.animation(ch_idx)
        if anim is not None:
            for f, val in channel_data:
                anim.setKey(f, val)


def kill_animation(knobs):
    '''
    Kill animation in knobs if knobs are animated but animation is constant.
    '''
    for knob in knobs:
        if knob.isAnimated():
            aSize = 1 if knob.singleValue() else knob.arraySize()
            for index in range(aSize):
                anim = knob.animation(index)
                if anim and anim.constant():
                    knob.clearAnimated(index)

def offset_nodes(x,y):
    '''
    find how far newly created node should be created.
    '''
    allNodes = nuke.allNodes()
    for step in range(1,10):
        step = abs(10-step)
        for node in allNodes:
            if node['xpos'].value() == x+110*step and node['ypos'].value() == y:
                x = x+110*step
                break
    return x

def check_first_last_frame(C2Tgroup):
    '''
    check if camera has animation and if yes collect first and last frame of it
    '''
    with nuke.Root():
        how = C2Tgroup['extraHelper'].value()
        try:
            with C2Tgroup:
                tr = nuke.toNode('DummyCam')['translate'].getKeyList()
                first_frame_v = min(tr)
                last_frame_v = max(tr)

            if how == 1:
                translateKeys = C2Tgroup.input(2)['translate'].getKeyList()
                first_frame_v = min([first_frame_v,min(translateKeys)])
                last_frame_v = max([last_frame_v,max(translateKeys)])
        except:
            first_frame_v = int(nuke.toNode('root')['first_frame'].value())
            last_frame_v = int(nuke.toNode('root')['last_frame'].value())

        if C2Tgroup['S'].value() == 1:
            C2Tgroup['Stabilize'].execute()

        return first_frame_v, last_frame_v

def check_curve(knob,first,last,ref):
    '''
    Check if a curve has Euler flip issue
    '''
    import math
    problem = False
    vals = [knob.valueAt(i,0) for i in range(first, last+1)]
    if not vals: return False

    valSort = sorted(vals)
    minX = valSort[0]
    maxX = valSort[-1]

    if abs(vals.index(maxX) - vals.index(minX)) == 1:
        problem = True
    return problem

def fix_curves(one,first,last,ref):
    import math
    timeline = ["beginning","end"]
    lastB = last
    firstB = first
    for side in timeline:
        if side == "beginning":
            last = ref
        if side == "end":
            first = ref
            last = lastB

        curveXDown = curveXUp = curveYDown = curveYUp = 0
        valsx = [one.valueAt(i,0) for i in range(first,last+1)]
        valsy = [one.valueAt(i,1) for i in range(first,last+1)]

        if not valsx or not valsy: continue

        valSortx = sorted(valsx)
        valSorty = sorted(valsy)

        minX = valSortx[0]; maxX = valSortx[-1]
        minY = valSorty[0]; maxY = valSorty[-1]

        if math.fabs(valsx.index(maxX)-valsx.index(minX)) == 1:
            if valsx.index(maxX)-valsx.index(minX) < 0: curveXUp = 1
            else: curveXDown = 1
            if valsy.index(maxY)-valsy.index(minY) < 0: curveYUp = 1
            else: curveYDown = 1

            if valsx.index(maxX)+first > ref:
                if curveXDown == 1:
                    lastGoodX= one.valueAt(valsx.index(minX)+first,0)
                    prelastGoodX= one.valueAt(valsx.index(minX)+first-1,0)
                    offsetX = abs(lastGoodX)+maxX+(abs(lastGoodX) - abs(prelastGoodX))*2
                    for i in range(valsx.index(maxX)+first,last+1): one.setValueAt(one.valueAt(i)[0]-offsetX,i,0)
                if curveXUp == 1:
                    lastGoodX = one.valueAt(valsx.index(maxX)+first,0)
                    prelastGoodX= one.valueAt(valsx.index(maxX)+first-1,0)
                    offsetX= maxX+abs(minX)+(abs(lastGoodX)- abs(prelastGoodX))*2
                    for i in range(valsx.index(minX)+first,last+1): one.setValueAt(one.valueAt(i)[0]+offsetX,i,0)

            if valsy.index(maxY)+first > ref:
                if curveYDown == 1:
                    lastGoodY= one.valueAt(valsy.index(minY)+first,1)
                    prelastGoodY= one.valueAt(valsy.index(minY)+first-1,1)
                    offsetY = abs(lastGoodY)+maxY+(abs(lastGoodY) - abs(prelastGoodY))*2
                    for i in range(valsy.index(maxY)+first,last+1): one.setValueAt(one.valueAt(i)[1]-offsetY,i,1)
                if curveYUp == 1:
                    lastGoodY = one.valueAt(valsy.index(maxY)+first,1)
                    prelastGoodY= one.valueAt(valsy.index(maxY)+first-1,1)
                    offsetY= maxY+abs(minY)+(abs(lastGoodY) - abs(prelastGoodY))*2
                    for i in range(valsy.index(minY)+first,last+1): one.setValueAt(one.valueAt(i)[1]+offsetY,i,1)

def delete_tab():
    if nuke.ask("This will delete currect Tab and all nodes inside of it\nAre you very sure you want to do so?\n"):
        node = nuke.thisGroup()
        tab_knob_name = nuke.thisKnob().name().replace('Delete','')
        to_remove = []

        for n in range(node.numKnobs()):
            cur_knob = node.knob(n)
            if tab_knob_name in cur_knob.name():
                to_remove.append(cur_knob)

        for element in to_remove:
            if isinstance(element, nuke.Tab_Knob):
                to_remove.remove(element)
                to_remove.append(element)

        for k in to_remove:
            node.removeKnob(k)

        if 'card_to_track' in node.knobs():
            node['card_to_track'].setFlag(1)

# -------------------------------------------------------------------------------------
# MAIN FUNCTIONS
# -------------------------------------------------------------------------------------

def set_ref_frame():
    C2Tgroup = nuke.thisGroup()
    C2Tgroup['Zfind'].setValue(0)

    if NUKE_16_PLUS:
        with C2Tgroup:
            nuke.toNode("ScanlineRender1")['disable'].setValue(0)
            nuke.toNode("StabFrameHold")['first_frame'].setValue(C2Tgroup['refFrame'].value())
            if C2Tgroup['S'].value() == 1:
                C2Tgroup['Stabilize'].execute()

            if not C2Tgroup.input(1): nuke.message('Could you please connect some Camera if you do not mind.')
            if not C2Tgroup.input(0): nuke.message('No connectd BG footage, will use the project resolution instead')

            nuke.toNode("NoOp1")['pick'].execute()
            C2Tgroup['refFrame'].setValue(nuke.frame())
            nuke.toNode("Switch")['which'].setValue(0)

            r=nuke.toNode("Perspective")
            r.setSelected(False); r.hideControlPanel()
            r['rotate'].setValue(0); r['translate'].setValue(0); r['scaling'].setValue(1)
            r['uniform_scale'].setValue(C2Tgroup['scene'].value())
    else:
        C2Tgroup.begin()
        try:
            nuke.toNode("ScanlineRender1")['disable'].setValue(0)
            nuke.toNode("StabFrameHold")['first_frame'].setValue(C2Tgroup['refFrame'].value())
            if C2Tgroup['S'].value() == 1:
                C2Tgroup['Stabilize'].execute()

            if not C2Tgroup.input(1): nuke.message('Could you please connect some Camera if you do not mind.')
            if not C2Tgroup.input(0): nuke.message('No connectd BG footage, will use the project resolution instead')

            nuke.toNode("NoOp1")['pick'].execute()
            C2Tgroup['refFrame'].setValue(nuke.frame())
            nuke.toNode("Switch")['which'].setValue(0)

            r=nuke.toNode("Perspective")
            r.setSelected(False); r.hideControlPanel()
            r['rotate'].setValue(0); r['translate'].setValue(0); r['scaling'].setValue(1)
            r['uniform_scale'].setValue(C2Tgroup['scene'].value())
        finally:
            C2Tgroup.end()

    if C2Tgroup['extraHelper'].value() in [0]:
        C2Tgroup['findZ'].clearFlag(1)
        for one in ['happyGroup','goGroup','goGroup']: C2Tgroup[one].setFlag(1)
    if C2Tgroup['extraHelper'].value() in [1,2,3,4]:
        C2Tgroup['Adjust'].execute()

def stabilize():
    '''
    add stabilization to card in order to find its position in 3d space in easier way
    '''
    node = nuke.thisGroup() 
    t = node['S']
    
    with node:
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
           node['HighPass'].setValue(0)
           node['HighPass_1'].setValue(0)
           nuke.toNode("StabFrameHold")['disable'].setValue(1)
           nuke.toNode("StabSwitch")['disable'].setValue(1)

def happy():
    ''' 
    bake position we did find in previous step in temporary Axis, this axis will be later used
    to get corner pin from 3d position.
    '''
    C2Tgroup=nuke.thisNode()
    
    with C2Tgroup:
        nuke.toNode("Switch")['which'].setValue(1)
        axisNode = nuke.toNode('Z_finder')
        perspective_axis = nuke.toNode('Perspective')
        refFrame = C2Tgroup['refFrame'].value()
        matrixVal = axisNode['world_matrix'].valueAt(refFrame)

        perspective_axis['translate'].setValue([matrixVal[3],matrixVal[7],matrixVal[11]])
        perspective_axis.setSelected(True)
        r=nuke.toNode("look_at_Axis")
        r.setSelected(False)
        r.hideControlPanel() 

    if C2Tgroup['S'].value() == 1:
        C2Tgroup['Stabilize'].execute()
        C2Tgroup['HighPass'].setValue(0)
    if C2Tgroup['extraHelper'].value() in [0,2,3,4]:
        C2Tgroup['findZ'].setFlag(1)
        C2Tgroup['happyGroup'].clearFlag(1)
        C2Tgroup['goGroup'].clearFlag(1)
    C2Tgroup['setGroup'].setFlag(1)

def show_grid_axis():
    C2Tgroup=nuke.thisNode()
    with C2Tgroup:
        perspective_axis = nuke.toNode('Perspective')
        perspective_axis.setSelected(True)   
        nuke.show(perspective_axis)

def go():
    C2Tgroup=nuke.thisNode()
    modes = ['MatchMove','3D Locator(card or axis)','Geometry',"WorldPosition","Deep"]
    mode = modes[int(C2Tgroup['extraHelper'].value())]
    
    if mode == '3D Locator(card or axis)':
        if C2Tgroup.input(2):
            axisNode = C2Tgroup.input(2)
            try:
                if 'world_matrix' not in axisNode.knobs() and 'matrix' not in axisNode.knobs(): raise Exception
            except:
                nuke.message("Supported nodes are an Axis,Card or any Other 3D node with world_matrix")
                return
        else:
            nuke.message("It looks like you did not connect an Axis or a Card to the <b>Extra</b> input.")
            return

    if C2Tgroup['S'].value() == 1:
        C2Tgroup['Stabilize'].execute()
        C2Tgroup['HighPass'].setValue(0)
    for one in ['happyGroup','C2T','scene_settings','cameraExchange','goGroup','findZ']:
        C2Tgroup[one].setFlag(1)
        
    # THIS WAS THE MISSING FUNCTION CALL IN THE PREVIOUS VERSION
    first_frame_v, last_frame_v = check_first_last_frame(C2Tgroup)
    
    x=int(C2Tgroup['xpos'].value())
    y=int(C2Tgroup['ypos'].value())

    with C2Tgroup:
        nuke.toNode("Perspective").setSelected(False)

    with nuke.Root():
        def C2T(dialog):
            ref = int(nuke.frame())
            first = first_frame_v
            last = last_frame_v
            bg = C2Tgroup.input(0)
            recalculate = False

            if dialog == True:
                panel = nuke.Panel("C2T")
                panel.addSingleLineInput("label:", "")
                panel.addSingleLineInput("firstFrame:", str(first))
                panel.addSingleLineInput("lastFrame:", str(last))
                panel.addSingleLineInput("ref frame:", str(ref))
                if panel.show():
                    first = int(panel.value("firstFrame:"))
                    last = int(panel.value("lastFrame:"))
                    ref = int(panel.value("ref frame:"))
                    if ref>last or ref<first: ref = first
                    raw_label = panel.value("label:")
                    label = re.sub(r'[^\w]', '_', raw_label)
                else:
                    nuke.message('canceled')
                    nuke.delete(bg)
                    return
            else:
                print ('no dialog, use auto-created input values')
             
            if '_X_'+label not in C2Tgroup.knobs():
                tab_knob = nuke.Tab_Knob('_X_'+label, label)
                refFrame = nuke.Int_Knob('ReferenceFrame_X_'+label,'Reference Frame')
                firstFrame = nuke.Int_Knob('FirstFrame_X_'+label, 'First Frame')
                lastFrame = nuke.Int_Knob('LastFrame_X_'+label, 'Last Frame')
                baked = nuke.Boolean_Knob('Baked_X_'+label, "Baked", True)
                card = nuke.PyScript_Knob('Card_X_'+label, '3d object')
                corner = nuke.PyScript_Knob('CornerPin_X_'+label, 'CornerPin')
                roto = nuke.PyScript_Knob('Roto_X_'+label, 'Roto')
                transform = nuke.PyScript_Knob('Transform_X_'+label, 'Transform')
                translate = nuke.XYZ_Knob('Translate_X_'+label, 'translate')
                rotate = nuke.XYZ_Knob('Rotate_X_'+label, 'rotate')
                scale = nuke.XYZ_Knob('Scale_X_'+label, 'scale')
                uniform_scale = nuke.Double_Knob('Uniform_scale_X_'+label, 'uniform scale')
                to1 = nuke.XY_Knob('to1_X_'+label, 'to1')
                to2 = nuke.XY_Knob('to2_X_'+label,'to2')
                to3 = nuke.XY_Knob('to3_X_'+label, 'to3')
                to4 = nuke.XY_Knob('to4_X_'+label, 'to4')
                translateT = nuke.XY_Knob('TranslateT_X_'+label, 'translate')
                centerT = nuke.XY_Knob('centerT_X_'+label, 'center')
                matrix = nuke.Array_Knob('matrix_X_'+label, 'matrix',16)
                bGCard = nuke.Tab_Knob('CardKnobs_X_'+label, 'card knobs', nuke.TABBEGINCLOSEDGROUP)
                bGMatrix = nuke.Tab_Knob('MatrixKnobs_X_'+label, 'matrix knobs', nuke.TABBEGINCLOSEDGROUP)
                bGTransform = nuke.Tab_Knob('TransformKnobs_X_'+label, 'transform knobs', nuke.TABBEGINCLOSEDGROUP)
                bGCorner = nuke.Tab_Knob('CornerPinKnobs_X_'+label, 'corner pin knobs', nuke.TABBEGINCLOSEDGROUP)
                eGMatrix = nuke.Tab_Knob('MatrixKnobs_close_X_'+label, None, nuke.TABENDGROUP)
                eGTransform = nuke.Tab_Knob('TransformKnobs_close_X_'+label, None, nuke.TABENDGROUP)
                eGCorner = nuke.Tab_Knob('CornerPinKnobs_close_X_'+label, None, nuke.TABENDGROUP)
                eGCard = nuke.Tab_Knob('CardKnobs_close_X_'+label, None, nuke.TABENDGROUP)
                delete = nuke.PyScript_Knob('Delete_X_'+label, "<b><font color=#A40000>Delete Tab")

                flags = [card, corner, roto, transform]
                for one in flags: one.clearFlag(nuke.STARTLINE)
                card.setFlag(nuke.STARTLINE)

                knobs = [tab_knob, refFrame, firstFrame, lastFrame, card, corner, roto, transform, baked,
                        bGCard, translate, rotate, scale, uniform_scale, eGCard, 
                        bGCorner, to1, to2, to3, to4, eGCorner,
                        bGTransform, translateT, centerT, eGTransform , 
                        bGMatrix, matrix, eGMatrix, delete]

                for one in knobs: C2Tgroup.addKnob(one)

            # Set Values & Scripts
            C2Tgroup['ReferenceFrame_X_'+label].setValue(ref)
            C2Tgroup['FirstFrame_X_'+label].setValue(int(first))
            C2Tgroup['LastFrame_X_'+label].setValue(int(last))
            C2Tgroup['Card_X_'+label].setValue('import NST_cardToTrack_v9; NST_cardToTrack_v9.card_code()')
            C2Tgroup['CornerPin_X_'+label].setValue('import NST_cardToTrack_v9; NST_cardToTrack_v9.corner_code()')
            C2Tgroup['Roto_X_'+label].setValue('import NST_cardToTrack_v9; NST_cardToTrack_v9.roto_code()')
            C2Tgroup['Transform_X_'+label].setValue('import NST_cardToTrack_v9; NST_cardToTrack_v9.transform_code()')
            C2Tgroup['Delete_X_'+label].setValue('import NST_cardToTrack_v9; NST_cardToTrack_v9.delete_tab()')

            # Calculation Call
            import time as time_module
            start_time = time_module.time()
            print(f"\n[CardToTrack] Starting calculation for '{label}'...")
            
            # This calls the function that includes the UNDO FIX and STRING INJECTION
            calculate_corner_pin(C2Tgroup, label, recalculate)
            
            calc_time = time_module.time() - start_time
            print(f"[CardToTrack] Calculation completed in {calc_time:.3f} seconds")

            # Clean up Internal Connections
            with C2Tgroup:
                am = nuke.toNode('aM')
                am['translate'].setExpression('parent.Perspective.translate')
                am['rotate'].setExpression('parent.Perspective.rotate')
                # Revert internal helpers to default expressions
                scale_x_expr = '-0.5*Perspective.uniform_scale*Perspective.scaling.x'
                scale_y_expr = 'input0.pixel_aspect*-0.5*Perspective.uniform_scale*Perspective.scaling.y'
                nuke.toNode('a1')['translate'].setExpression(scale_x_expr,0)
                
            toes = [C2Tgroup['to1_X_'+label], C2Tgroup['to2_X_'+label], C2Tgroup['to3_X_'+label], C2Tgroup['to4_X_'+label]]
            cardknobs = [C2Tgroup['Translate_X_'+label], C2Tgroup['Rotate_X_'+label], C2Tgroup['Scale_X_'+label], C2Tgroup['Uniform_scale_X_'+label]]
            kill_animation(toes + cardknobs)

            issues = []
            for one in toes:
                issues.append(check_curve(one,first,last,ref))

            if True in issues:
                 if nuke.ask("Perspective problem detected! Fix it?"):
                    for i, issue in enumerate(issues):
                        if issue: fix_curves(toes[i],first,last,ref)
            
            if '_X_'+label in C2Tgroup.knobs(): C2Tgroup['_X_'+label].setFlag(0)

        C2T(True)

def recalculate_camera():
    C2Tgroup=nuke.thisNode()
    cardTabs = [k.rpartition('_X_')[2] for k in C2Tgroup.knobs() if k.startswith('_X_')]
    iterations = len(cardTabs)
    
    if iterations > 1: progress_bar = nuke.ProgressTask("Processing Tabs")

    for i, label in enumerate(cardTabs):
        if iterations > 1 and progress_bar.isCancelled(): break
        
        calculate_corner_pin(C2Tgroup, label, True)
        
        if C2Tgroup['TranslateT_X_'+label].isAnimated():
            calculate_translate(C2Tgroup, label)
        
        if C2Tgroup['matrix_X_'+label].isAnimated():
            calculate_matrix(C2Tgroup, label)
        
        with C2Tgroup:
             nuke.toNode('aM')['translate'].setExpression('parent.Perspective.translate')
             nuke.toNode('aM')['rotate'].setExpression('parent.Perspective.rotate')

        if iterations > 1:
            progress_bar.setProgress(int(100*(i / float(iterations))))
            progress_bar.setMessage("Processing Tab: "+label)
            
    if iterations > 1: del progress_bar

def select_associated_nodes():
    '''
    Select all nodes created by this Group.
    '''
    C2Tgroup = nuke.thisGroup()
    group_name = C2Tgroup.name()
    cardTabs = []

    for label in C2Tgroup.knobs():
        if label.startswith('_X_'):
            cardTabs.append(label.rpartition('_X_')[2])

    with nuke.Root():
        nan = nuke.allNodes()

        for node in nan:
            node.setSelected(False)

        for node in nan:
            if 'card_to_track' in node.knobs() and "CardToTrack" not in node.name():
                if group_name+":" in node['card_to_track'].value():
                    node.setSelected(True)

def update_baked():
    '''
    Recalculate selected nodes to match updated camera.
    '''
    C2Tgroup = nuke.thisGroup()
    group_name = C2Tgroup.name()
    cardTabs = []

    for label in C2Tgroup.knobs():
        if label.startswith('_X_'):
            cardTabs.append(label.rpartition('_X_')[2])

    with nuke.Root():
        c2t_nodes = nuke.selectedNodes()
        for node in c2t_nodes:
            identificator = node['card_to_track'].value()
            label = identificator.rpartition(": ")[2]
            nodetype = identificator.split(':')[1]

            if '_X_'+label not in C2Tgroup.knobs():
                nuke.message('looks like <b>'+node.name() +"</b> is not a part of the <b>" +C2Tgroup.name()+"</b> anymore.\nCould be you erased the tab with it?\nPlease deselect this node and run Update Selected Nodes again.")
                return
            if nodetype == 'card':
                if C2Tgroup['Translate_X_'+label].isAnimated():
                    node['translate'].copyAnimations(C2Tgroup['Translate_X_'+label].animations())
                else:
                    node['translate'].setValue(C2Tgroup['Translate_X_'+label].value())

                if C2Tgroup['Rotate_X_'+label].isAnimated():
                    node['rotate'].copyAnimations(C2Tgroup['Rotate_X_'+label].animations())
                else:
                    node['rotate'].setValue(C2Tgroup['Rotate_X_'+label].value())

                if C2Tgroup['Scale_X_'+label].isAnimated():
                    node['scaling'].copyAnimations(C2Tgroup['Scale_X_'+label].animations())
                else:
                    node['scaling'].setValue(C2Tgroup['Scale_X_'+label].value())

                if C2Tgroup['Uniform_scale_X_'+label].isAnimated():
                    node['uniform_scale'].copyAnimations(C2Tgroup['Uniform_scale_X_'+label].animations())
                else:
                    node['uniform_scale'].setValue(C2Tgroup['Uniform_scale_X_'+label].value())

            elif nodetype == 'cornerpin':
                node['to1'].copyAnimations(C2Tgroup['to1_X_'+label].animations())
                node['to2'].copyAnimations(C2Tgroup['to2_X_'+label].animations())
                node['to3'].copyAnimations(C2Tgroup['to3_X_'+label].animations())
                node['to4'].copyAnimations(C2Tgroup['to4_X_'+label].animations())

            elif nodetype == 'transform':
                if C2Tgroup['TranslateT_X_'+label].isAnimated():
                    node['translate'].copyAnimations(C2Tgroup['TranslateT_X_'+label].animations())
                else:
                    node['translate'].setValue(C2Tgroup['TranslateT_X_'+label].value())
                node['center'].setValue(C2Tgroup['centerT_X_'+label].value())

            elif nodetype == 'roto':
                nuke.show(node)
                node['transform_matrix'].copyAnimations(C2Tgroup['matrix_X_'+label].animations())
                node['curves'].changed()

# -------------------------------------------------------------------------------------
# CORE CALCULATION FUNCTIONS (WITH FIXES)
# -------------------------------------------------------------------------------------

def calculate_corner_pin(C2Tgroup,label,recalculate):
    import time as time_module
    start_time = time_module.time()
    
    modes = ['MatchMove','3D Locator(card or axis)','Geometry',"WorldPosition","Deep"]
    mode = modes[int(C2Tgroup['extraHelper'].value())]

    first = int(C2Tgroup['FirstFrame_X_'+label].value())
    last = int(C2Tgroup['LastFrame_X_'+label].value())
    frame_count = last - first + 1
    print(f"  [calculate_corner_pin] Processing {frame_count} frames ({first}-{last}), mode: {mode}")
    
    translate = C2Tgroup['Translate_X_'+label]
    rotate = C2Tgroup['Rotate_X_'+label]
    scale = C2Tgroup['Scale_X_'+label]
    uniform_scale = C2Tgroup['Uniform_scale_X_'+label]
    toes = [C2Tgroup['to1_X_'+label], C2Tgroup['to2_X_'+label], C2Tgroup['to3_X_'+label], C2Tgroup['to4_X_'+label]]
    cardknobs = [translate, rotate, scale, uniform_scale]

    task = nuke.ProgressTask("Calculating Corner Pin Data")
    progress_step = 30
    
    # --- UNDO DISABLE (CRITICAL FOR SPEED) ---
    _undo_disable()

    try:
        if recalculate:
            recalc_start = time_module.time()
            with C2Tgroup:
                am = nuke.toNode('aM')
                am['translate'].setExpression('parent.'+'Translate_X_'+label)
                am['rotate'].setExpression('parent.'+'Rotate_X_'+label)
                expr_x = '0.5*parent.Scale_X_'+label+'.x*parent.Uniform_scale_X_'+label
                expr_y = 'input0.pixel_aspect*0.5*parent.Scale_X_'+label+'.y*parent.Uniform_scale_X_'+label
                nuke.toNode('a1')['translate'].setExpression('-'+expr_x, 0); nuke.toNode('a1')['translate'].setExpression('-'+expr_y, 1)
                nuke.toNode('a2')['translate'].setExpression(expr_x, 0); nuke.toNode('a2')['translate'].setExpression('-'+expr_y, 1)
                nuke.toNode('a3')['translate'].setExpression(expr_x, 0); nuke.toNode('a3')['translate'].setExpression(expr_y, 1)
                nuke.toNode('a4')['translate'].setExpression('-'+expr_x, 0); nuke.toNode('a4')['translate'].setExpression(expr_y, 1)
            print(f"  [calculate_corner_pin] Recalculate expressions set in {time_module.time() - recalc_start:.3f}s")
        else:
            if mode == '3D Locator(card or axis)':
                matrix_start = time_module.time()
                axisNode = C2Tgroup.input(2)
                axis_matrix = axisNode['world_matrix'] if 'world_matrix' in axisNode.knobs() else axisNode['matrix']
                math_matrix = nuke.math.Matrix4()
                
                for k in cardknobs: k.setExpression('curve')
                
                frames = range(int(first), int(last+1))
                scale_data, rotate_data, translate_data = [[],[],[]], [[],[],[]], [[],[],[]]

                for idx, i in enumerate(frames):
                    if task.isCancelled(): break
                    if idx % progress_step == 0:
                         task.setMessage(f"Reading 3D Data frame {i}")
                         task.setProgress(int((idx / len(frames)) * 30))
                    
                    k_vals = axis_matrix.getValueAt(i)
                    for y in range(4):
                        for x in range(4): math_matrix[x+(y*4)] = k_vals[y + 4*x]
                    
                    transM = nuke.math.Matrix4(math_matrix); transM.translationOnly()
                    rotM = nuke.math.Matrix4(math_matrix); rotM.rotationOnly()
                    scaleM = nuke.math.Matrix4(math_matrix); scaleM.scaleOnly()
                    
                    s = (scaleM.xAxis().x, scaleM.yAxis().y, scaleM.zAxis().z)
                    r = rotM.rotationsZXY()
                    t = (transM[12], transM[13], transM[14])
                    
                    for ch in range(3):
                        scale_data[ch].append((i, s[ch]))
                        rotate_data[ch].append((i, math.degrees(r[ch])))
                        translate_data[ch].append((i, t[ch]))

                print(f"  [calculate_corner_pin] Matrix decomposition completed in {time_module.time() - matrix_start:.3f}s")
                
                # --- BATCH INJECT STRINGS (FIXES SLOWDOWN) ---
                inject_start = time_module.time()
                set_anim_curve_from_data(scale, scale_data)
                set_anim_curve_from_data(rotate, rotate_data)
                set_anim_curve_from_data(translate, translate_data)
                uniform_scale.setValue(1)
                print(f"  [calculate_corner_pin] Animation injection completed in {time_module.time() - inject_start:.3f}s")

                with C2Tgroup:
                    am = nuke.toNode('aM')
                    am['translate'].setExpression('parent.'+'Translate_X_'+label)
                    am['rotate'].setExpression('parent.'+'Rotate_X_'+label)
                    expr_x = '0.5*parent.Scale_X_'+label+'.x'; expr_y = 'input0.pixel_aspect*0.5*parent.Scale_X_'+label+'.y'
                    nuke.toNode('a1')['translate'].setExpression('-'+expr_x, 0); nuke.toNode('a1')['translate'].setExpression('-'+expr_y, 1)
                    nuke.toNode('a2')['translate'].setExpression(expr_x, 0); nuke.toNode('a2')['translate'].setExpression('-'+expr_y, 1)
                    nuke.toNode('a3')['translate'].setExpression(expr_x, 0); nuke.toNode('a3')['translate'].setExpression(expr_y, 1)
                    nuke.toNode('a4')['translate'].setExpression('-'+expr_x, 0); nuke.toNode('a4')['translate'].setExpression(expr_y, 1)
            else:
                translate.setExpression('Perspective.translate.x',0); translate.setExpression('Perspective.translate.y',1); translate.setExpression('Perspective.translate.z',2)
                rotate.setExpression('Perspective.rotate.x',0); rotate.setExpression('Perspective.rotate.y',1); rotate.setExpression('Perspective.rotate.z',2)
                scale.setExpression('Perspective.scaling.x',0); scale.setExpression('Perspective.scaling.y',1); scale.setExpression('Perspective.scaling.z',2)
                uniform_scale.setExpression('Perspective.uniform_scale')

        # Internal Expressions for CornerPin
        for one in toes:
            idx = "a" + str(toes.index(one) + 1)
            ratio = "input0.width*DummyCam.focal/DummyCam.haperture"
            one.setExpression(f"({idx}.world_matrix.3/-{idx}.world_matrix.11) * {ratio}+input0.width/2 - DummyCam.win_translate.u*input0.width/2", 0)
            one.setExpression(f"({idx}.world_matrix.7/-{idx}.world_matrix.11)*input0.pixel_aspect*{ratio}+input0.height/2-DummyCam.win_translate.v*input0.width/2", 1)

        # Bake Focal Length (Fast enough with standard loop)
        with C2Tgroup:
            focal_knob = nuke.toNode("DummyCam")['focal']
            if focal_knob.isAnimated() and not focal_knob.animation(0).constant():
                f_anim = focal_knob.animation(0)
                f_data = [(f, f_anim.evaluate(f)) for f in range(first, last+1)]
                for f, v in f_data: f_anim.setKey(f, v)
                focal_knob.setExpression('curve')

        # --- BATCH BAKE CORNER PINS AND CARD KNOBS ---
        # Must bake both toes (corner pins) and cardknobs (translate, rotate, scale)
        bake_start = time_module.time()
        knobs_to_bake = toes + cardknobs
        for k_idx, knob in enumerate(knobs_to_bake):
            if task.isCancelled(): break
            task.setMessage(f"Baking {knob.name()}")
            task.setProgress(40 + int((k_idx/len(knobs_to_bake))*50))

            if knob.isAnimated():
                aSize = 1 if knob.singleValue() else knob.arraySize()
                k_data = [[] for _ in range(aSize)]
                
                for f in range(first, last+1):
                    for ch in range(aSize):
                        anim = knob.animation(ch)
                        if anim and not anim.noExpression():
                            k_data[ch].append((f, anim.evaluate(f)))
                
                # Only apply if we have data
                if any(k_data):
                    # Filter out empty channels
                    non_empty_data = [ch_data for ch_data in k_data if ch_data]
                    if non_empty_data:
                        set_anim_curve_from_data(knob, k_data)

        print(f"  [calculate_corner_pin] Baking knobs completed in {time_module.time() - bake_start:.3f}s")

        with C2Tgroup:
            focal_knob.setExpression("[expression [value the_cam]focal([value the_frame])]")

    except Exception as e:
        print(f"Error in calculate_corner_pin: {e}")
    finally:
        _undo_enable()
        del task
        total_time = time_module.time() - start_time
        print(f"  [calculate_corner_pin] Total time: {total_time:.3f}s")

def calculate_translate(C2Tgroup,label):
    import time as time_module
    start_time = time_module.time()
    
    bg = C2Tgroup.input(0)
    first = int(C2Tgroup['FirstFrame_X_'+label].value())
    last = int(C2Tgroup['LastFrame_X_'+label].value())
    frame_count = last - first + 1
    print(f"  [calculate_translate] Processing {frame_count} frames ({first}-{last})")
    
    to1,to2,to3,to4 = C2Tgroup['to1_X_'+label], C2Tgroup['to2_X_'+label], C2Tgroup['to3_X_'+label], C2Tgroup['to4_X_'+label]
    
    task = nuke.ProgressTask("Calculating Translate")
    progress_step = 30 
    _undo_disable()
    
    try:
        translateT_knob = C2Tgroup['TranslateT_X_'+label]
        bg_width_half = bg.width() / 2
        bg_height_half = bg.height() / 2
        
        data_x, data_y = [], []
        frames = range(first, last+1)
        
        read_start = time_module.time()
        for idx, f in enumerate(frames):
            if task.isCancelled(): break
            if idx % progress_step == 0:
                task.setMessage(f"Processing frame {f}")
                task.setProgress(int((idx / len(frames)) * 100))
                
            t1 = to1.getValueAt(f); t2 = to2.getValueAt(f); t3 = to3.getValueAt(f); t4 = to4.getValueAt(f)
            avg_x = (t1[0]+t2[0]+t3[0]+t4[0])/4 - bg_width_half
            avg_y = (t1[1]+t2[1]+t3[1]+t4[1])/4 - bg_height_half
            data_x.append((f, avg_x)); data_y.append((f, avg_y))
        
        print(f"  [calculate_translate] Data collection completed in {time_module.time() - read_start:.3f}s")
            
        set_anim_curve_from_data(translateT_knob, [data_x, data_y])
        C2Tgroup['centerT_X_'+label].setValue([bg.width()/2, bg.height()/2])
        
    finally:
        _undo_enable()
        del task
        total_time = time_module.time() - start_time
        print(f"  [calculate_translate] Total time: {total_time:.3f}s")

def calculate_matrix(C2Tgroup,label):
    import time as time_module
    start_time = time_module.time()
    
    to1 = C2Tgroup['to1_X_'+label]; to2 = C2Tgroup['to2_X_'+label]
    to3 = C2Tgroup['to3_X_'+label]; to4 = C2Tgroup['to4_X_'+label]
    matrix = C2Tgroup['matrix_X_'+label]
    width = C2Tgroup.input(0).width()
    height = C2Tgroup.input(0).height()

    first = int(C2Tgroup['FirstFrame_X_'+label].value())
    last = int(C2Tgroup['LastFrame_X_'+label].value())
    frame_count = last - first + 1
    print(f"  [calculate_matrix] Processing {frame_count} frames ({first}-{last})")
    
    task = nuke.ProgressTask("Calculating Matrix")
    progress_step = 30 
    _undo_disable()
    
    try:
        matrix_data = [[] for _ in range(16)]
        projFrom = nuke.math.Matrix4()
        projFrom.mapUnitSquareToQuad(0, 0, width, 0, width, height, 0, height)
        projFromInv = projFrom.inverse()
        projTo = nuke.math.Matrix4()
        
        calc_start = time_module.time()
        frames = range(first, last+1)
        for idx, f in enumerate(frames):
            if task.isCancelled(): break
            if idx % progress_step == 0:
                task.setMessage(f"Matrix frame {f}")
                task.setProgress(int((idx / len(frames)) * 100))
                
            t1 = to1.getValueAt(f); t2 = to2.getValueAt(f); t3 = to3.getValueAt(f); t4 = to4.getValueAt(f)
            projTo.mapUnitSquareToQuad(t1[0], t1[1], t2[0], t2[1], t3[0], t3[1], t4[0], t4[1])
            resM = projTo * projFromInv
            resM.transpose()
            
            for i in range(16): matrix_data[i].append((f, resM[i]))
        
        print(f"  [calculate_matrix] Matrix computation completed in {time_module.time() - calc_start:.3f}s")
                
        inject_start = time_module.time()
        set_anim_curve_from_data(matrix, matrix_data)
        print(f"  [calculate_matrix] Animation injection completed in {time_module.time() - inject_start:.3f}s")

    finally:
        _undo_enable()
        del task
        total_time = time_module.time() - start_time
        print(f"  [calculate_matrix] Total time: {total_time:.3f}s")

# -------------------------------------------------------------------------------------
# OBJECT CREATION
# -------------------------------------------------------------------------------------

def card_code():
    _create_object_helper('Card')
def corner_code():
    _create_object_helper('CornerPin')
def transform_code():
    _create_object_helper('Transform')
def roto_code():
    _create_object_helper('Roto')

def _create_object_helper(type):
    if type == 'Card': _card_impl()
    elif type == 'CornerPin': _cp_impl()
    elif type == 'Transform': _tr_impl()
    elif type == 'Roto': _roto_impl()

def _card_impl():
    import time as time_module
    start_time = time_module.time()
    
    panel = nuke.Panel("Choose your 3D object")
    panel.addEnumerationPulldown("objects:", "Card Axis Cube Sphere Cylinder Light TransformGeo Camera2")
    if panel.show(): 
        object_3d = panel.value("objects:")
        if object_3d in ['Card','Camera']: object_3d += '2'
        C2Tgroup = nuke.thisNode()
        label = nuke.thisKnob().name().rpartition('_X_')[2]
        print(f"\n[CardToTrack] Creating 3D object '{object_3d}' for '{label}'...")
        x = C2Tgroup['xpos'].value(); y = C2Tgroup['ypos'].value()
        with nuke.Root():
            x = offset_nodes(x,y)
            card = nuke.createNode(object_3d)
            card.setInput(0,None); card.setXYpos(int(x+110), int(y))
            card.setName(panel.value("objects:")+"_"+label)
            knob = nuke.Text_Knob('card_to_track', ''); knob.setValue(C2Tgroup.name()+":card: "+label); card.addKnob(knob)
            if object_3d == 'Card2': card['image_aspect'].setValue(0)
            
            if C2Tgroup['Baked_X_'+label].value():
                for k, src in [('translate','Translate'),('rotate','Rotate'),('scaling','Scale'),('uniform_scale','Uniform_scale')]:
                    if C2Tgroup[src+'_X_'+label].isAnimated(): card[k].copyAnimations(C2Tgroup[src+'_X_'+label].animations())
                    else: card[k].setValue(C2Tgroup[src+'_X_'+label].value())
            else:
                card['translate'].setExpression("parent."+C2Tgroup.name()+'.Translate_X_'+label)
                card['rotate'].setExpression("parent."+C2Tgroup.name()+'.Rotate_X_'+label)
                card['scaling'].setExpression("parent."+C2Tgroup.name()+'.Scale_X_'+label)
                card['uniform_scale'].setExpression("parent."+C2Tgroup.name()+'.Uniform_scale_X_'+label) 
            card.showControlPanel()
            
            elapsed = time_module.time() - start_time
            print(f"[CardToTrack] 3D object creation completed in {elapsed:.3f} seconds")

def _cp_impl():
    import time as time_module
    start_time = time_module.time()
    
    C2Tgroup = nuke.thisNode()
    label = nuke.thisKnob().name().rpartition('_X_')[2]
    print(f"\n[CardToTrack] Creating CornerPin for '{label}'...")
    ref = int(C2Tgroup['ReferenceFrame_X_'+label].value())
    x = C2Tgroup['xpos'].value(); y = C2Tgroup['ypos'].value()
    with nuke.Root():
        x = offset_nodes(x,y)
        try:
            cp = nuke.nodes.NST_CProject2(xpos = x+110, ypos = y)
            cp.setName("CP_"+label); cp['refFrame'].setValue(ref); cp['label'].setValue("Matchmove\n"+str(ref))
            cp['card_to_track'].setValue(C2Tgroup.name()+":cornerpin: "+label)
        except:
            cp = nuke.nodes.CornerPin2D(label=label, xpos=x+110, ypos=y)
        
        if C2Tgroup['Baked_X_'+label].value():
            for i in range(1,5):
                cp[f'to{i}'].copyAnimations(C2Tgroup[f'to{i}_X_'+label].animations())
                cp[f'from{i}'].setValue(C2Tgroup[f'to{i}_X_'+label].getValueAt(float(ref)))
        else:
            for i in range(1,5):
                cp[f'to{i}'].setExpression(f"parent.parent.{C2Tgroup.name()}.to{i}_X_{label}")
                cp[f'from{i}'].setValue(C2Tgroup[f'to{i}_X_'+label].getValueAt(ref))
        cp.showControlPanel()
        
        elapsed = time_module.time() - start_time
        print(f"[CardToTrack] CornerPin creation completed in {elapsed:.3f} seconds")

def _tr_impl():
    import time as time_module
    start_time = time_module.time()
    
    C2Tgroup = nuke.thisNode()
    label = nuke.thisKnob().name().rpartition('_X_')[2]
    print(f"\n[CardToTrack] Creating Transform for '{label}'...")
    
    calc_start = time_module.time()
    calculate_translate(C2Tgroup, label)
    print(f"  [_tr_impl] calculate_translate took {time_module.time() - calc_start:.3f}s")
    
    ref = str(int(C2Tgroup['ReferenceFrame_X_'+label].value()))
    x = C2Tgroup['xpos'].value(); y = C2Tgroup['ypos'].value()
    with nuke.Root():
        x = offset_nodes(x,y)
        try:
            tr = nuke.nodes.NST_TProject2(xpos=x+110, ypos=y)
            tr.setName("TP_"+label); tr['label'].setValue("Matchmove\n"+ref)
            tr['card_to_track'].setValue(C2Tgroup.name()+":transform: "+label)
        except:
            tr = nuke.nodes.Transform(label=label, xpos=x+110, ypos=y)
        
        if C2Tgroup['Baked_X_'+label].value():
            tr['translate'].copyAnimations(C2Tgroup['TranslateT_X_'+label].animations())
            tr['center'].setValue(C2Tgroup['centerT_X_'+label].value())
        else:
            tr['translate'].setExpression(f"parent.parent.{C2Tgroup.name()}.TranslateT_X_{label}")
            tr['center'].setExpression(f"parent.parent.{C2Tgroup.name()}.centerT_X_{label}")
        tr.showControlPanel()
        if 'setCurrentAsRefFrame' in tr.knobs(): tr['setCurrentAsRefFrame'].execute()
        
        elapsed = time_module.time() - start_time
        print(f"[CardToTrack] Transform creation completed in {elapsed:.3f} seconds")

def _roto_impl():
    import time as time_module
    start_time = time_module.time()
    
    message = '''Looks like Nuke does not support linking of the transformation matrix in roto nodes - please bake instead.

    Since we are able to recalculate nodes if camera is updated - i will generally recommend to bake and not to link nodes while using CardToTrack.'''
    
    C2Tgroup = nuke.thisNode()
    label = nuke.thisKnob().name().rpartition('_X_')[2]
    ask = C2Tgroup['Baked_X_'+label].value()
    
    if ask:
        print(f"\n[CardToTrack] Creating Roto for '{label}'...")
        
        ref = C2Tgroup['ReferenceFrame_X_'+label].value()
        x = C2Tgroup['xpos'].value()
        y = C2Tgroup['ypos'].value()
        first = C2Tgroup['FirstFrame_X_'+label].value()
        last = C2Tgroup['LastFrame_X_'+label].value()
        
        to1 = C2Tgroup['to1_X_'+label]
        to2 = C2Tgroup['to2_X_'+label]
        to3 = C2Tgroup['to3_X_'+label]
        to4 = C2Tgroup['to4_X_'+label]
        matrix = C2Tgroup['matrix_X_'+label]
        
        # CRITICAL: Must set animated before calculating matrix
        matrix.setAnimated()
        
        calc_start = time_module.time()
        calculate_matrix(C2Tgroup, label)
        print(f"  [_roto_impl] calculate_matrix took {time_module.time() - calc_start:.3f}s")
        
        # Create roto node and copy animation from matrix to roto root matrix
        with nuke.Root():
            panel = nuke.Panel("Roto or RotoPaint")
            panel.addEnumerationPulldown("Roto Type:", "Roto RotoPaint")
            if panel.show():
                rototype = panel.value("Roto Type:")
                x = offset_nodes(x, y)
                if rototype == "Roto":
                    roto = nuke.nodes.Roto(xpos=x+110, ypos=y)
                else:
                    roto = nuke.nodes.RotoPaint(xpos=x+110, ypos=y)
                roto.setName(roto['name'].value().replace('Roto', 'R')+"_"+label)
                roto['cliptype'].setValue("no clip")
                nuke.show(roto)
                knob = nuke.Text_Knob('card_to_track', '')
                knob.setValue(C2Tgroup.name()+":roto: "+label)
                roto.addKnob(knob)
                
                # Copy matrix animation to roto
                roto['transform_matrix'].copyAnimations(C2Tgroup['matrix_X_'+label].animations())
                roto['curves'].changed()
                
                # Apply format to the roto node
                group_format = C2Tgroup.format()
                name = group_format.name()
                if name:
                    roto['format'].setValue(name)
                else:
                    width = str(group_format.width())
                    height = str(group_format.height())
                    aspect = str(group_format.pixelAspect())
                    name = "temp_"+width+"x"+height
                    new_format = width+" "+height+" "+aspect+" "+name
                    nuke.addFormat(new_format)
                    roto['format'].setValue(name)
                
                elapsed = time_module.time() - start_time
                print(f"[CardToTrack] Roto creation completed in {elapsed:.3f} seconds")
    else:
        nuke.message(message)

def object_only():
    C2Tgroup=nuke.thisGroup()
    t = C2Tgroup['translate'].value(); r = C2Tgroup['rotate'].value()
    s = C2Tgroup['scaling'].value(); u = C2Tgroup['uniform_scale'].value()
    panel = nuke.Panel("object")
    panel.addSingleLineInput("Object Name:","")
    panel.addEnumerationPulldown("objects:", "Card Axis Cube Sphere Cylinder Light TransformGeo Camera")
    if panel.show(): 
        ob = panel.value("objects:"); name = panel.value("Object Name:")
        obj = nuke.createNode(ob); x = C2Tgroup['xpos'].value(); y = C2Tgroup['ypos'].value()
        obj.setInput(0,None); obj['xpos'].setValue(int(x)); obj['ypos'].setValue(int(y+100))
        obj['translate'].setValue(t); obj['rotate'].setValue(r)
        obj['scaling'].setValue(s); obj['uniform_scale'].setValue(u)
        obj.setName(name)


# -------------------------------------------------------------------------------------
# CProject and TProject Functions
# -------------------------------------------------------------------------------------

def set_ref_frame_cp(frame, node):
    '''
    Set reference frame for corner pin node (CProject/TProject)
    '''
    ntn = nuke.thisNode()
    if node == 'cornerpin':
        set_to_input_label_toggle(ntn, unset=True)
        for one in range(1, 5):
            ntn['from'+str(one)].setValue(ntn['to'+str(one)].valueAt(frame))
    elif node == 'translate':
        with ntn:
            pall = nuke.toNode("refPall")
            papa = nuke.toNode("Transform1")
            pall['disable'].setValue(False)
            knobs = ["translate", "rotate", "scale", "center"]
            for one in knobs:
                pall[one].setValue(papa[one].value())

    ntn['label'].setValue(ntn['mode_toggle'].label().rpartition(">")[2]+"\n"+str(frame))
    ntn['refFrame'].setValue(frame)
    with ntn:
        nuke.toNode("FHold")['first_frame'].setValue(frame)


stored = []
def recurseUpSelect(node):
    '''
    Recursively select upstream nodes
    '''
    global stored
    if node != None and node not in stored:
        for i in range(node.inputs()):
            recurseUpSelect(node.input(i))
            stored.append(node.input(i))
    return stored


def toggle_matchmove_stabilise(node):
    '''
    Toggle matchmove vs stabilise in CProject or TProject
    '''
    ntn = nuke.thisNode()
    ntk = nuke.thisKnob()
    ref_frame = str(int(ntn['refFrame'].value()))
    lab = ntk.label()

    mm = "<h1 style = 'font-size:30'><b><font color=#9667D1>Matchmove"
    stab = "<h1 style = 'font-size:30'><b><font color=#797BFF>Stabilize"

    if lab == mm:
        ntk.setLabel(stab)
        ntn['invert'].setValue(True)
        ntn['tile_color'].setValue(1834205695)

        if node == 'translate':
            ntn['label'].setValue("Stabilize\n"+ref_frame)
            with ntn:
                nuke.toNode('refPall')['disable'].setValue(False)
        else:
            if ntn['set_to_input_1'].label() == "<h1 style = 'font-size:10'><b>Set To Input":
                ntn['label'].setValue("Stabilize\ninput")
            else:
                ntn['label'].setValue("Stabilize\n"+ref_frame)

    elif lab == stab:
        ntk.setLabel(mm)
        ntn['invert'].setValue(False)
        ntn['tile_color'].setValue(2051246591)

        if node == 'translate':
            ntn['label'].setValue("Matchmove\n"+ref_frame)
            with ntn:
                nuke.toNode('refPall')['disable'].setValue(True)
        else:
            if ntn['set_to_input_1'].label() == "<h1 style = 'font-size:10'><b>Set To Input":
                ntn['label'].setValue("Matchmove\ninput")
            else:
                ntn['label'].setValue("Matchmove\n"+ref_frame)

    if node != 'translate':
        # Auto toggle for second CProject to check input/output aspect checkboxes
        global stored
        stored = []
        upstreamNodes = recurseUpSelect(ntn.input(0))
        for one in upstreamNodes:
            if one:
                if 'card_to_track' in one.knobs():
                    image_aspect = one['image_aspect'].value()
                    image_aspect_out = one['image_aspect_out'].value()
                    if image_aspect_out:
                        ntn['image_aspect'].setValue(True)
                        ntn['image_aspect_out'].setValue(False)
                        break
                    elif image_aspect:
                        ntn['image_aspect_out'].setValue(True)
                        ntn['image_aspect'].setValue(False)
                        break
                    else:
                        ntn['image_aspect_out'].setValue(False)
                        ntn['image_aspect'].setValue(False)
                        break
                else:
                    ntn['image_aspect_out'].setValue(False)
                    ntn['image_aspect'].setValue(False)


def set_to_input_label_toggle(ntn, unset):
    '''
    Toggle the set-to-input label state
    '''
    ntk = ntn['set_to_input_1']
    lab = ntk.label()
    input_set = "<h1 style = 'font-size:10'><b>Set To Input"
    ref_frame_set = "Set To Input"
    if unset:
        ntk.setLabel(ref_frame_set)
        return
    if lab == input_set:
        ntk.setLabel(ref_frame_set)
    else:
        ntk.setLabel(input_set)


def set_to_input_cp():
    '''
    Set 'From' values of the Corner pin to the input footage canvas.
    '''
    ntn = nuke.thisNode()
    set_to_input_label_toggle(ntn, unset=False)
    with ntn:
        nuke.toNode("CornerPin2D2")["set_to_input"].execute()
        ntn['label'].setValue(ntn['mode_toggle'].label().rpartition(">")[2]+"\ninput")


def knob_changed_cp():
    '''
    Handle knob changes in CProject/TProject nodes
    '''
    nn = nuke.thisNode()
    k = nuke.thisKnob()
    kn = k.name()

    if kn == "cropP":
        if nn['cropP'].value() in ["Hard Crop"]:
            nn["growBbox"].setVisible(False)
            nn["text"].setValue("Image is cropped to Input, Concatenation preserved.")

        elif nn['cropP'].value() in ["Adjustable Crop"]:
            nn["growBbox"].setVisible(True)
            nn["text"].setValue("Adjust your Bbox , Downward <b><font color='Dark Red'>Concatenation is broken<b>.")

        elif nn['cropP'].value() in ["No Crop"]:
            nn["growBbox"].setVisible(False)
            nn["text"].setValue("No Crop applied, Concatenation preserved.")
