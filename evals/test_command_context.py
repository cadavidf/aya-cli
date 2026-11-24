"""Verify command generation receives the installed tool's help."""
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import aya


class CommandContextTest(unittest.TestCase):
    def test_fabric_help_is_in_model_prompt(self):
        calls = []
        class FakeProcess:
            returncode = 0
            def __init__(self, args, **kwargs): calls.append(args)
            def communicate(self): return "fabric --listpatterns", ""
        result = subprocess.CompletedProcess([], 0, "--listpatterns List all patterns", "")
        with patch.object(aya.shutil, "which", side_effect=lambda name: "/usr/bin/fabric" if name == "fabric" else None), \
             patch.object(aya.subprocess, "run", return_value=result), \
             patch.object(aya.subprocess, "Popen", FakeProcess):
            self.assertEqual(aya.generate("Use fabric to list patterns"), "fabric --listpatterns")
        self.assertIn("--listpatterns List all patterns", calls[0][-1])


if __name__ == "__main__":
    unittest.main()
