"""Native apGlow regression tests; run in a fresh Nuke --safe -ti process.

Only Nuke and the Python standard library are required. Fixtures, copied graphs,
and saved scripts are generated in a TemporaryDirectory and removed after use.
"""

import argparse
import __main__
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
import traceback

import nuke


SOURCE_PATH = Path(__file__).resolve().parents[1] / "NukeSurvivalToolkit" / "gizmos" / "NST_apeGlow.gizmo"
REPRESENTATIONS = ("APGlowGroupTest", "APGlowGizmoTest")
STEPS = (1, 3, 10, 11, 0)
INPUT_ROLES = ("apglow-test:image", "apglow-test:area", "apglow-test:mask")
SAMPLE_POINTS = ((4, 4), (23, 31), (32, 32), (41, 31), (60, 60))
PIXEL_TOLERANCE = 1e-6


def describe(node):
    """Capture graph behavior rather than serialized source formatting."""
    merge = node.node("MergeBlurs")
    return {
        "name": node.fullName(),
        "class": node.Class(),
        "steps": int(node["s"].value()),
        "inputs": [node.input(i).fullName() if node.input(i) else None for i in range(3)],
        "input_roles": [node.input(i)["label"].value() if node.input(i) else None for i in range(3)],
        "blurs": sorted(child.name() for child in node.nodes() if child.Class() == "Blur"),
        "merge_inputs": [merge.input(i).name() if merge.input(i) else None for i in range(merge.inputs())],
    }


def samples(node):
    values = [
        float(nuke.sample(node, channel, x, y))
        for x, y in SAMPLE_POINTS
        for channel in ("red", "green", "blue", "alpha")
    ]
    if not all(math.isfinite(value) for value in values):
        raise AssertionError("apGlow produced a non-finite sample")
    return values


def sample_delta(first, second):
    if len(first) != len(second):
        raise AssertionError("Sample sets have different lengths")
    return max(abs(a - b) for a, b in zip(first, second))


def selection(group):
    return sorted(node.name() for node in group.nodes() if node.isSelected())


def check(case, name, passed):
    case["checks"][name] = bool(passed)


def graph_matches(snapshot, steps, input_names):
    return snapshot["steps"] == steps and len(snapshot["blurs"]) == steps and snapshot["inputs"] == input_names


def reset_owned_history():
    """Discard only this standalone test process's fixture/setup history."""
    undo = nuke.Undo()
    undo.undoTruncate(0)
    undo.redoTruncate(0)


def check_group_view(case, prefix, node):
    knob = node.knob("disable_group_view")
    # Older releases have no native Group View setting. Modern Nuke must expose
    # it on the shipped Group; real Gizmos do not expose this native Group knob.
    # Every representation must omit its native value when saving.
    required = node.Class() == "Group" and nuke.NUKE_VERSION_MAJOR >= 17
    case.setdefault("group_view", {})[prefix] = {"class": node.Class(), "exists": knob is not None}
    check(case, prefix + "_group_view_available", knob is not None or not required)
    if knob is not None:
        check(case, prefix + "_group_view_disabled", bool(knob.value()))
        check(case, prefix + "_group_view_not_written", knob.getFlag(nuke.DO_NOT_WRITE))


def no_serialized_group_view(path):
    # The callback itself mentions this knob; inspect native knob-value lines,
    # not arbitrary occurrences inside its serialized Python source.
    return re.search(r"^\s*disable_group_view\s+", path.read_text(encoding="utf-8"), re.MULTILINE) is None


def fresh_regression_glow(case):
    nuke.scriptClear()
    source = nuke.nodes.Constant(name="RegressionSource")
    glow = nuke.createNode(case["representation"], inpanel=False)
    glow.setInput(0, source)
    reset_owned_history()
    return source, glow


def run_matrix_case(case, workdir):
    """Edit, undo, paste and reopen one Group/Gizmo graph in isolation."""
    nuke.scriptClear()
    nuke.root()["format"].setValue(nuke.addFormat("64 64 0 0 64 64 1 apGlowTest64"))
    parent = nuke.nodes.Group(name="Parent") if case["nested"] else nuke.root()
    expected_steps = max(1, case["requested_steps"])
    with parent:
        base = nuke.nodes.Constant(name="SourceBase")
        base["color"].setValue([1, 1, 1, 1])
        image = nuke.nodes.Expression(name="Image", inputs=[base])
        image["expr0"].setValue("x>=24 && x<40 && y>=24 && y<40 ? 1 : 0")
        image["expr1"].setValue("r*0.4")
        image["expr2"].setValue("r*0.1")
        area = nuke.nodes.Constant(name="Area")
        area["color"].setValue([1, 1, 1, 1])
        mask = nuke.nodes.Constant(name="Mask")
        mask["color"].setValue([1, 1, 1, 1])
        input_nodes = (image, area, mask)
        for node, role in zip(input_nodes, INPUT_ROLES):
            node["label"].setValue(role)
        sentinel = nuke.nodes.NoOp(name="ExternalSentinel", inputs=[image])
        sentinel.setXYpos(1000, 1000)
        glow = nuke.createNode(case["representation"], inpanel=False)
        for index, node in enumerate(input_nodes):
            glow.setInput(index, node)
        glow["channels"].setValue("rgba")
        glow["max_size"].setValue([20, 20])
        glow["p"].setValue([0.9, 0.7, 0.5])
        expected_class = "Group" if case["representation"] == REPRESENTATIONS[0] else REPRESENTATIONS[1]
        check(case, "native_representation", glow.Class() == expected_class)
        with glow:
            note = nuke.nodes.NoOp(name="UserNote", inputs=[])
            note.setXYpos(2000, 2000)
            for child in glow.nodes():
                child.setSelected(child.name() in ("Blur0", "UserNote"))
        for node in parent.nodes():
            node.setSelected(node == sentinel)

        context_before = nuke.thisGroup().fullName()
        undo_disabled_before = nuke.Undo().disabled()
        selected_before = selection(parent)
        inner_selection_before = selection(glow)
        input_names = [node.fullName() for node in input_nodes]
        original_name = glow.fullName()
        check_group_view(case, "created", glow)
        reset_owned_history()
        undo = nuke.Undo()
        undo.begin("apGlow steps regression")
        try:
            glow["s"].setValue(case["requested_steps"])
        finally:
            undo.end()

        case["changed"] = describe(glow)
        check(case, "step_graph", graph_matches(case["changed"], expected_steps, input_names))
        check(case, "group_context", nuke.thisGroup().fullName() == context_before)
        check(case, "undo_state", nuke.Undo().disabled() == undo_disabled_before)
        check(case, "external_selection", selection(parent) == selected_before)
        check(case, "internal_user_note_survives", glow.node("UserNote") is not None)
        check(case, "internal_selection", selection(glow) == inner_selection_before)
        check(case, "external_sentinel", sentinel.input(0) == image)
        case["samples"] = samples(glow)

        if case["requested_steps"] == 3:
            undo.undo()
            case["undo"] = describe(glow)
            check(case, "undo", graph_matches(case["undo"], 10, input_names))
            undo.redo()
            case["redo"] = describe(glow)
            check(case, "redo", graph_matches(case["redo"], 3, input_names))
            case["redo_sample_max_delta"] = sample_delta(case["samples"], samples(glow))
            check(case, "redo_pixels", case["redo_sample_max_delta"] < PIXEL_TOLERANCE)

        for node in parent.nodes():
            node.setSelected(node in (base, image, area, mask, glow))
        original_nodes = set(parent.nodes())
        copy_path = workdir / "copy.nk"
        nuke.nodeCopy(copy_path.as_posix())
        check(case, "copy_omits_native_group_view", no_serialized_group_view(copy_path))
        nuke.nodePaste(copy_path.as_posix())
        added_nodes = set(parent.nodes()) - original_nodes
        pasted = next(node for node in added_nodes if node.knob("s") is not None)
        case["pasted"] = describe(pasted)
        check(case, "paste_inputs", case["pasted"]["input_roles"] == list(INPUT_ROLES))
        check(case, "paste_uses_copied_inputs", all(pasted.input(i) in added_nodes for i in range(3)))
        check(case, "paste_root_nodes", len(added_nodes) == 5)
        check(case, "paste_step_graph", case["pasted"]["steps"] == expected_steps and len(case["pasted"]["blurs"]) == expected_steps)
        case["paste_sample_max_delta"] = sample_delta(case["samples"], samples(pasted))
        check(case, "paste_pixels", case["paste_sample_max_delta"] < PIXEL_TOLERANCE)
        pasted_name = pasted.fullName()
        check_group_view(case, "pasted", pasted)

    save_path = workdir / "reload.nk"
    nuke.scriptSaveAs(save_path.as_posix(), overwrite=1)
    check(case, "save_omits_native_group_view", no_serialized_group_view(save_path))
    nuke.scriptClear()
    nuke.scriptOpen(save_path.as_posix())
    reopened = nuke.toNode(original_name)
    reopened_copy = nuke.toNode(pasted_name)
    case["reopened"] = describe(reopened)
    case["reopened_copy"] = describe(reopened_copy)
    for name, node in (("original", reopened), ("copy", reopened_copy)):
        check_group_view(case, "reopened_" + name, node)
        snapshot = describe(node)
        check(case, "reload_" + name + "_inputs", snapshot["input_roles"] == list(INPUT_ROLES))
        check(case, "reload_" + name + "_steps", snapshot["steps"] == expected_steps and len(snapshot["blurs"]) == expected_steps)
        delta = sample_delta(case["samples"], samples(node))
        case["reload_" + name + "_sample_max_delta"] = delta
        check(case, "reload_" + name + "_pixels", delta < PIXEL_TOLERANCE)


def run_disabled_undo_case(case, workdir):
    """A caller's disabled undo scope must stay disabled and remain balanced."""
    nuke.scriptClear()
    source = nuke.nodes.Constant(name="UndoSource")
    glow = nuke.createNode(case["representation"], inpanel=False)
    glow.setInput(0, source)
    undo = nuke.Undo()
    undo.disable()
    try:
        case["before"] = undo.disabled()
        glow["s"].setValue(3)
        case["after"] = undo.disabled()
    finally:
        undo.enable()
    check(case, "scope_stays_disabled", case["before"] and case["after"])
    check(case, "scope_balances", not undo.disabled())
    check(case, "input_preserved", glow.input(0) == source)
    check(case, "step_graph", len(describe(glow)["blurs"]) == 3)


def run_namespace_case(case, workdir):
    source, glow = fresh_regression_glow(case)
    names = ("node", "n", "k", "saved_stack", "selected_names", "undo", "branches",
             "mult", "blur", "item", "index", "s", "nd", "nm", "b0", "b0x", "b0y", "b0n")
    absent = object()
    previous = {name: __main__.__dict__.get(name, absent) for name in names}
    sentinels = {name: object() for name in names}
    try:
        __main__.__dict__.update(sentinels)
        glow["s"].setValue(3)
        overwritten = [name for name in names if __main__.__dict__.get(name) is not sentinels[name]]
        case["overwritten_globals"] = overwritten
        check(case, "caller_globals_preserved", not overwritten)
        check(case, "private_helper_cleaned", "_apglow_knob_changed" not in __main__.__dict__)
        check(case, "graph_rebuilt", len(describe(glow)["blurs"]) == 3)
    finally:
        for name, value in previous.items():
            if value is absent:
                __main__.__dict__.pop(name, None)
            else:
                __main__.__dict__[name] = value


def run_duplicate_merge_case(case, workdir):
    source, glow = fresh_regression_glow(case)
    merge = glow.node("MergeBlurs")
    merge.setInput(12, merge.input(1))
    disabled_before = nuke.Undo().disabled()
    glow["s"].setValue(3)
    case["changed"] = describe(glow)
    check(case, "duplicate_branch_deleted_once", len(case["changed"]["blurs"]) == 3)
    check(case, "correct_merge_inputs", case["changed"]["merge_inputs"] == ["Multiply0", "Multiply1", None, "Multiply2"])
    check(case, "undo_state_restored", nuke.Undo().disabled() == disabled_before)
    check(case, "external_input_preserved", glow.input(0) == source)


def run_custom_branch_case(case, workdir):
    source, glow = fresh_regression_glow(case)
    with glow:
        data = glow.node("DP")
        blur = nuke.nodes.Blur(name="UserSoftening", inputs=[data])
        blur.setXYpos(data.xpos() - 300, data.ypos())
        mult = nuke.nodes.Multiply(name="UserArtDirection", inputs=[blur])
        mult.setXYpos(data.xpos() - 300, data.ypos() + 100)
        glow.node("MergeBlurs").setInput(12, mult)
    for steps in (3, 5, 3):
        glow["s"].setValue(steps)
    check(case, "custom_blur_preserved", glow.node("UserSoftening") == blur)
    check(case, "custom_multiply_preserved", glow.node("UserArtDirection") == mult)
    check(case, "custom_topology_preserved", mult.input(0) == blur and blur.input(0) == data)
    check(case, "custom_merge_port_preserved", glow.node("MergeBlurs").input(12) == mult)
    check(case, "external_input_preserved", glow.input(0) == source)


def run_shared_consumer_case(case, workdir):
    source, glow = fresh_regression_glow(case)
    with glow:
        blur = glow.node("Blur1")
        mult = glow.node("Multiply1")
        blur_tap = nuke.nodes.NoOp(name="UserBlurTap", inputs=[blur])
        mult_tap = nuke.nodes.NoOp(name="UserMultiplyTap", inputs=[mult])
    for steps in (3, 5, 3):
        glow["s"].setValue(steps)
    # nuke.delete can silently bypass a removed node, so non-null inputs alone
    # would miss the regression. Require the exact original endpoints.
    check(case, "shared_blur_endpoint_preserved", blur_tap.input(0) == blur)
    check(case, "shared_multiply_endpoint_preserved", mult_tap.input(0) == mult)
    check(case, "shared_merge_port_preserved", glow.node("MergeBlurs").input(1) == mult)
    check(case, "external_input_preserved", glow.input(0) == source)


def run_mask_port_case(case, workdir):
    source, glow = fresh_regression_glow(case)
    merge = glow.node("MergeBlurs")
    blur = glow.node("Blur1")
    mult = glow.node("Multiply1")
    merge.setInput(2, mult)
    for steps in (3, 5, 3):
        glow["s"].setValue(steps)
    # Merge2's image input1 and mask input2 are distinct uses of the same node;
    # dependent-node identity alone cannot distinguish their roles.
    check(case, "mask_endpoint_preserved", merge.input(2) == mult)
    check(case, "shared_image_endpoint_preserved", merge.input(1) == mult)
    check(case, "mask_blur_preserved", glow.node("Blur1") == blur)
    check(case, "mask_topology_preserved", mult.input(0) == blur and blur.input(0) == glow.node("DP"))
    check(case, "external_input_preserved", glow.input(0) == source)


def run_repeated_history_case(case, workdir):
    source, glow = fresh_regression_glow(case)
    undo = nuke.Undo()
    history = [(10, 10)]
    for steps in (3, 7, 0, 11):
        undo.begin("apGlow repeated steps " + str(steps))
        try:
            glow["s"].setValue(steps)
        finally:
            undo.end()
        history.append((int(glow["s"].value()), len(describe(glow)["blurs"])))
    undos = []
    for unused in range(4):
        undo.undo()
        undos.append((int(glow["s"].value()), len(describe(glow)["blurs"])))
    redos = []
    for unused in range(4):
        undo.redo()
        redos.append((int(glow["s"].value()), len(describe(glow)["blurs"])))
    case.update(history=history, undos=undos, redos=redos)
    check(case, "normalized_step_history", history == [(10, 10), (3, 3), (7, 7), (1, 1), (11, 11)])
    check(case, "repeated_undo", undos == list(reversed(history[:-1])))
    check(case, "repeated_redo", redos == history[1:])
    check(case, "external_input_preserved", glow.input(0) == source)


def record_case(report, case, runner, workdir):
    report["cases"].append(case)
    case["checks"] = {}
    reset_owned_history()
    try:
        runner(case, workdir)
    except Exception:
        case["error"] = traceback.format_exc()
    case["passed"] = not case.get("error") and bool(case["checks"]) and all(case["checks"].values())
    failed = [name for name, passed in case["checks"].items() if not passed]
    print("{} {}{}".format("PASS" if case["passed"] else "FAIL", case["id"], ": " + ", ".join(failed) if failed else ""), flush=True)
    if case.get("error"):
        print(case["error"], file=sys.stderr, flush=True)


def run_suite():
    source_bytes = SOURCE_PATH.read_bytes()
    source = source_bytes.decode("utf-8").replace("\r\n", "\n")
    if not source.startswith("Group {\n"):
        raise AssertionError("The production apGlow tool must retain its Group header")
    report = {
        "nuke_version": nuke.NUKE_VERSION_STRING,
        "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "pixel_tolerance": PIXEL_TOLERANCE,
        "cases": [],
    }
    undo = nuke.Undo()
    undo_was_disabled = undo.disabled()
    if undo_was_disabled:
        undo.enable()
    try:
        if undo.disabled():
            raise AssertionError("Could not enable undo in the isolated test process")
        with tempfile.TemporaryDirectory(prefix="nst-apglow-") as directory:
            workdir = Path(directory)
            for class_name, header in zip(REPRESENTATIONS, ("Group {", "Gizmo {")):
                (workdir / (class_name + ".gizmo")).write_text(source.replace("Group {", header, 1), encoding="utf-8")
            nuke.pluginAddPath(workdir.as_posix())
            for class_name in REPRESENTATIONS:
                for nested in (False, True):
                    for steps in STEPS:
                        case = {
                            "id": "{}/{}/steps={}".format(class_name, "nested" if nested else "root", steps),
                            "representation": class_name,
                            "nested": nested,
                            "requested_steps": steps,
                        }
                        record_case(report, case, run_matrix_case, workdir)
            for class_name in REPRESENTATIONS:
                case = {"id": class_name + "/disabled-undo", "representation": class_name}
                record_case(report, case, run_disabled_undo_case, workdir)
            for class_name in REPRESENTATIONS:
                for suffix, runner in (
                    ("namespace", run_namespace_case),
                    ("duplicate-merge-input", run_duplicate_merge_case),
                    ("custom-branch-port", run_custom_branch_case),
                    ("shared-generated-consumers", run_shared_consumer_case),
                    ("shared-image-and-mask-port", run_mask_port_case),
                    ("repeated-undo-history", run_repeated_history_case),
                ):
                    case = {"id": class_name + "/" + suffix, "representation": class_name}
                    record_case(report, case, runner, workdir)
    finally:
        if undo_was_disabled:
            undo.disable()
    report["passed"] = all(case["passed"] for case in report["cases"]) and len(report["cases"]) == 34
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, help="Optional JSON report path; generated output is not part of the repository")
    args = parser.parse_args(argv)
    try:
        report = run_suite()
    except Exception:
        report = {"nuke_version": nuke.NUKE_VERSION_STRING, "passed": False, "error": traceback.format_exc(), "cases": []}
        print(report["error"], file=sys.stderr, flush=True)
    if args.report is not None:
        try:
            args.report.expanduser().write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        except Exception:
            report["passed"] = False
            print("Could not write the requested report:", file=sys.stderr)
            traceback.print_exc()
    passed = sum(case["passed"] for case in report["cases"])
    print("apGlow: {}/{} cases passed; {}".format(passed, len(report["cases"]), "PASS" if report["passed"] else "FAIL"), flush=True)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    # Refuse before clearing nodes or exiting: this file is never a Script Editor tool.
    if nuke.GUI or nuke.root().nodes():
        raise RuntimeError("Run this test in a fresh standalone Nuke --safe -ti process with an empty graph")
    status = main()
    sys.stdout.flush()
    sys.stderr.flush()
    # Cleanup and reporting have completed. Exiting the owned process directly
    # also avoids unrelated legacy Nuke teardown errors after a successful run.
    os._exit(status)
