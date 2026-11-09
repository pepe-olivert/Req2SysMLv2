"""SysML v2 Pilot Implementation as a validator: a pool of persistent JVMs (tools/pilot/PilotServer.java).

Each server loads the standard library once and then validates one file per request in its own resource, so a
model never resolves names against another one. Used by the R11 repair loop (core/agents/agent2/pilot_repair.py).
"""

from __future__ import annotations

import queue
import subprocess
import tempfile
import threading
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE = REPO_ROOT / "tools" / "pilot" / "PilotServer.java"


def pilot_jar(sysml: Path) -> Path:
    """The kernel jar of an installed release; stops with instructions if the release is not installed."""
    jar = next(Path(sysml).glob("jupyter-sysml-kernel-*-all.jar"), None)
    if jar is None:
        raise SystemExit(f"error: SysML v2 Pilot Implementation not found in {sysml}. "
                         "Install releases 2024-04.1 and 2026-08 as explained in README.md, or pass its location.")
    return jar


class _Server:
    def __init__(self, release_dir: Path, classes: Path, scratch: Path) -> None:
        sysml = release_dir / "sysml"
        jar = pilot_jar(sysml)
        self.scratch = scratch
        self.proc = subprocess.Popen(
            ["java", "-Xmx1500m", "-cp", f"{jar}:{classes}", "PilotServer", str(sysml / "sysml.library") + "/"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, encoding="utf-8",
            bufsize=1)
        line = self.proc.stdout.readline()
        if line.strip() != "READY":
            raise RuntimeError(f"PilotServer did not start: {line!r}")

    def validate(self, code: str) -> list[dict]:
        path = self.scratch / f"{uuid.uuid4().hex}.sysml"
        path.write_text(code, encoding="utf-8")
        try:
            self.proc.stdin.write(str(path) + "\n")
            self.proc.stdin.flush()
            issues = []
            for line in self.proc.stdout:
                line = line.rstrip("\n")
                if line == "DONE":
                    break
                kind, severity, code_, line_no, column, message = (line.split("\t") + [""] * 6)[:6]
                issues.append({"kind": kind, "severity": severity, "code": code_,
                               "line": int(line_no) if line_no.isdigit() else None,
                               "column": int(column) if column.isdigit() else None, "message": message})
            else:
                raise RuntimeError("PilotServer closed its output")
            return issues
        finally:
            path.unlink(missing_ok=True)

    def close(self) -> None:
        try:
            self.proc.stdin.close()
            self.proc.wait(timeout=30)
        except Exception:
            self.proc.kill()


class PilotValidator:
    """Thread-safe pool of `size` Pilot servers of one release (e.g. ~/tools/pilot/2024-04.1)."""

    def __init__(self, release_dir: Path, size: int = 4) -> None:
        sysml = Path(release_dir) / "sysml"
        jar = pilot_jar(sysml)
        self.release = Path(release_dir).name
        classes = REPO_ROOT / "tools" / "pilot" / "build" / f"server-{self.release}"
        if not (classes / "PilotServer.class").exists():
            classes.mkdir(parents=True, exist_ok=True)
            subprocess.run(["javac", "-cp", str(jar), "-d", str(classes), str(SOURCE)], check=True)
        self._scratch = Path(tempfile.mkdtemp(prefix="pilot_"))
        self._pool: queue.Queue[_Server] = queue.Queue()
        servers = []
        threads = [threading.Thread(target=lambda: servers.append(_Server(Path(release_dir), classes, self._scratch)))
                   for _ in range(size)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        for s in servers:
            self._pool.put(s)
        self._all = servers

    def issues(self, code: str) -> list[dict]:
        server = self._pool.get()
        try:
            return server.validate(code)
        finally:
            self._pool.put(server)

    def errors(self, code: str) -> list[dict]:
        """ERROR issues only (warnings do not count), in the order the Pilot reports them."""
        return [i for i in self.issues(code) if i["severity"] == "ERROR" or i["kind"] == "EXCEPTION"]

    def close(self) -> None:
        for s in self._all:
            s.close()
