import subprocess
import sys
from pathlib import Path
from langchain_core.tools import tool

from src.utils.paths import SANDBOX_DIR, get_sandbox_path


@tool
def write_sandbox_file(filename: str, content: str) -> str:
    """Creates or overwrites a file inside the sandbox directory.
    
    Args:
        filename: Relative file name/path (e.g., 'script.py' or 'data.txt').
        content: Code or text to write to the file.
    """
    try:
        target = get_sandbox_path(filename)
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            f.write(content)
        return f"OK: File '{filename}' was successfully written to the sandbox."
    except Exception as e:
        return f"File write error: {str(e)}"


@tool
def read_sandbox_file(filename: str) -> str:
    """Reads the contents of a file located within the sandbox directory.
    
    Args:
        filename: Relative file name/path (e.g., 'script.py').
    """
    try:
        target = get_sandbox_path(filename)
        if not target.exists():
            return f"Error: File '{filename}' does not exist in sandbox."
        with open(target, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"File read error: {str(e)}"


@tool
def list_sandbox_files() -> str:
    """Lists all files currently stored inside the sandbox directory."""
    try:
        files = [p.relative_to(SANDBOX_DIR).as_posix() for p in SANDBOX_DIR.rglob("*") if p.is_file()]
        if not files:
            return "The sandbox directory is empty."
        return "Files in sandbox:\n" + "\n".join(f"- {f}" for f in files)
    except Exception as e:
        return f"Listing error: {str(e)}"


@tool
def execute_python_sandbox_file(filename: str) -> str:
    """Executes a Python script located inside the sandbox directory and returns stdout/stderr.
    
    Args:
        filename: Name of the Python file in sandbox (e.g., 'solution.py').
    """
    try:
        target = get_sandbox_path(filename)
        if not target.exists():
            return f"Error: File '{filename}' does not exist."
        if target.suffix.lower() != ".py":
            return "Error: Only Python (.py) scripts can be executed."

        # Run within an isolated subprocess, setting working directory to sandbox
        process = subprocess.run(
            [sys.executable, str(target)],
            cwd=str(SANDBOX_DIR),
            capture_output=True,
            text=True,
            timeout=30  # Safety timeout to prevent infinite loops
        )

        output = process.stdout
        if process.stderr:
            output += f"\n[STDERR]:\n{process.stderr}"
        if not output.strip():
            output = "(Script completed with no console output)"

        return f"Execution result for '{filename}' (exit code {process.returncode}):\n{output}"
    except subprocess.TimeoutExpired:
        return f"Error: Script '{filename}' exceeded timeout limit (30s)."
    except Exception as e:
        return f"Execution error: {str(e)}"


# Export list of sandbox tools for agents
ALL_SANDBOX_TOOLS = [
    write_sandbox_file,
    read_sandbox_file,
    list_sandbox_files,
    execute_python_sandbox_file
]