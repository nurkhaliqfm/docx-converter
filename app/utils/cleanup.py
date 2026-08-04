import shutil
from pathlib import Path


def cleanup_tmp_dir(path: Path):
    shutil.rmtree(path, ignore_errors=True)
