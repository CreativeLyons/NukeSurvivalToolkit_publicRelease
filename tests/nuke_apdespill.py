"""Native regression tests for NST_apDespill's image-based limit.

Run only in a separate terminal process: Nuke --safe -ti tests/nuke_apdespill.py
Use run_nuke_apdespill.py for bounded execution and a fresh-process reload.
"""
import argparse
from pathlib import Path
import hashlib
import json
import math
import os
import sys
import tempfile
import traceback

import nuke


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Evidence directory; defaults to a new temporary directory")
    parser.add_argument("--phase", choices=("compute", "reload"), default="compute")
    parser.add_argument("--gizmo", type=Path, default=Path(__file__).resolve().parents[1] / "NukeSurvivalToolkit/gizmos/NST_apDespill.gizmo")
    args = parser.parse_args(argv)
    if args.phase == "reload" and args.output is None:
        parser.error("--phase reload requires --output from a previous compute run")
    GIZMO = args.gizmo.expanduser().resolve()
    OUT = args.output.expanduser().resolve() if args.output else Path(tempfile.mkdtemp(prefix="apdespill_native_"))
    OUT.mkdir(parents=True, exist_ok=True)
    PHASE = args.phase
    VERSION = nuke.NUKE_VERSION_STRING
    SCENE = OUT / "roundtrip.nk"
    EXPECTED = OUT / "roundtrip_expected.json"
    REPORT = OUT / (PHASE + ".json")
    CHANNELS = ("rgba.red", "rgba.green", "rgba.blue", "rgba.alpha")
    report = {"nuke": VERSION, "phase": PHASE, "gizmo_sha256": hashlib.sha256(GIZMO.read_bytes()).hexdigest(), "checks": [], "failures": []}
    if not GIZMO.read_text(encoding="utf-8").lstrip().startswith("Group {"):
        raise RuntimeError("Expected a portable embedded Group, not a Gizmo header")


    def sample(node, channels=CHANNELS):
        return [node.sample(channel, 5.5, 5.5) for channel in channels]


    def check(name, actual, expected):
        passed = len(actual) == len(expected) and all(math.isfinite(a) and abs(a - b) <= 3e-5 for a, b in zip(actual, expected))
        report["checks"].append({"name": name, "actual": actual, "expected": expected, "passed": passed})
        if not passed:
            report["failures"].append(name)


    def fact(name, passed):
        check(name, [int(bool(passed))], [1])


    def group_view_state(group):
        knob = group.knob("disable_group_view")
        report["group_view_knob_supported"] = knob is not None
        fact("inline Group view disabled when supported", knob is None or bool(knob.value()))


    def group_view_serialization():
        # onCreate may mention the knob in its escaped Python source, but an
        # actual knob record would warn when the scene is read by older Nuke.
        serialized = SCENE.read_text(encoding="utf-8").splitlines()
        fact("script omits version-specific Group-view knob record",
             not any(line.lstrip().startswith("disable_group_view ") for line in serialized))


    def constant(name, color):
        node = nuke.nodes.Constant(name=name)
        node["format"].setValue(nuke.addFormat("16 16 0 0 16 16 1 apDespill_test"))
        node["color"].setValue(color)
        return node


    def load(name):
        for node in nuke.selectedNodes():
            node.setSelected(False)
        nuke.nodePaste(str(GIZMO))
        group = nuke.selectedNode()
        group.setName(name)
        group["imagebased"].setValue(True)
        return group


    def configure(group, source, limit=None, color_input=None, respill_input=None, mask=None, **options):
        defaults = {"colorspace_shift": False, "log_space": False, "color": "green", "pick": [0, 1, 0],
                    "respill_color": [0, 0, 0], "output_alpha": False, "inverted_spill_matte": True,
                    "absolute_mode": False, "prot1_activate": False, "prot1_preview": False,
                    "mode": "average", "custom_weight": 0, "tolerance": 1, "out": "despill",
                    "hue_offset": 0, "invert_limit_channel": False, "limit_channel": "rgba.alpha", "mix": 1}
        defaults.update(options)
        # Channel selectors validate against the current input's channel list.
        # Connect first so a selector is not constrained by a previous RGB-only input.
        for index, node in enumerate((source, mask, color_input, limit, respill_input)):
            group.setInput(index, node)
        for name, value in defaults.items():
            group[name].setValue(value)


    def core_regressions(group, source, limiter):
        """Direct numeric contract, disconnected behavior and public input controls."""
        configure(group, source)
        original = [0.2, 0.3, 0.4, 0.37]
        check("no limit: default RGB and original alpha", sample(group), original)
        roles = {node.name(): int(node["number"].value()) for node in group.nodes() if node.Class() == "Input"}
        fact("image-based input roles", roles == {"Inputimage": 0, "Inputmask": 1, "Inputcolor": 2, "Inputlimit": 3, "Inputrespill": 4})
        group.setInput(3, limiter)
        group["imagebased"].setValue(False)
        fact("connected limit cannot be hidden", group["imagebased"].value() and group.input(3) is limiter)

        # A negative control reconstructs the old mappings on this test node only.
        shuffle = group.node("Shuffle_limit")
        mapping = {channel: shuffle[channel].value() for channel in ("red", "green", "blue", "alpha")}
        for channel in mapping:
            shuffle[channel].setValue("black")
        check("original failure reproduction: black limiter", sample(shuffle), [0, 0, 0, 0])
        check("original failure reproduction: invert off", sample(group), [0.2, 0, 0.4, 0.37])
        group["invert_limit_channel"].setValue(True)
        check("original failure reproduction: invert on", sample(group), original)
        for channel, value in mapping.items():
            shuffle[channel].setValue(value)

        for invert in (False, True):
            for channel, value in zip(CHANNELS, [0.1, 0.3, 0.7, 0.8]):
                for tolerance in (0.5, 1, 2):
                    configure(group, source, limiter, limit_channel=channel, invert_limit_channel=invert, tolerance=tolerance)
                    effective = tolerance * (1 - value if invert else value)
                    check("limit %s invert=%s tolerance=%s" % (channel, invert, tolerance),
                          sample(group), [0.2, min(1, 0.3 * effective), 0.4, 0.37])
        for invert in (False, True):
            for value in (-0.2, 0, 0.25, 1, 1.5):
                limiter["color"].setValue([0.1, 0.3, 0.7, value])
                configure(group, source, limiter, invert_limit_channel=invert)
                check("HDR limit alpha=%s invert=%s" % (value, invert), sample(group),
                      [0.2, min(1, 0.3 * (1 - value if invert else value)), 0.4, 0.37])
        limiter["color"].setValue([0.1, 0.3, 0.7, 0.8])

        source["color"].setValue([-0.2, 1, 0.4, 0.37])
        configure(group, source)
        check("negative RGB: lift before kernel", sample(group.node("Expression1")), [0, 1.2, 0.6, 0.2])
        check("negative RGB: restore after kernel", sample(group), [-0.2, 0.1, 0.4, 0.37])
        for invert in (False, True):
            configure(group, source, limiter, invert_limit_channel=invert)
            check("negative RGB with limit invert=%s" % invert, sample(group),
                  [-0.2, 0.3 * (0.2 if invert else 0.8) - 0.2, 0.4, 0.37])
        source["color"].setValue([0.2, 1, 0.4, 0.37])
        for inverted in (False, True):
            configure(group, source, output_alpha=True, inverted_spill_matte=inverted)
            matte = 0.7 * 0.7154
            check("requested spill matte, inverted=%s" % inverted, sample(group),
                  [0.2, 0.3, 0.4, 1 - matte if inverted else matte])
        for channel in CHANNELS:
            for invert in (False, True):
                configure(group, source, limit_channel=channel, invert_limit_channel=invert)
                check("no limit ignores routing: %s invert=%s" % (channel, invert), sample(group), original)
        group["imagebased"].setValue(False)
        fact("disconnected image inputs can hide", not group["imagebased"].value() and len([n for n in group.nodes() if n.Class() == "Input"]) == 2)
        group["imagebased"].setValue(True)
        fact("limit input role restored after hiding", int(group.node("Inputlimit")["number"].value()) == 3)

        # Copy/paste is a separate artist workflow from the fresh-process script load.
        configure(group, source, limiter, limit_channel="rgba.green", invert_limit_channel=True)
        expected = sample(group)
        for node in nuke.allNodes():
            node.setSelected(node in (source, limiter, group))
        copied = OUT / "copied_nodes.nk"
        nuke.nodeCopy(str(copied))
        # Pasting onto the selected originals can insert nodes into their
        # downstream connections, contaminating fixtures used by later checks.
        for node in nuke.selectedNodes():
            node.setSelected(False)
        nuke.nodePaste(str(copied))
        pasted = next(n for n in nuke.selectedNodes() if n.Class() == "Group")
        check("node copy/paste: numeric result", sample(pasted), expected)
        fact("node copy/paste: non-default channel and input role", pasted["limit_channel"].value() == group["limit_channel"].value() and int(pasted.node("Inputlimit")["number"].value()) == 3)


    try:
        if PHASE == "reload":
            expected = json.loads(EXPECTED.read_text())
            nuke.scriptOpen(str(SCENE))
            group = nuke.toNode("Test_apDespill")
            group_view_state(group)
            group_view_serialization()
            check("fresh-process script reload: RGBA", sample(group), expected["rgba"])
            check("fresh-process script reload: source auxiliary channel", sample(group, ["despillAux.keep"]), expected["aux"])
            fact("fresh-process script reload: custom limit channel", group["limit_channel"].value() == expected["channel"])
            fact("fresh-process script reload: all image inputs", all(group.input(i) is not None for i in (0, 2, 3, 4)))
            group["imagebased"].setValue(False)
            fact("fresh-process callback: connected inputs cannot hide", group["imagebased"].value())
        else:
            source = constant("Test_Source", [0.2, 1, 0.4, 0.37])
            limiter = constant("Test_Limiter", [0.1, 0.3, 0.7, 0.8])
            color_image = constant("Test_Color", [0, 1, 0, 1])
            respill_image = constant("Test_Respill", [1, 0, 0, 1])
            auxiliary = constant("Test_Auxiliary", [3.2, 0, 0, 1])
            rgb_limit = nuke.nodes.Remove(inputs=[limiter])
            rgb_limit["channels"].setValue("alpha")
            rgb_source = nuke.nodes.Remove(inputs=[source])
            rgb_source["channels"].setValue("alpha")
            nuke.Layer("despillLimit", ["despillLimit.amount"])
            nuke.Layer("despillAux", ["despillAux.keep"])
            layered_limit = nuke.nodes.Copy(inputs=[limiter, limiter])
            layered_limit["from0"].setValue("rgba.blue")
            layered_limit["to0"].setValue("despillLimit.amount")
            layered_source = nuke.nodes.Copy(inputs=[source, auxiliary])
            layered_source["from0"].setValue("rgba.red")
            layered_source["to0"].setValue("despillAux.keep")
            group = load("Test_apDespill")
            reference = load("Test_Reference")
            group_view_state(group)
            core_regressions(group, source, limiter)

            fact("RGB-only limiter fixture", "rgba.alpha" not in rgb_limit.channels())
            for invert in (False, True):
                configure(group, source, rgb_limit, invert_limit_channel=invert)
                check("missing limiter alpha, invert=%s" % invert, sample(group), [0.2, 0.3 if invert else 0, 0.4, 0.37])
            configure(group, source, rgb_limit, limit_channel="rgba.blue")
            check("RGB-only limiter: selected blue remains usable", sample(group), [0.2, 0.21, 0.4, 0.37])
            fact("RGB-only source fixture", "rgba.alpha" not in rgb_source.channels())
            configure(group, rgb_source, limiter)
            check("RGB-only source: limit alpha does not become source alpha", sample(group), [0.2, 0.24, 0.4, 0])

            configure(group, source, limiter)
            alpha_samples = []
            for alpha in (-0.2, 0.0, 1.0, 2.0):
                source["color"].setValue([0.2, 1, 0.4, alpha])
                alpha_samples.append(sample(group)[3])
            check("source alpha zero/one/negative/HDR is preserved", alpha_samples, [-0.2, 0, 1, 2])
            source["color"].setValue([0.2, 1, 0.4, 0.37])

            configure(group, layered_source, layered_limit, limit_channel="despillLimit.amount")
            check("custom single-channel layer drives limiter", sample(group), [0.2, 0.21, 0.4, 0.37])
            check("unrelated source auxiliary layer is preserved", sample(group, ["despillAux.keep"]), [3.2])

            configure(group, source, limiter, color_input=color_image, color="red")
            check("image color actually overrides red picker with green", sample(group), [0.2, 0.24, 0.4, 0.37])
            configure(group, source, limiter, respill_input=respill_image, respill_color=[1, 1, 1])
            check("image respill actually supplies red-only replacement", sample(group), [0.2 + 0.76 * 0.7154, 0.24, 0.4, 0.37])
            for input_index, image in ((2, color_image), (4, respill_image)):
                configure(group, source)
                group.setInput(input_index, image)
                group["imagebased"].setValue(False)
                fact("color/respill input alone prevents hiding: input%s" % input_index, group["imagebased"].value())

            # The documented multiplier contract should hold across independent
            # algorithm branches; compare to the same operation with scalar tolerance.
            branch_cases = (
                ("maximum", {"mode": "maximum"}),
                ("minimum and spill matte", {"mode": "minimum", "output_alpha": True, "inverted_spill_matte": False}),
                ("custom weights", {"mode": "custom", "custom_weight": 0.5}),
                ("spill output", {"out": "spill", "output_alpha": True}),
                ("absolute and image inputs", {"absolute_mode": True, "respill_color": [0.6, 0.3, 0.1]}),
                ("log sandwich", {"log_space": True}),
                ("custom picked hue", {"color": "custom", "pick": [0.2, 1.0, 0.1], "hue_offset": 7}),
                ("negative HDR source", {}),
            )
            for index, (name, options) in enumerate(branch_cases):
                source["color"].setValue([-0.2, 2.5, 0.4, 0.37] if name == "negative HDR source" else [0.2, 1, 0.4, 0.37])
                images = {"color_input": color_image, "respill_input": respill_image} if name == "absolute and image inputs" else {}
                invert = index % 2 == 1
                effective = 0.3 if invert else 0.7
                configure(group, source, layered_limit, limit_channel="despillLimit.amount", invert_limit_channel=invert, **images, **options)
                configure(reference, source, tolerance=effective, **images, **options)
                check("documented limit multiplier: " + name, sample(group), sample(reference))

            source["color"].setValue([0.2, 1, 0.4, 0.37])
            configure(group, layered_source, layered_limit, color_input=color_image, respill_input=respill_image,
                      limit_channel="despillLimit.amount", invert_limit_channel=True,
                      respill_color=[0.7, 0.2, 0.1], mode="maximum")
            expected = {"rgba": sample(group), "aux": sample(group, ["despillAux.keep"]), "channel": group["limit_channel"].value()}
            EXPECTED.write_text(json.dumps(expected, indent=2))
            nuke.scriptSaveAs(str(SCENE), overwrite=1)
            fact("full script saved for fresh-process reload", SCENE.is_file())
            group_view_serialization()

    except Exception:
        report["failures"].append("Unhandled exception")
        report["exception"] = traceback.format_exc()
    finally:
        report["ok"] = not report["failures"]
        REPORT.write_text(json.dumps(report, indent=2))
        print("APDESPILL_TEST", VERSION, PHASE, report["ok"], len(report["checks"]), str(REPORT))
        if report.get("exception"):
            print(report["exception"])
        for node in nuke.allNodes("Group"):
            node["knobChanged"].setValue("")

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    # Never clear or exit an artist's GUI session, even if pasted into Script Editor.
    if nuke.GUI or "--safe" not in nuke.rawArgs:
        raise RuntimeError("Run in a separate Nuke --safe -ti terminal process")
    try:
        status = main()
    except SystemExit as error:
        status = int(error.code or 0)
    except Exception:
        traceback.print_exc()
        status = 1
    # Remove only this isolated process's test graph before terminating.
    for node in nuke.allNodes("Group"):
        node["knobChanged"].setValue("")
    nuke.scriptClear(ignoreUnsavedChanges=True)
    sys.stdout.flush()
    sys.stderr.flush()
    if status:
        # Nuke may catch Python exceptions/SystemExit and otherwise return zero.
        os._exit(status)
    nuke.scriptExit()
