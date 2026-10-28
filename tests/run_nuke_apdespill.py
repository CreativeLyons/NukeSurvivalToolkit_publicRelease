"""Run apDespill tests in owned, bounded native Nuke processes (stdlib only)."""
import argparse
from pathlib import Path
import hashlib
import json
import os
import subprocess
import tempfile


def main(argv=None):
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nuke", type=Path, action="append", required=True,
                        help="Nuke executable; repeat for multiple versions")
    parser.add_argument("--output", type=Path,
                        help="Parent for a unique evidence directory; defaults to system temporary storage")
    parser.add_argument("--timeout", type=float, default=120,
                        help="Maximum seconds per owned Nuke process (default: 120)")
    parser.add_argument("--skip-reload", action="store_true",
                        help="Run numeric checks only, without a second process for full-script reload")
    parser.add_argument("--gizmo", type=Path,
                        default=root / "NukeSurvivalToolkit/gizmos/NST_apDespill.gizmo",
                        help="Candidate apDespill file; defaults to this checkout")
    args = parser.parse_args(argv)
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    gizmo = args.gizmo.expanduser().resolve()
    before = hashlib.sha256(gizmo.read_bytes()).hexdigest()
    headers = [root / "NukeSurvivalToolkit/gizmos" / name
               for name in ("NST_apDespill.gizmo", "NST_apeGlow.gizmo")]
    for path in headers:
        if not path.read_text(encoding="utf-8").lstrip().startswith("Group {"):
            parser.error("Portable Group header missing: " + path.name)
    if args.output:
        args.output = args.output.expanduser().resolve()
        args.output.mkdir(parents=True, exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix="apdespill_tests_", dir=args.output))
    script = Path(__file__).with_name("nuke_apdespill.py")
    failures = []
    phases = ("compute",) if args.skip_reload else ("compute", "reload")

    for index, executable in enumerate(args.nuke, 1):
        run_dir = output / ("nuke_%02d" % index)
        run_dir.mkdir()
        for phase in phases:
            command = [str(executable.expanduser().resolve()), "--safe", "-ti", str(script),
                       "--output", str(run_dir), "--phase", phase, "--gizmo", str(gizmo)]
            try:
                # subprocess.run kills and waits for its child on timeout.
                result = subprocess.run(command, cwd=root,
                                        env=dict(os.environ, QT_QPA_PLATFORM="offscreen"),
                                        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT, text=True, timeout=args.timeout)
                (run_dir / (phase + ".log")).write_text(result.stdout, encoding="utf-8")
                report = json.loads((run_dir / (phase + ".json")).read_text(encoding="utf-8"))
                checks = report.get("checks", [])
                passed = (result.returncode == 0 and report.get("ok") is True
                          and report.get("phase") == phase and report.get("gizmo_sha256") == before
                          and bool(checks) and all(item.get("passed") is True for item in checks))
                print("%s %s: %s (%d checks)" %
                      (report.get("nuke", "unknown"), phase, "PASS" if passed else "FAIL", len(checks)), flush=True)
                if not passed:
                    failures.append({"executable": str(executable), "phase": phase,
                                     "exit_code": result.returncode, "failures": report.get("failures", [])})
                    break
            except (OSError, ValueError, subprocess.TimeoutExpired) as error:
                # Partial output can still explain a timeout or license failure.
                partial = getattr(error, "stdout", None)
                if partial:
                    if isinstance(partial, bytes):
                        partial = partial.decode("utf-8", errors="replace")
                    (run_dir / (phase + ".log")).write_text(partial, encoding="utf-8")
                failures.append({"executable": str(executable), "phase": phase, "error": str(error)})
                break

    if hashlib.sha256(gizmo.read_bytes()).hexdigest() != before:
        failures.append({"error": "Candidate changed while tests were running"})
    if any(not path.read_text(encoding="utf-8").lstrip().startswith("Group {") for path in headers):
        failures.append({"error": "A portable Group header changed while tests were running"})
    summary = {"ok": not failures, "gizmo_sha256": before, "failures": failures}
    (output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("Evidence: " + str(output))
    if failures:
        print(json.dumps(failures, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
