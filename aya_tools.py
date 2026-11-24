"""Bounded, read-only filesystem tools for an Aya workspace."""

from pathlib import Path
import os


class WorkspaceTools:
    """Read files under root. Symlinks are deliberately not followed."""

    MAX_READ_BYTES = 64 * 1024
    MAX_ENTRIES = 200
    MAX_SEARCH_FILES = 2000
    MAX_MATCHES = 50
    SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__"}

    def __init__(self, root):
        self.root = Path(root).resolve(strict=True)
        if not self.root.is_dir():
            raise ValueError("Workspace root must be a directory")

    def _path(self, path):
        if not isinstance(path, str) or not path or "\x00" in path:
            raise ValueError("Path must be a non-empty string")
        candidate = Path(path)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise ValueError("Path must be relative and inside the workspace")
        current = self.root
        for part in candidate.parts:
            current = current / part
            if current.is_symlink():
                raise ValueError("Symlinks are not supported")
        try:
            current.resolve(strict=False).relative_to(self.root)
        except ValueError:
            raise ValueError("Path must stay inside the workspace") from None
        return current

    def list_files(self, path="."):
        directory = self._path(path)
        if not directory.is_dir():
            raise ValueError("Path is not a directory")
        entries = sorted(directory.iterdir(), key=lambda p: p.name.casefold())
        result = []
        for entry in entries[:self.MAX_ENTRIES]:
            suffix = "@" if entry.is_symlink() else "/" if entry.is_dir() else ""
            result.append(entry.name + suffix)
        if len(entries) > self.MAX_ENTRIES:
            result.append("[Listing truncated]")
        return "\n".join(result) if result else "[Empty directory]"

    def read_file(self, path):
        file_path = self._path(path)
        if not file_path.is_file():
            raise ValueError("Path is not a regular file")
        with file_path.open("rb") as source:
            data = source.read(self.MAX_READ_BYTES + 1)
        if b"\x00" in data:
            raise ValueError("File appears to be binary")
        truncated = len(data) > self.MAX_READ_BYTES
        text = data[:self.MAX_READ_BYTES].decode("utf-8", errors="replace")
        lines = text.splitlines()
        result = "\n".join(f"{number}: {line}" for number, line in enumerate(lines, 1))
        return result + ("\n[File truncated]" if truncated else "")

    def search_files(self, query, path="."):
        if not isinstance(query, str) or not query or len(query) > 256 or "\n" in query:
            raise ValueError("Search query must be a non-empty single line of at most 256 characters")
        directory = self._path(path)
        if not directory.is_dir():
            raise ValueError("Path is not a directory")
        matches, scanned = [], 0
        truncated = False
        for base, dirs, files in os.walk(directory, followlinks=False):
            dirs[:] = sorted(d for d in dirs if d not in self.SKIP_DIRS and not (Path(base) / d).is_symlink())
            for name in sorted(files):
                file_path = Path(base) / name
                if file_path.is_symlink() or not file_path.is_file():
                    continue
                if scanned >= self.MAX_SEARCH_FILES:
                    truncated = True
                    break
                scanned += 1
                try:
                    with file_path.open("rb") as source:
                        data = source.read(self.MAX_READ_BYTES)
                    if b"\x00" in data:
                        continue
                    text = data.decode("utf-8", errors="replace")
                except OSError:
                    continue
                relative = file_path.relative_to(self.root)
                if query.casefold() in str(relative).casefold():
                    matches.append(f"{relative} [filename]")
                    if len(matches) >= self.MAX_MATCHES:
                        truncated = True
                        break
                for number, line in enumerate(text.splitlines(), 1):
                    if query.casefold() in line.casefold():
                        matches.append(f"{relative}:{number}: {line[:500]}")
                        if len(matches) >= self.MAX_MATCHES:
                            truncated = True
                            break
                if truncated:
                    break
            if truncated:
                break
        if truncated:
            matches.append("[Search truncated]")
        return "\n".join(matches) if matches else "[No matches]"
