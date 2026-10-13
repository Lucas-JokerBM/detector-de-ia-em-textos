"""Requer: pip install -e .[api,dev]  (httpx para o TestClient)."""
import unittest

try:
    from fastapi.testclient import TestClient
    from detector_ia.api.app import create_app
    from detector_ia.config import Settings
except ImportError:  # dependências opcionais ausentes
    TestClient = None

from helpers import AI_TEXT, make_docx

DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


@unittest.skipIf(TestClient is None, "fastapi/httpx não instalados")
class ApiTests(unittest.TestCase):
    def client(self, **kw):
        return TestClient(create_app(Settings(**kw)))

    def post(self, c, content, name="a.docx", headers=None):
        return c.post("/api/v1/analyze", files={"file": (name, content, DOCX)}, headers=headers or {})

    def test_health(self):
        self.assertEqual(self.client().get("/api/v1/health").json()["status"], "ok")

    def test_analyze_ok(self):
        r = self.post(self.client(), make_docx(AI_TEXT))
        self.assertEqual(r.status_code, 200)
        self.assertIn("score", r.json())

    def test_requires_api_key_when_configured(self):
        c = self.client(api_keys=("segredo",))
        self.assertEqual(self.post(c, make_docx(AI_TEXT)).status_code, 401)
        self.assertEqual(self.post(c, make_docx(AI_TEXT), headers={"X-API-Key": "errada"}).status_code, 401)
        self.assertEqual(self.post(c, make_docx(AI_TEXT), headers={"X-API-Key": "segredo"}).status_code, 200)

    def test_rejects_wrong_extension_and_garbage(self):
        c = self.client()
        self.assertEqual(self.post(c, b"x", name="a.txt").status_code, 415)
        self.assertEqual(self.post(c, b"nao-e-docx").status_code, 422)

    def test_rejects_too_large(self):
        c = self.client(max_upload_bytes=200)
        self.assertEqual(self.post(c, make_docx(AI_TEXT)).status_code, 413)

    def test_rate_limit(self):
        c = self.client(rate_limit_per_minute=2)
        codes = [self.post(c, make_docx(AI_TEXT)).status_code for _ in range(3)]
        self.assertEqual(codes, [200, 200, 429])

    def test_security_headers_and_static_ui(self):
        r = self.client().get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("default-src 'self'", r.headers["content-security-policy"])


if __name__ == "__main__":
    unittest.main()
