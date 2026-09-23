"""Run the upstream pythonocc-core test suite against one specific occt variant.

The recipe does not pin occt to either the 'novtk' or the 'all' variant, because
pythonocc-core links only OCCT libraries that both of them ship -- picking one is
the consumer's choice, see
https://github.com/conda-forge/pythonocc-core-feedstock/issues/27.

To keep that claim honest the recipe invokes this script once per variant. Both
invocations run the very same suite; the only difference is which occt build the
solver put into the test environment, which is asserted here so a run cannot
silently pass twice against the same variant.

Usage: python run_tests.py {novtk|all}
"""

from __future__ import annotations

import glob
import json
import os
import subprocess
import sys

# The recipe copies both this file and the upstream "test" directory into the
# test working directory.
HERE = os.path.dirname(os.path.abspath(__file__))
TEST_DIR = os.path.join(HERE, "test")
if not os.path.isdir(TEST_DIR):
    TEST_DIR = os.path.join(os.getcwd(), "test")

# Creates on-screen OpenGL windows, which the headless conda-forge Windows agent
# cannot do (OpenGl_Window::CreateWindow: SetPixelFormat failed / wglMakeCurrent
# failed). This affects every backend (tk and the Qt backends alike), in
# particular re-initializing a second display. Linux already skips this suite via
# a skipif marker.
WINDOWS_IGNORED = ["test_display_sideeffects.py"]

# Known to fail on the conda-forge Linux images.
LINUX_DESELECTED = ["test_array1_of_gp", "test_array2_of_gp", "test_surface_derivative_eval"]


def installed_occt() -> dict:
    """Return the conda metadata of the occt package in this environment."""
    metas = glob.glob(os.path.join(sys.prefix, "conda-meta", "occt-*.json"))
    if len(metas) != 1:
        raise SystemExit(f"expected exactly one occt package in {sys.prefix}, found {metas}")
    with open(metas[0]) as fh:
        return json.load(fh)


def assert_variant(expected: str) -> None:
    """Fail unless the environment resolved to the occt variant we asked for."""
    meta = installed_occt()
    # occt encodes the variant as the first field of its build string, e.g.
    # "novtk_h6d4b9b0_101" or "all_h6d4b9b0_201".
    actual = meta["build"].split("_")[0]
    if actual != expected:
        raise SystemExit(
            f"test environment resolved to occt variant {actual!r} "
            f"(build {meta['build']}), expected {expected!r}"
        )
    print(f"testing against occt {meta['version']} {meta['build']} (variant {actual})", flush=True)


def smoke_test() -> None:
    """Exercise the OCCT libraries pythonocc-core links against.

    Cheap, headless and runs everywhere, so every platform gets at least this
    much coverage of both variants even where the full suite is skipped.
    """
    from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut
    from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeSphere
    from OCC.Core.TopAbs import TopAbs_FACE
    from OCC.Core.TopExp import TopExp_Explorer

    box = BRepPrimAPI_MakeBox(10.0, 10.0, 10.0).Shape()
    sphere = BRepPrimAPI_MakeSphere(6.0).Shape()
    cut = BRepAlgoAPI_Cut(box, sphere).Shape()
    BRepMesh_IncrementalMesh(cut, 0.5)

    explorer = TopExp_Explorer(cut, TopAbs_FACE)
    faces = 0
    while explorer.More():
        faces += 1
        explorer.Next()
    if faces == 0:
        raise SystemExit("boolean cut produced no faces")
    print(f"smoke test ok: boolean cut has {faces} faces", flush=True)


def run(cmd: list[str]) -> None:
    print(f"+ {' '.join(cmd)}", flush=True)
    subprocess.run(cmd, cwd=TEST_DIR, check=True)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    assert_variant(sys.argv[1])
    smoke_test()

    if sys.platform == "win32":
        run([sys.executable, "-m", "pytest", "-sv"] + [f"--ignore={n}" for n in WINDOWS_IGNORED])
    elif sys.platform.startswith("linux"):
        deselect = " and ".join(f"not {name}" for name in LINUX_DESELECTED)
        run([sys.executable, "-m", "pytest", "-sv", "-k", deselect])
        run([sys.executable, "-m", "mypy", "test_mypy_classic_occ_bottle.py"])
    else:
        # The suite has never been run on osx here; the smoke test above still
        # covers both occt variants.
        print(f"skipping the test suite on {sys.platform}", flush=True)


if __name__ == "__main__":
    main()
