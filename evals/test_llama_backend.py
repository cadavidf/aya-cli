"""Exercise Aya's local-server protocol and all three model call sites."""
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


class MockServer:
    def __init__(self, answers):
        self.answers = iter(answers)
        self.requests = []

    def open(self, request, timeout):
        self.requests.append((request.full_url, json.loads(request.data), timeout))
        reply = {"choices": [{"message": {"content": next(self.answers)}}]}
        return io.BytesIO(json.dumps(reply).encode())


class LlamaBackendTest(unittest.TestCase):
    def test_command_chat_and_inspection_use_chat_protocol(self):
        server = MockServer(["echo hi", "Hello", json.dumps({"answer": "blue"})])
        with tempfile.TemporaryDirectory() as root:
            Path(root, "settings.txt").write_text("color=blue")
            old = os.getcwd()
            try:
                os.chdir(root)
                with patch.dict(os.environ, {"AYA_BACKEND": "llama", "AYA_LLAMA_URL": "http://127.0.0.1:9999"}), \
                     patch.object(aya.urllib.request, "build_opener", return_value=server), \
                     contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(aya.generate("say hi"), "echo hi")
                    history = []
                    self.assertEqual(aya.chat("Hi", history), "Hello")
                    self.assertEqual(aya.inspect_workspace("Read settings.txt"), "blue")
            finally:
                os.chdir(old)
        self.assertEqual(len(history), 2)
        self.assertEqual(len(server.requests), 3)
        for url, payload, timeout in server.requests:
            self.assertEqual(url, "http://127.0.0.1:9999/v1/chat/completions")
            self.assertEqual(timeout, 180)
        # generate() and inspect_workspace() send one user-role message each.
        self.assertEqual(server.requests[0][1]["messages"][0]["role"], "user")
        self.assertEqual(server.requests[2][1]["messages"][0]["role"], "user")
        # chat() sends a system message first, then real conversation turns.
        chat_messages = server.requests[1][1]["messages"]
        self.assertEqual(chat_messages[0]["role"], "system")
        self.assertEqual(chat_messages[-1], {"role": "user", "content": "Hi"})
        self.assertIn("color=blue", server.requests[2][1]["messages"][0]["content"])

    def test_nonlocal_server_is_rejected(self):
        with patch.dict(os.environ, {"AYA_BACKEND": "llama", "AYA_LLAMA_URL": "http://example.com"}):
            with self.assertRaisesRegex(RuntimeError, "local HTTP"):
                aya.model_generate("hello")

    def test_failed_request_is_reported(self):
        server = MockServer([])
        server.open = lambda *args, **kwargs: (_ for _ in ()).throw(OSError("connection refused"))
        with patch.dict(os.environ, {"AYA_BACKEND": "llama", "AYA_LLAMA_URL": "http://127.0.0.1:8080"}), \
             patch.object(aya.urllib.request, "build_opener", return_value=server):
            with self.assertRaisesRegex(RuntimeError, "connection refused"):
                aya.model_generate("hello")


if __name__ == "__main__":
    unittest.main()
