"""The read-only boundary, enforced rather than promised.

The twin advises and never writes to line control. In ISA-95 terms it sits
strictly above the control layer: it reads what the plant already emits and
returns advice to a human, who decides.

That claim appears in the proposal, on every screen of the dashboard, and in
the phased roadmap, where "never closed-loop write to line control" is the one
phase that never arrives. A claim carried that prominently should not rest on
the authors remembering to keep it true, so this module checks it structurally.

The rule: exactly two modules may write anything at all - `store.py` (our own
SQLite) and `sink.py` (our own JSONL). Every other module in the twin is pure.
Nothing anywhere opens an outbound network connection.

If a future change adds a write path, one of these tests fails and names the
file, which is the point. Should a genuine new sink ever be needed, it is added
to ALLOWED_WRITERS deliberately and in the open, not by accident.
"""

import ast
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
SRC = os.path.join(ROOT, "src", "twin")
WEB = os.path.join(ROOT, "web")

# The only two modules permitted to write, and only ever to our own outputs.
ALLOWED_WRITERS = {"store.py", "sink.py"}

# Simulator modules generate the sample datasets offline. They are not part of
# the live twin and never run against a plant, but they are held to the network
# rule like everything else.
SIMULATOR = {"plant.py", "line.py", "tools.py", "layouts.py"}

# Calls that write, whatever they are called on. These names are unambiguous:
# nothing in the standard library or pandas uses them for anything but output.
WRITE_CALLS = {
    "to_csv", "to_sql", "to_parquet", "to_pickle",
    "write", "writelines", "writerow", "writerows",
    "write_text", "write_bytes",
    "executemany", "executescript",
}

# Filesystem mutations are only writes when called on the filesystem modules.
# Checked as a dotted pair because the bare names collide with entirely
# innocent methods - pandas `.rename(columns=...)` and `str.replace()` both
# appear in this codebase and neither touches a disk.
FS_MODULES = {"os", "shutil", "path"}
FS_CALLS = {
    "mkdir", "makedirs", "remove", "unlink", "rmdir", "rename", "replace",
    "rmtree", "copy", "copy2", "copyfile", "move", "touch",
}

# Anything that could reach the plant network - a PLC, an OPC-UA server, an
# MQTT broker, a historian. None of these may appear anywhere.
NETWORK_MODULES = {
    "socket", "requests", "urllib", "urllib3", "http", "httpx",
    "asyncua", "opcua", "paho", "pymodbus", "snap7", "aiohttp",
}

SQL_WRITE_KEYWORDS = ("INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER")


def _python_files(directory):
    out = []
    for dirpath, dirnames, filenames in os.walk(directory):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for fn in sorted(filenames):
            if fn.endswith(".py"):
                out.append(os.path.join(dirpath, fn))
    return out


def _parse(path):
    with open(path, "r", encoding="utf-8") as fh:
        return ast.parse(fh.read(), filename=path)


ALL_FILES = _python_files(SRC) + _python_files(WEB)


def test_files_were_found():
    """Guard against the scan silently passing because it found nothing."""
    assert len(ALL_FILES) >= 10, f"only found {len(ALL_FILES)} files to scan"


@pytest.mark.parametrize("path", ALL_FILES, ids=lambda p: os.path.basename(p))
def test_only_designated_modules_write(path):
    """No module outside store.py and sink.py performs any write."""
    name = os.path.basename(path)
    if name in ALLOWED_WRITERS or name in SIMULATOR:
        pytest.skip(f"{name} is a designated writer or an offline builder")

    offenders = []
    for node in ast.walk(_parse(path)):
        # foo.to_csv(...) / fh.write(...) / cur.executemany(...)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in WRITE_CALLS:
                offenders.append(f"line {node.lineno}: .{node.func.attr}()")
            # os.remove(...) / shutil.rmtree(...) - only when on a fs module
            elif node.func.attr in FS_CALLS:
                owner = node.func.value
                owner_name = owner.id if isinstance(owner, ast.Name) else (
                    owner.attr if isinstance(owner, ast.Attribute) else ""
                )
                if owner_name.lower() in FS_MODULES:
                    offenders.append(
                        f"line {node.lineno}: {owner_name}.{node.func.attr}()"
                    )
        # open(path, "w") / open(path, "a")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "open":
                mode = ""
                if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                    mode = str(node.args[1].value)
                for kw in node.keywords:
                    if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                        mode = str(kw.value.value)
                if any(c in mode for c in ("w", "a", "x", "+")):
                    offenders.append(f"line {node.lineno}: open(mode={mode!r})")

    assert not offenders, (
        f"{name} writes, but only {sorted(ALLOWED_WRITERS)} may:\n  "
        + "\n  ".join(offenders)
    )


@pytest.mark.parametrize("path", ALL_FILES, ids=lambda p: os.path.basename(p))
def test_no_outbound_network(path):
    """Nothing in the twin can reach the plant network.

    The twin is fed by an adapter that reads the plant's own historian or MES
    export. It never dials out, so it cannot reach a PLC even by mistake.
    """
    offenders = []
    for node in ast.walk(_parse(path)):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name.split(".")[0] in NETWORK_MODULES:
                    offenders.append(f"line {node.lineno}: import {a.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[0] in NETWORK_MODULES:
                offenders.append(f"line {node.lineno}: from {node.module} import ...")

    assert not offenders, (
        f"{os.path.basename(path)} imports a network client:\n  "
        + "\n  ".join(offenders)
    )


def test_sql_writes_are_confined_to_our_own_tables():
    """store.py may write, but only to the twin's own database.

    A write here is a record of what the twin decided. It must never be a
    write back into a plant system, so every statement is checked to name a
    table the twin itself owns.
    """
    own_tables = {
        "sessions", "frames", "rankings", "forming",
        "alerts", "shifts", "tool_assessments", "manual_checks",
    }
    with open(os.path.join(SRC, "store.py"), "r", encoding="utf-8") as fh:
        source = fh.read()

    unknown = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
            continue
        text = node.value
        upper = text.upper()
        if not any(k in upper for k in SQL_WRITE_KEYWORDS):
            continue
        if not any(t in text for t in own_tables):
            # Allow pragmas and index statements, which name no table.
            if "PRAGMA" in upper or "INDEX" in upper:
                continue
            unknown.append(text.strip().split("\n")[0][:80])

    assert not unknown, (
        "store.py contains a write naming no table the twin owns:\n  "
        + "\n  ".join(unknown)
    )


def test_the_frame_declares_itself_advisory():
    """Every frame the twin emits is labelled advisory, not a command."""
    with open(os.path.join(SRC, "loop.py"), "r", encoding="utf-8") as fh:
        assert '"advisory_only": True' in fh.read(), (
            "loop.py no longer marks its output advisory_only"
        )
