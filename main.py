"""
Launcher so `uvicorn main:app --reload` works from the project root.
Loads the FastAPI app from fastapi-tasks/main.py (folder has a hyphen so not importable as a package).
"""
import importlib.util
from pathlib import Path

_root = Path(__file__).resolve().parent
_main_py = _root / "fastapi-tasks" / "main.py"

if not _main_py.exists():
    raise FileNotFoundError(
        f"App not found at {_main_py}. Run uvicorn from fastapi-tasks/: cd fastapi-tasks && uvicorn main:app --reload"
    )

_spec = importlib.util.spec_from_file_location("main", _main_py)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

app = _module.app
