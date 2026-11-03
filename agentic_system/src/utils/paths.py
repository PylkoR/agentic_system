from pathlib import Path


def get_project_root() -> Path:
    """Resolve the project root by locating 'agentic_system' or key project directories."""
    current_path = Path(__file__).resolve()

    for parent in [current_path] + list(current_path.parents):
        if parent.name == "agentic_system":
            return parent
        if (parent / "src").is_dir() and (parent / "sandbox").is_dir():
            return parent

    # Fallback assuming structure: src/utils/paths.py -> 3 levels up
    return current_path.parents[2]


ROOT_DIR: Path = get_project_root()

NOTEBOOKS_DIR: Path = ROOT_DIR / "notebooks"
SANDBOX_DIR: Path = ROOT_DIR / "sandbox"
SRC_DIR: Path = ROOT_DIR / "src"
TESTS_DIR: Path = ROOT_DIR / "tests"

AGENTS_DIR: Path = SRC_DIR / "agents"
TOOLS_DIR: Path = SRC_DIR / "tools"
UTILS_DIR: Path = SRC_DIR / "utils"

SANDBOX_DIR.mkdir(parents=True, exist_ok=True)


def get_sandbox_path(relative_filename: str) -> Path:
    """Resolve and validate a path inside sandbox, preventing path traversal."""
    target_path = (SANDBOX_DIR / relative_filename).resolve()
    if not str(target_path).startswith(str(SANDBOX_DIR)):
        raise PermissionError(
            f"Access denied: Attempted path traversal outside sandbox ({relative_filename})"
        )
    return target_path