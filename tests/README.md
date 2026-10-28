# Native Nuke regression tests

These tests use Nuke's actual nodes, pixel evaluation, callbacks and script
serialization. They require a Nuke executable and an appropriate license; no
third-party Python packages or external media are needed.

Run them in **new terminal processes**, never inside an artist's Script Editor.
The native scripts refuse GUI sessions and non-empty initial graphs. `--safe`
keeps the user's startup plugins out of the tests. All graphs are disposable.

## apGlow

From this checkout, replacing `Nuke` with the executable path:

```sh
Nuke --safe -ti tests/nuke_apglow.py --report /path/to/apglow-report.json
```

The optional report directory must already exist. The test generates temporary
Group and real-Gizmo fixtures from the production Group definition; the shipped
tool remains a self-contained Group. It checks root/nested contexts, step edits
and clamping, undo/redo, input roles, copy/paste and save/reopen, sampled pixels,
selection and customized internal state. Temporary fixtures are removed.

The 34 cases also cover callback namespace isolation, repeated step-edit history,
duplicate Merge inputs, custom branches and ports, shared internal consumers,
and a generated branch used as a mask. Each fixture owns its undo history.

## apDespill

Use an ordinary Python 3 interpreter to run the bounded process launcher:

```sh
python3 tests/run_nuke_apdespill.py --nuke /path/to/Nuke
```

Repeat `--nuke` to test several installed versions. `--timeout` controls the
maximum seconds for each owned child process. The runner creates a unique
evidence directory in system temporary storage, prints its location and retains
reports, logs and the synthetic scene for inspection. Use `--output` to choose
another parent directory.

The compute phase checks limit channels and inversion, scalar tolerance,
negative/HDR values, source alpha, missing channels, auxiliary layers, image
color/respill inputs and the supported output modes. A **second Nuke process**
reopens the saved scene and checks output, channels, connections and callbacks.

For a compute-only run directly in Nuke:

```sh
Nuke --safe -ti tests/nuke_apdespill.py --output /path/to/evidence
```

The same evidence can then be reopened in another fresh process:

```sh
Nuke --safe -ti tests/nuke_apdespill.py --phase reload --output /path/to/evidence
```

## Results and scope

Both suites write the exact production source SHA-256 in their reports and
return a nonzero process exit status on failure. The apDespill launcher also
checks the reports and verifies that its source did not change during the run.

Group View is disabled only when the native knob exists. Its value is excluded
from serialization, so a Group saved in a newer Nuke does not introduce that
unknown knob when loaded in an older version.

The tests use small procedural images and CPU evaluation. They establish the
listed graph/serialization and numerical behavior; they do not replace manual
interaction checks, full-frame shot review, GPU tests or tests on other
operating systems.

The complete suites were validated in macOS Nuke 17.0v1 and 17.1v1. The apGlow
suite also passes in Nuke 14.1v5. In 14.1v5, the full apDespill sampling suite
currently reports native `get(...), but request() not called` warnings and
subsequent zero samples; it is not claimed as a passing legacy regression run.
A separate small EXR render produces the expected limit result in both the
final tool and the upstream processing graph with corrected mappings. Guarded
Group View creation/serialization is independently checked across 17 and 14.
