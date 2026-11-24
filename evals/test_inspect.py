"""Evaluation of the model-to-workspace inspection loop without a model."""
import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import aya


class InspectTest(unittest.TestCase):
    def test_explicit_filename_is_read_before_model_response(self):
        calls = []
        class FakeProcess:
            returncode = 0
            def __init__(self, args, **kwargs): calls.append(args[-1])
            def communicate(self): return json.dumps({"answer": "blue"}), ""
        with tempfile.TemporaryDirectory() as root:
            Path(root, "settings.txt").write_text("color=blue")
            old = os.getcwd()
            try:
                os.chdir(root)
                with patch.object(aya.subprocess, "Popen", FakeProcess), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(aya.inspect_workspace("Read settings.txt"), "blue")
                self.assertIn("color=blue", calls[0])
            finally:
                os.chdir(old)

    def test_tool_results_reach_model_and_answer(self):
        calls = []
        class FakeProcess:
            returncode = 0
            def __init__(self, args, **kwargs):
                calls.append(args[-1])
            def communicate(self):
                if len(calls) == 1:
                    return json.dumps({"tool": "read_file", "path": "config.txt"}), ""
                return json.dumps({"answer": "config.txt contains blue"}), ""
        with tempfile.TemporaryDirectory() as root:
            Path(root, "config.txt").write_text("color=blue\n")
            old = os.getcwd()
            try:
                os.chdir(root)
                with patch.object(aya.subprocess, "Popen", FakeProcess), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(aya.inspect_workspace("what color?"), "config.txt contains blue")
                self.assertIn("color=blue", calls[1])
            finally:
                os.chdir(old)

    def test_invalid_model_output_is_not_executed(self):
        class FakeProcess:
            returncode = 0
            def __init__(self, *args, **kwargs): pass
            def communicate(self): return "rm -rf /", ""
        with patch.object(aya.subprocess, "Popen", FakeProcess):
            with self.assertRaisesRegex(RuntimeError, "valid inspection action"):
                aya.inspect_workspace("inspect")


if __name__ == "__main__":
    unittest.main(verbosity=2)
