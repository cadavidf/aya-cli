#!/usr/bin/env python3
"""Black-box regression checks for Aya; no model, network, or user files required."""
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest


AYA = Path(os.environ.get("AYA_SCRIPT", str(Path(__file__).resolve().parents[1] / "aya.py")))
STUB = '''#!/usr/bin/python3
import json, os, sys
with open(os.environ["AYA_EVAL_LOG"], "a", encoding="utf-8") as out:
    out.write(json.dumps(sys.argv[1:]) + "\\n")
prompt = sys.argv[-1]
if "EVAL_EXECUTION_REQUEST" in prompt:
    print("touch " + os.environ["AYA_EVAL_MARKER"])
elif "EVAL_SECOND_QUESTION" in prompt:
    print("EVAL_SECOND_ANSWER")
else:
    print("EVAL_FIRST_ANSWER")
'''


class AyaEvaluation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="aya-eval-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        fake = self.bin / "ollama"
        fake.write_text(STUB)
        fake.chmod(0o755)
        fake_yt = self.bin / "yt-dlp"
        fake_yt.write_text("#!/bin/sh\nexit 0\n")
        fake_yt.chmod(0o755)
        self.log = self.root / "model.jsonl"
        self.marker = self.root / "executed"
        self.chat_log = self.log  # same file; chat() logs its own argv-shaped entry below
        self.server = HTTPServer(("127.0.0.1", 0), self._make_handler())
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.addCleanup(self.server.shutdown)
        self.addCleanup(self.server.server_close)
        self.env = os.environ.copy()
        self.env.update(HOME=str(self.root), PATH=str(self.bin) + ":/usr/bin:/bin",
                        TERM="dumb", AYA_EVAL_LOG=str(self.log),
                        AYA_EVAL_MARKER=str(self.marker),
                        AYA_OLLAMA_URL="http://127.0.0.1:%d" % self.server.server_port)

    def _make_handler(self):
        chat_log = self.log

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                prompt = body["messages"][-1]["content"]
                seen = " ".join(m["content"] for m in body["messages"])  # whole conversation the model saw
                with open(chat_log, "a", encoding="utf-8") as out:
                    out.write(json.dumps(["chat", seen]) + "\n")
                answer = "EVAL_SECOND_ANSWER" if "EVAL_SECOND_QUESTION" in prompt else "EVAL_FIRST_ANSWER"
                reply = json.dumps({"message": {"content": answer}}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(reply)))
                self.end_headers()
                self.wfile.write(reply)

        return Handler

    def run_aya(self, inputs, timeout=12):
        return subprocess.run([sys.executable, str(AYA)], input=inputs,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              text=True, cwd=self.root, env=self.env, timeout=timeout)

    def calls(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()] if self.log.exists() else []

    def test_start_and_exit_without_fixed_delay(self):
        start = time.monotonic()
        result = self.run_aya("exit\n")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertLess(time.monotonic() - start, 2.5, "startup has a long fixed delay")

    def test_conversation_includes_prior_turn(self):
        result = self.run_aya("EVAL_FIRST_QUESTION\nEVAL_SECOND_QUESTION\nexit\n")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("EVAL_FIRST_ANSWER", result.stdout)
        self.assertIn("EVAL_SECOND_ANSWER", result.stdout)
        calls = self.calls()
        self.assertEqual(len(calls), 2, calls)
        self.assertIn("EVAL_FIRST_QUESTION", calls[1][-1])
        self.assertIn("EVAL_FIRST_ANSWER", calls[1][-1])
        self.assertIn("EVAL_SECOND_QUESTION", calls[1][-1])

    def test_clear_drops_previous_turn(self):
        result = self.run_aya("EVAL_FIRST_QUESTION\n/clear\nEVAL_SECOND_QUESTION\nexit\n")
        self.assertEqual(result.returncode, 0, result.stdout)
        calls = self.calls()
        self.assertEqual(len(calls), 2, calls)
        self.assertNotIn("EVAL_FIRST_QUESTION", calls[1][-1])
        self.assertNotIn("EVAL_FIRST_ANSWER", calls[1][-1])

    def test_command_requires_approval(self):
        result = self.run_aya("/command EVAL_EXECUTION_REQUEST\nn\nexit\n")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("Execute?", result.stdout)
        self.assertFalse(self.marker.exists(), "rejected command executed")

    def test_approved_command_runs(self):
        result = self.run_aya("/command EVAL_EXECUTION_REQUEST\ny\nexit\n")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertTrue(self.marker.exists(), "approved command did not execute")

    def test_youtube_cancel_preserves_router(self):
        result = self.run_aya("https://youtu.be/abcdefghijk\nq\nexit\n")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("YOUTUBE DETECTED", result.stdout.upper())
        self.assertFalse(self.calls(), "cancelled YouTube workflow called the model")


if __name__ == "__main__":
    unittest.main(verbosity=2)
