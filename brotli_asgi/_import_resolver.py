"""Small utility to solve import conflicts."""

import importlib.util
from pathlib import Path

import starlette


def import_brotli():
    """Import official google brotli by path.

    If Brotlipy and Brotli (official version) are installed in the same environment it
    will create a import conflict.

    https://github.com/python-hyper/brotlipy/issues/145
    """
    pkg_folder = Path(starlette.__path__[0]).parent
    brotlipy_folder = pkg_folder / "brotli"

    if brotlipy_folder.exists():
        google_brotli = pkg_folder / "brotli.py"
        spec = importlib.util.spec_from_file_location("brotli", google_brotli)
        brotli = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(brotli)
    else:
        import brotli
    return brotli
