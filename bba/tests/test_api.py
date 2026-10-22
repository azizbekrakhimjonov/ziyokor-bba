import json

from django.test import Client, TestCase, override_settings

from bba.models import BbaState
from bba.store import DEFAULT_SEED, PB


@override_settings(
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
)
class BbaApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        BbaState.objects.create(id=1, data=dict(DEFAULT_SEED))

    def _post(self, body: dict):
        return self.client.post(
            "/api/public/bba",
            data=json.dumps(body, ensure_ascii=False),
            content_type="application/json",
        )

    def test_options_cors(self):
        r = self.client.options("/api/public/bba")
        self.assertEqual(r.status_code, 204)
        self.assertEqual(r.headers.get("Access-Control-Allow-Origin"), "*")

    def test_admin_login(self):
        r = self._post({"a": "login", "u": "admin", "p": "admin123"})
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(data.get("admin"))
        self.assertIn("db", data)
        self.assertNotIn("adm", data["db"])

    def test_student_login_demo(self):
        r = self._post({"a": "login", "u": "demo", "p": "demo123"})
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("s", data)
        self.assertEqual(data["s"]["email"], "demo")

    def test_student_login_wrong_password(self):
        r = self._post({"a": "login", "u": "demo", "p": "wrong"})
        self.assertEqual(r.status_code, 401)

    def test_add_student_persists(self):
        r = self._post(
            {
                "a": "addst",
                "u": "admin",
                "p": "admin123",
                "name": "Ali Valiyev",
            }
        )
        self.assertEqual(r.status_code, 200)
        st = r.json()["st"]
        self.assertIn("@gmail.com", st["login"])
        row = BbaState.objects.get(pk=1)
        logins = [x["login"] for x in row.data["st"]]
        self.assertIn(st["login"], logins)

    def test_begin_and_answer_flow(self):
        login = self._post({"a": "login", "u": "demo", "p": "demo123"}).json()
        cred = {"u": "demo", "p": "demo123"}
        r = self._post({"a": "begin", **cred, "key": "test-key"})
        self.assertEqual(r.status_code, 200)
        prog = r.json()["prog"]
        self.assertIn("ans", prog)
        r2 = self._post({"a": "ans", **cred, "ans": {"0": 1}})
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(r2.json().get("ok"), 1)
        sid = next(s["sid"] for s in BbaState.objects.get(pk=1).data["st"] if s["login"] == "demo")
        pr = BbaState.objects.get(pk=PB + sid).data
        self.assertEqual(pr["ans"], {"0": 1})

    def test_platform_html(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        body = b"".join(r.streaming_content)
        self.assertIn(b"BBA", body)
