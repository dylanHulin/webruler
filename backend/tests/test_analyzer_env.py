"""Regression tests for the analyzer's .env / environment wiring.

Stdlib unittest only (no new dependencies).
Run from backend/:  python -m unittest discover -s tests

The .env-loading tests run in a subprocess against a copy of analyzer.py,
so they never touch the real backend/.env and never expose real secrets.
"""
import importlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRUBBED_VARS = ("MUSE_API_KEY", "MODEL_API_KEY", "MUSE_API_URL")


def run_analyzer_in_isolation(dotenv_content, snippet):
    """Copy analyzer.py to a clean temp dir with the given .env, run snippet there."""
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copy(os.path.join(BACKEND_DIR, "analyzer.py"), tmp)
        with open(os.path.join(tmp, ".env"), "w") as fh:
            fh.write(dotenv_content)
        env = {k: v for k, v in os.environ.items() if k not in SCRUBBED_VARS}
        proc = subprocess.run(
            [sys.executable, "-c", snippet],
            cwd=tmp, env=env, capture_output=True, text=True, timeout=120,
        )
    return proc


class AnalyzerEnvTest(unittest.TestCase):
    def setUp(self):
        self._saved_environ = dict(os.environ)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._saved_environ)
        import analyzer
        importlib.reload(analyzer)

    def test_loads_api_key_from_dotenv_file(self):
        proc = run_analyzer_in_isolation(
            "MUSE_API_KEY=fake-key-from-dotenv-file\n",
            "import analyzer, os; print(os.getenv('MUSE_API_KEY'))",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout.strip(), "fake-key-from-dotenv-file")

    def test_api_url_reads_from_environment(self):
        os.environ["MUSE_API_URL"] = "https://example.test/v1/responses"
        import analyzer
        analyzer = importlib.reload(analyzer)
        self.assertEqual(analyzer.META_API_URL, "https://example.test/v1/responses")

    def test_api_url_falls_back_to_default(self):
        proc = run_analyzer_in_isolation(
            "MUSE_API_KEY=fake-key-without-url\n",
            "import analyzer; print(analyzer.META_API_URL)",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout.strip(), "https://api.meta.ai/v1/responses")

    def test_analyze_sends_configured_key(self):
        os.environ["MUSE_API_KEY"] = "test-key-123"
        os.environ.pop("MODEL_API_KEY", None)
        import analyzer
        analyzer = importlib.reload(analyzer)
        captured = {}

        def fake_post(url, json=None, headers=None, timeout=None):
            captured["url"] = url
            captured["headers"] = headers
            captured["payload"] = json

            class Resp:
                status_code = 200

                def json(self):
                    return {"output": [{"content": [{"text": '{"violations": [], "summary": "ok"}'}]}]}

            return Resp()

        with mock.patch.object(analyzer.requests, "post", fake_post), \
                mock.patch.object(analyzer, "fetch_page_content", lambda url: "<html></html>"):
            result = analyzer.analyze_web_content(url="https://example.test")

        self.assertEqual(captured["headers"]["Authorization"], "Bearer test-key-123")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["violations_found"], 0)


if __name__ == "__main__":
    unittest.main()
